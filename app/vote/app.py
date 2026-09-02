from flask import (
    Flask,
    Response,
    g,
    make_response,
    redirect,
    render_template,
    request,
)
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    generate_latest,
    multiprocess,
)
from redis import Redis
import json
import logging
import os
import random
import socket
import threading
import time

import psycopg2


option_a = os.getenv("OPTION_A", "Cats")
option_b = os.getenv("OPTION_B", "Dogs")

# Browser URL to open after a vote is submitted.
result_url = os.getenv(
    "RESULT_URL",
    "http://127.0.0.1:8082",
)

# PostgreSQL is the durable source of truth for business totals.
postgres_host = os.getenv("POSTGRES_HOST", "db")
postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
postgres_user = os.getenv("POSTGRES_USER", "postgres")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_database = os.getenv("POSTGRES_DB", "postgres")

if not postgres_password:
    raise RuntimeError(
        "POSTGRES_PASSWORD environment variable is required."
    )

hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger("gunicorn.error")
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Prometheus operational metrics
# ---------------------------------------------------------------------------
#
# These counters intentionally describe activity in the current running
# application processes. They are useful for rates and trends, but they are
# NOT the source of truth for lifetime business totals.
# ---------------------------------------------------------------------------

vote_page_views_total = Counter(
    "opsboard_vote_page_views_total",
    "Total voting-page GET requests observed by the running vote service.",
)

votes_submitted_total = Counter(
    "opsboard_votes_submitted_total",
    "Votes submitted through the running OpsBoard vote service.",
    ["choice"],
)


# ---------------------------------------------------------------------------
# Durable business-metric cache
# ---------------------------------------------------------------------------
#
# Prometheus currently scrapes every 15 seconds. Avoid hitting PostgreSQL
# unnecessarily on every request by caching the durable aggregate values for
# a short period.
# ---------------------------------------------------------------------------

BUSINESS_METRICS_CACHE_TTL_SECONDS = 10

business_metrics_cache = {
    "timestamp": 0.0,
    "votes": {
        "a": 0,
        "b": 0,
    },
    "page_views": 0,
}

business_metrics_cache_lock = threading.Lock()


def get_redis():
    if not hasattr(g, "redis"):
        g.redis = Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            socket_timeout=5,
        )

    return g.redis


def get_postgres_connection():
    """
    Open a short-lived PostgreSQL connection.

    PostgreSQL is used only for durable business counters here. Vote
    persistence itself still follows the existing Redis -> Worker ->
    PostgreSQL architecture.
    """
    return psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        user=postgres_user,
        password=postgres_password,
        dbname=postgres_database,
        connect_timeout=5,
    )


def ensure_business_metrics_table(connection):
    """
    Create the small durable business-metrics table if it does not exist.

    This table currently stores lifetime voting-page views.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS business_metrics (
                metric_name TEXT PRIMARY KEY,
                value BIGINT NOT NULL DEFAULT 0,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )

    connection.commit()


def record_durable_page_view():
    """
    Atomically increment the persistent voting-page view counter.
    """
    connection = get_postgres_connection()

    try:
        ensure_business_metrics_table(connection)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO business_metrics (
                    metric_name,
                    value,
                    updated_at
                )
                VALUES (
                    'vote_page_views',
                    1,
                    NOW()
                )
                ON CONFLICT (metric_name)
                DO UPDATE SET
                    value = business_metrics.value + 1,
                    updated_at = NOW();
                """
            )

        connection.commit()

        # Force the next metrics request to refresh from PostgreSQL.
        with business_metrics_cache_lock:
            business_metrics_cache["timestamp"] = 0.0

    finally:
        connection.close()


