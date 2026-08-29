from flask import Flask, Response, g, make_response, redirect, render_template, request
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


option_a = os.getenv("OPTION_A", "Cats")
option_b = os.getenv("OPTION_B", "Dogs")

# Browser URL to open after a vote is submitted.
# This can be overridden later by Docker Compose or Kubernetes.
result_url = os.getenv(
    "RESULT_URL",
    "http://127.0.0.1:8082",
)

hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger("gunicorn.error")
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Prometheus application metrics
# ---------------------------------------------------------------------------

vote_page_views_total = Counter(
    "opsboard_vote_page_views_total",
    "Total number of GET requests to the OpsBoard voting page.",
)

votes_submitted_total = Counter(
    "opsboard_votes_submitted_total",
    "Total number of votes submitted through the OpsBoard voting service.",
    ["choice"],
)


def get_redis():
    if not hasattr(g, "redis"):
        g.redis = Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            socket_timeout=5,
        )

    return g.redis


def get_vote_label(vote):
    """
    Translate the form's internal vote values into human-readable labels
    for Prometheus.

    Redis continues receiving the original values ("a" or "b") so the
    existing application workflow remains unchanged.
    """
    if vote == "a":
        return option_a

    if vote == "b":
        return option_b

    return "Unknown"


@app.route("/healthz")
def healthz():
    """
    Lightweight health endpoint.

    Monitoring and Kubernetes health checks use this endpoint so they do not
    artificially increase the application page-view counter.
    """
    return {"status": "ok"}, 200


@app.route("/metrics")
def metrics():
    """
    Expose Prometheus metrics aggregated across all Gunicorn workers.
    """
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    return Response(
        generate_latest(registry),
        mimetype=CONTENT_TYPE_LATEST,
    )


@app.route("/", methods=["GET", "POST"])
def hello():
    voter_id = request.cookies.get("voter_id")

    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

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

        # Persist the original vote value to Redis first.
        # This preserves compatibility with the existing worker/result flow.
        redis.rpush("votes", data)

        # Prometheus gets the human-readable option name instead of "a"/"b".
        vote_label = get_vote_label(vote)
        votes_submitted_total.labels(choice=vote_label).inc()

        # Redirect the browser to the result service
        # after successfully queuing the vote.
        response = make_response(
            redirect(result_url)
        )

        response.set_cookie(
            "voter_id",
            voter_id,
        )

        return response

    # Count real voting-page views.
    # Health checks and Prometheus scrapes use separate endpoints.
    vote_page_views_total.inc()

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
