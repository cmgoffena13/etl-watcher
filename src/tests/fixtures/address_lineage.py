TEST_ADDRESS_LINEAGE_POST_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {"address_name": "Source Address 1", "address_type_name": "database"}
    ],
    "target_addresses": [
        {"address_name": "Target Address 1", "address_type_name": "database"}
    ],
}

TEST_ADDRESS_LINEAGE_POST_OUTPUT_DATA = {
    "pipeline_id": 1,
    "lineage_relationships_created": 1,
}

TEST_ADDRESS_LINEAGE_GET_OUTPUT_DATA = [
    {
        "id": 1,
        "pipeline_id": 1,
        "source_address_id": 1,
        "target_address_id": 2,
    }
]

TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {"address_name": "Source Address 1", "address_type_name": "database"},
        {"address_name": "Source Address 2", "address_type_name": "database"},
    ],
    "target_addresses": [
        {"address_name": "Target Address 1", "address_type_name": "database"}
    ],
}

TEST_ADDRESS_LINEAGE_MULTIPLE_TARGETS_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {"address_name": "Source Address 1", "address_type_name": "database"}
    ],
    "target_addresses": [
        {"address_name": "Target Address 1", "address_type_name": "database"},
        {"address_name": "Target Address 2", "address_type_name": "database"},
    ],
}
