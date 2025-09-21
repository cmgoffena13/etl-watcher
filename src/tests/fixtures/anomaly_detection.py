TEST_ANOMALY_DETECTION_RULE_PATCH_DATA = {
    "id": 1,
    "pipeline_id": 1,
    "metric_field": "updates",
}
TEST_ANOMALY_DETECTION_RULE_PATCH_OUTPUT_DATA = {
    "id": 1,
    "pipeline_id": 1,
    "metric_field": "updates",
}
TEST_ANOMALY_DETECTION_RULE_DURATION_SECONDS_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "duration_seconds",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}

TEST_ANOMALY_DETECTION_RULE_INSERTS_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "inserts",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}

TEST_ANOMALY_DETECTION_RULE_UPDATES_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "updates",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}

TEST_ANOMALY_DETECTION_RULE_SOFT_DELETES_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "soft_deletes",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}

TEST_ANOMALY_DETECTION_RULE_TOTAL_ROWS_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "total_rows",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}

TEST_ANOMALY_DETECTION_RULE_THROUGHPUT_POST_DATA = {
    "pipeline_id": 1,
    "metric_field": "throughput",
    "std_deviation_threshold_multiplier": 1.0,
    "lookback_days": 10,
    "minimum_executions": 5,
    "active": True,
}