def read_durable_business_metrics():
    """
    Read persistent vote totals and persistent page views from PostgreSQL.
    """
    connection = get_postgres_connection()

    try:
        ensure_business_metrics_table(connection)

        votes = {
            "a": 0,
            "b": 0,
        }

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    vote,
                    COUNT(*) AS count
                FROM votes
                GROUP BY vote;
                """
            )

            for vote, count in cursor.fetchall():
                if vote in votes:
                    votes[vote] = int(count)

            cursor.execute(
                """
                SELECT value
                FROM business_metrics
                WHERE metric_name = 'vote_page_views';
                """
            )

            page_view_row = cursor.fetchone()
            page_views = (
                int(page_view_row[0])
                if page_view_row
                else 0
            )

        return {
            "votes": votes,
            "page_views": page_views,
        }

    finally:
        connection.close()


def get_durable_business_metrics():
    """
    Return cached business totals, refreshing them from PostgreSQL when the
    short cache TTL has expired.
    """
    now = time.monotonic()

    with business_metrics_cache_lock:
        cache_age = (
            now
            - business_metrics_cache["timestamp"]
        )

        if (
            business_metrics_cache["timestamp"] > 0
            and cache_age < BUSINESS_METRICS_CACHE_TTL_SECONDS
        ):
            return {
                "votes": dict(
                    business_metrics_cache["votes"]
                ),
                "page_views": business_metrics_cache[
                    "page_views"
                ],
            }

    fresh_metrics = read_durable_business_metrics()

    with business_metrics_cache_lock:
        business_metrics_cache["timestamp"] = now
        business_metrics_cache["votes"] = dict(
            fresh_metrics["votes"]
        )
        business_metrics_cache["page_views"] = (
            fresh_metrics["page_views"]
        )

    return fresh_metrics


def get_vote_label(vote):
    """
    Translate internal vote values into human-readable labels.
    """
    if vote == "a":
        return option_a

    if vote == "b":
        return option_b

    return "Unknown"


def escape_prometheus_label(value):
    """
    Escape a controlled label value for Prometheus text exposition format.
    """
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )


def generate_durable_business_metrics():
    """
    Generate PostgreSQL-backed Prometheus metrics.

    These are gauges because PostgreSQL, not the Prometheus process, owns
    their authoritative values.
    """
    durable = get_durable_business_metrics()

    cats = durable["votes"]["a"]
    dogs = durable["votes"]["b"]
    total_votes = cats + dogs
    page_views = durable["page_views"]

    cats_label = escape_prometheus_label(option_a)
    dogs_label = escape_prometheus_label(option_b)

    lines = [
        "# HELP opsboard_votes_persisted Durable number of votes stored in PostgreSQL.",
        "# TYPE opsboard_votes_persisted gauge",
        (
            'opsboard_votes_persisted{choice="'
            + cats_label
            + '"} '
            + str(cats)
        ),
        (
            'opsboard_votes_persisted{choice="'
            + dogs_label
            + '"} '
            + str(dogs)
        ),
        "# HELP opsboard_votes_persisted_total Durable total votes stored in PostgreSQL.",
        "# TYPE opsboard_votes_persisted_total gauge",
        "opsboard_votes_persisted_total "
        + str(total_votes),
        "# HELP opsboard_vote_page_views_persisted Durable voting-page views stored in PostgreSQL.",
        "# TYPE opsboard_vote_page_views_persisted gauge",
        "opsboard_vote_page_views_persisted "
        + str(page_views),
        "",
    ]

    return "\n".join(lines).encode("utf-8")


@app.route("/healthz")
def healthz():
    """
    Lightweight application health endpoint.

    Kubernetes probes intentionally use this instead of the voting page so
    health checks do not inflate business page-view metrics.
    """
    return {"status": "ok"}, 200


@app.route("/metrics")
def metrics():
    """
    Expose both operational process metrics and durable business metrics.
    """
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    process_metrics = generate_latest(registry)

    try:
        durable_metrics = generate_durable_business_metrics()
    except Exception:
        app.logger.exception(
            "Unable to read durable business metrics from PostgreSQL."
        )
        durable_metrics = b""

    return Response(
        process_metrics + durable_metrics,
        mimetype=CONTENT_TYPE_LATEST,
    )


@app.route("/", methods=["GET", "POST"])
def hello():
    voter_id = request.cookies.get("voter_id")

    if not voter_id:
        voter_id = hex(
            random.getrandbits(64)
        )[2:-1]

    if request.method == "POST":
        redis = get_redis()
        vote = request.form["vote"]

        app.logger.info(
            "Received vote for %s",
            vote,
        )

        data = json.dumps(
            {
                "voter_id": voter_id,
                "vote": vote,
            }
        )

        # Preserve the existing architecture:
        # Vote -> Redis -> Worker -> PostgreSQL.
        redis.rpush(
            "votes",
            data,
        )

        # Operational Prometheus counter.
        votes_submitted_total.labels(
            choice=get_vote_label(vote)
        ).inc()

        response = make_response(
            redirect(result_url)
        )

        response.set_cookie(
            "voter_id",
            voter_id,
        )

        return response

    # Operational counter for the currently running vote process.
    vote_page_views_total.inc()

    # Persistent all-time page-view counter.
    try:
        record_durable_page_view()
    except Exception:
        app.logger.exception(
            "Unable to persist voting-page view."
        )

    response = make_response(
        render_template(
            "index.html",
            option_a=option_a,
            option_b=option_b,
            hostname=hostname,
            vote=None,
        )
    )

    response.set_cookie(
        "voter_id",
        voter_id,
    )

    return response


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=80,
        debug=True,
        threaded=True,
    )
