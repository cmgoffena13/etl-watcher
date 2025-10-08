import pendulum

# Use current timestamps for test data (needed for anomaly detection)
now = pendulum.now("UTC")
start_time = now.subtract(hours=1)
end_time = now

TEST_PIPELINE_EXECUTION_START_DATA = {
    "pipeline_id": 1,
    "start_date": start_time.isoformat(),
}

TEST_PIPELINE_EXECUTION_END_DATA = {
    "id": 1,
    "end_date": end_time.isoformat(),
    "inserts": 10,
    "updates": 12,
    "soft_deletes": 14,
    "total_rows": 36,
    "completed_successfully": True,
}
