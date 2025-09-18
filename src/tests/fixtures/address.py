TEST_ADDRESS_POST_DATA = {
    "name": "Test Address",
    "address_type_name": "databricks",
    "address_type_group_name": "database",
}
TEST_ADDRESS_PATCH_DATA = {"id": 1, "name": "Test Address Patched"}
TEST_ADDRESS_PATCH_OUTPUT_DATA = {
    "id": 1,
    "name": "test address patched",
    "address_type_id": 1,
}
TEST_ADDRESS_DATABASE_POST_DATA = {
    "name": "database.schema.table",
    "address_type_name": "databricks",
    "address_type_group_name": "database",
}
TEST_ADDRESS_DATABASE_GET_OUTPUT_DATA = {
    "id": 1,
    "name": "database.schema.table",
    "address_type_id": 1,
    "database_name": "database",
    "schema_name": "schema",
    "table_name": "table",
}
