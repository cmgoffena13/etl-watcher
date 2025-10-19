TEST_ADDRESS_LINEAGE_POST_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "Source Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
    "target_addresses": [
        {
            "name": "Target Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
}

TEST_ADDRESS_LINEAGE_POST_OUTPUT_DATA = {
    "pipeline_id": 1,
    "lineage_relationships_created": 1,
    "message": "lineage relationships created for pipeline 1",
}


TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "Source Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
        {
            "name": "Source Address 2",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
    ],
    "target_addresses": [
        {
            "name": "Target Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
}

TEST_ADDRESS_LINEAGE_MULTIPLE_TARGETS_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "Source Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
    "target_addresses": [
        {
            "name": "Target Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
        {
            "name": "Target Address 2",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
    ],
}

TEST_ADDRESS_LINEAGE_MULTIPLE_SOURCES_AND_TARGETS_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "Source Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
        {
            "name": "Source Address 2",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
    ],
    "target_addresses": [
        {
            "name": "Target Address 1",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
        {
            "name": "Target Address 2",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        },
    ],
}

TEST_ADDRESS_LINEAGE_UPDATE_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "New Source Address",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
    "target_addresses": [
        {
            "name": "New Target Address",
            "address_type_name": "databricks",
            "address_type_group_name": "database",
        }
    ],
}

TEST_ADDRESS_LINEAGE_CHAIN_FIRST_LINK_DATA = {
    "pipeline_id": 1,
    "source_addresses": [
        {
            "name": "address1",
            "address_type_name": "table",
            "address_type_group_name": "database",
        }
    ],
    "target_addresses": [
        {
            "name": "address2",
            "address_type_name": "table",
            "address_type_group_name": "database",
        }
    ],
}

TEST_ADDRESS_LINEAGE_CHAIN_SECOND_LINK_DATA = {
    "pipeline_id": 2,
    "source_addresses": [
        {
            "name": "address2",
            "address_type_name": "table",
            "address_type_group_name": "database",
        }
    ],
    "target_addresses": [
        {
            "name": "address3",
            "address_type_name": "table",
            "address_type_group_name": "database",
        }
    ],
}
