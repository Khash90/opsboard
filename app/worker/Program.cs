using System;
using System.Data.Common;
using System.Threading;
using Newtonsoft.Json;
using Npgsql;
using StackExchange.Redis;

namespace Worker
{
    internal static class Program
    {
        private static readonly string RedisHost =
            Environment.GetEnvironmentVariable("REDIS_HOST") ?? "redis";

        private static readonly string PostgresHost =
            Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "db";

        private static readonly string PostgresUser =
            Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "postgres";

        private static readonly string PostgresPassword =
            Environment.GetEnvironmentVariable("POSTGRES_PASSWORD")
            ?? throw new InvalidOperationException(
                "POSTGRES_PASSWORD environment variable is required."
            );

        private static readonly string PostgresDatabase =
            Environment.GetEnvironmentVariable("POSTGRES_DB") ?? "postgres";

        private static void Main()
        {
            try
            {
                using var pgsql = OpenDatabaseConnection();

                EnsureVotesTable(pgsql);

                var redisConn = OpenRedisConnection(RedisHost);
                var redis = redisConn.GetDatabase();

                var definition = new
                {
                    vote = "",
                    voter_id = ""
                };

                while (true)
                {
                    // Prevent a tight polling loop while the queue is empty.
                    Thread.Sleep(100);

                    if (!redisConn.IsConnected)
                    {
                        Console.WriteLine("Reconnecting to Redis");

                        redisConn.Dispose();
                        redisConn = OpenRedisConnection(RedisHost);
                        redis = redisConn.GetDatabase();
                    }

                    string? json =
                        redis.ListLeftPopAsync("votes").Result;

                    if (json == null)
                    {
                        CheckDatabaseConnection(pgsql);
                        continue;
                    }

                    var vote =
                        JsonConvert.DeserializeAnonymousType(
                            json,
                            definition
                        );

                    if (vote == null)
                    {
                        Console.Error.WriteLine(
                            "Unable to deserialize vote."
                        );

                        continue;
                    }

                    Console.WriteLine(
                        $"Processing vote for '{vote.vote}' " +
                        $"by '{vote.voter_id}'"
                    );

                    if (
                        !pgsql.State.Equals(
                            System.Data.ConnectionState.Open
                        )
                    )
                    {
                        pgsql.Open();
                    }

                    InsertVote(
                        pgsql,
                        vote.voter_id,
                        vote.vote
                    );
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(
                    $"Worker stopped: {ex.Message}"
                );

                Environment.ExitCode = 1;
            }
        }

        private static NpgsqlConnection OpenDatabaseConnection()
        {
            while (true)
            {
                try
                {
                    var connection =
                        new NpgsqlConnection(
                            BuildPostgresConnectionString()
                        );

                    connection.Open();

                    Console.WriteLine(
                        $"Connected to PostgreSQL at {PostgresHost}"
                    );

                    return connection;
                }
                catch (DbException)
                {
                    Console.Error.WriteLine(
                        "Waiting for PostgreSQL"
                    );

                    Thread.Sleep(1000);
                }
            }
        }

        private static string BuildPostgresConnectionString()
        {
            return
                $"Host={PostgresHost};" +
                $"Username={PostgresUser};" +
                $"Password={PostgresPassword};" +
                $"Database={PostgresDatabase};" +
                "GSS Encryption Mode=Disable;";
        }

        private static void EnsureVotesTable(
            NpgsqlConnection connection
        )
        {
            const string sql = @"
                CREATE TABLE IF NOT EXISTS votes (
                    id BIGSERIAL PRIMARY KEY,
                    voter_id VARCHAR(255) NOT NULL,
                    vote VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            ";

            using var command =
                new NpgsqlCommand(sql, connection);

            command.ExecuteNonQuery();
        }

        private static void CheckDatabaseConnection(
            NpgsqlConnection connection
        )
        {
            using var command =
                new NpgsqlCommand(
                    "SELECT 1;",
                    connection
                );

            command.ExecuteScalar();
        }

        private static void InsertVote(
            NpgsqlConnection connection,
            string voterId,
            string vote
        )
        {
            const string sql = @"
                INSERT INTO votes (
                    voter_id,
                    vote
                )
                VALUES (
                    @voter_id,
                    @vote
                );
            ";

            using var command =
                new NpgsqlCommand(sql, connection);

            command.Parameters.AddWithValue(
                "voter_id",
                voterId
            );

            command.Parameters.AddWithValue(
                "vote",
                vote
            );

            command.ExecuteNonQuery();
        }

        private static ConnectionMultiplexer OpenRedisConnection(
            string hostname
        )
        {
            while (true)
            {
                try
                {
                    Console.WriteLine(
                        $"Connecting to Redis at {hostname}"
                    );

                    var connection =
                        ConnectionMultiplexer.Connect(hostname);

                    Console.WriteLine(
                        $"Connected to Redis at {hostname}"
                    );

                    return connection;
                }
                catch (RedisConnectionException)
                {
                    Console.Error.WriteLine(
                        "Waiting for Redis"
                    );

                    Thread.Sleep(1000);
                }
            }
        }
    }
}
