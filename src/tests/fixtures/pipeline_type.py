TEST_PIPELINE_TYPE_POST_DATA = {
    "name": "audit",
    "freshness_number": 10,
    "freshness_datepart": "hour",
    "mute_freshness_check": False,
}

TEST_PIPELINE_TYPE_PATCH_DATA = {"id": 1, "name": "audit_patched"}
TEST_PIPELINE_TYPE_PATCH_OUTPUT_DATA = {
    "id": 1,
    "name": "audit_patched",
    "freshness_number": 10,
    "freshness_datepart": "hour",
    "mute_freshness_check": False,
}
