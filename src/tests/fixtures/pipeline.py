TEST_PIPELINE_POST_DATA = {
    "name": "Test Pipeline 1",
    "pipeline_type_name": "extraction",
    "pipeline_type_group_name": "databricks",
    "next_watermark": 10,
}

TEST_PIPELINE_FRESHNESS_DATA = {
    "name": "Timeliness Test Pipeline",
    "pipeline_type_name": "audit",
    "pipeline_type_group_name": "databricks",
    "next_watermark": 10,
    "last_target_insert": "2024-01-01T10:00:00Z",
    "last_target_update": "2024-01-01T10:00:00Z",
    "last_target_soft_delete": "2024-01-01T10:00:00Z",
    "freshness_number": 1,
    "freshness_datepart": "hour",
    "mute_freshness_check": False,
}
TEST_PIPELINE_PATCH_DATA = {"id": 1, "name": "Pipeline_Patched"}
TEST_PIPELINE_PATCH_OUTPUT_DATA = {
    "id": 1,
    "name": "pipeline_patched",
    "pipeline_type_id": 1,
}
