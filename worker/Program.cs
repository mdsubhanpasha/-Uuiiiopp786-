using System;
using System.Text.Json;
using System.Threading;
using Npgsql;
using StackExchange.Redis;

namespace Worker
{
    public class Program
    {
        public static void Main(string[] args)
        {
            try
            {
                var redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "redis";
                var redisPort = Environment.GetEnvironmentVariable("REDIS_PORT") ?? "6379";
                var pgHost = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "db";
                var pgUser = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "postgres";
                var pgPass = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "postgres";
                var pgDb = Environment.GetEnvironmentVariable("POSTGRES_DB") ?? "postgres";

                var pgConnectionString = $"Host={pgHost};Username={pgUser};Password={pgPass};Database={pgDb}";
                var redisConnectionString = $"{redisHost}:{redisPort}";

                Console.WriteLine($"Connecting to Redis at {redisConnectionString}...");
                var redis = ConnectionMultiplexer.Connect(redisConnectionString);
                var db = redis.GetDatabase();

                Console.WriteLine($"Connecting to Postgres at {pgHost}...");
                NpgsqlConnection? pgConn = OpenPgConnection(pgConnectionString);

                InitDb(pgConn);

                Console.WriteLine("Worker started processing votes...");

                while (true)
                {
                    try
                    {
                        string? value = db.ListRightPop("votes");
                        if (value != null)
                        {
                            var voteData = JsonSerializer.Deserialize<VoteData>(value);
                            if (voteData != null && !string.IsNullOrEmpty(voteData.voter_id) && !string.IsNullOrEmpty(voteData.vote))
                            {
                                Console.WriteLine($"Processing vote for '{voteData.vote}' from '{voteData.voter_id}'");
                                UpdateVote(pgConn, voteData.voter_id, voteData.vote);
                            }
                        }
                        else
                        {
                            Thread.Sleep(100);
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error processing item: {ex.Message}");
                        pgConn = OpenPgConnection(pgConnectionString);
                        Thread.Sleep(1000);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Fatal error in worker: {ex.Message}");
                Environment.Exit(1);
            }
        }

        private static NpgsqlConnection OpenPgConnection(string connectionString)
        {
            while (true)
            {
                try
                {
                    var conn = new NpgsqlConnection(connectionString);
                    conn.Open();
                    return conn;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Postgres connection failed ({ex.Message}). Retrying in 2 seconds...");
                    Thread.Sleep(2000);
                }
            }
        }

        private static void InitDb(NpgsqlConnection conn)
        {
            using var cmd = new NpgsqlCommand(@"
                CREATE TABLE IF NOT EXISTS votes (
                    id VARCHAR(255) NOT NULL PRIMARY KEY,
                    vote VARCHAR(255) NOT NULL
                );
            ", conn);
            cmd.ExecuteNonQuery();
        }

        private static void UpdateVote(NpgsqlConnection conn, string voterId, string vote)
        {
            using var cmd = new NpgsqlCommand(@"
                INSERT INTO votes (id, vote)
                VALUES (@id, @vote)
                ON CONFLICT (id) DO UPDATE SET vote = @vote;
            ", conn);
            cmd.Parameters.AddWithValue("id", voterId);
            cmd.Parameters.AddWithValue("vote", vote);
            cmd.ExecuteNonQuery();
        }

        public class VoteData
        {
            public string? voter_id { get; set; }
            public string? vote { get; set; }
        }
    }
}
