from rpd_generator.schema.get_item_parents import extract_parent_element_data
from rpd_generator.schema.get_schema_units import extract_units


def test_extract_units_collects_properties_with_units_by_definition():
    schema = {
        "definitions": {
            "Space": {
                "properties": {
                    "floor_area": {"type": "number", "units": "area"},
                    "id": {"type": "string"},
                }
            },
            "Zone": {
                "properties": {
                    "volume": {"type": "number", "units": "volume"},
                }
            },
            "NoUnits": {"properties": {"id": {"type": "string"}}},
        }
    }

    assert extract_units(schema) == {
        "Space": {"floor_area": "area"},
        "Zone": {"volume": "volume"},
    }


def test_extract_parent_element_data_collects_refs_and_ignores_options():
    schema = {
        "definitions": {
            "BuildingSegment": {
                "properties": {
                    "zones": {
                        "type": "array",
                        "items": {"$ref": "ASHRAE229.schema.json#/definitions/Zone"},
                    },
                    "surface_type": {
                        "$ref": "ASHRAE229.schema.json#/definitions/SurfaceOptions"
                    },
                    "spaces": {
                        "oneOf": [{"$ref": "ASHRAE229.schema.json#/definitions/Space"}]
                    },
                }
            }
        }
    }

    assert extract_parent_element_data(schema) == {
        "Zone": ["zones"],
        "Space": ["spaces"],
    }
