import duckdb

conn = duckdb.connect("data/job_market.duckdb")

print("=== REMOTE FRIENDLINESS ===")
print(conn.execute(
    "SELECT tech_stack, ROUND(AVG(remote_pct), 1) as avg_remote_pct "
    "FROM job_market_history WHERE location != 'remote' "
    "GROUP BY tech_stack ORDER BY avg_remote_pct DESC"
).df().to_string(index=False))

print("\n=== PIPELINE RUNS ===")
print(conn.execute("SELECT * FROM pipeline_runs").df().to_string(index=False))

conn.close()
