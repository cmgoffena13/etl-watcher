TEST_PIPELINE_TYPE_POST_DATA = {
    "name": "audit",
    "timely_number": 10,
    "timely_datepart": "hour",
    "mute_timely_check": False,
}

TEST_PIPELINE_TYPE_PATCH_DATA = {"id": 1, "name": "audit_patched"}
TEST_PIPELINE_TYPE_PATCH_OUTPUT_DATA = {
    "id": 1,
    "name": "audit_patched",
    "timely_number": 10,
    "timely_datepart": "hour",
    "mute_timely_check": False,
}
