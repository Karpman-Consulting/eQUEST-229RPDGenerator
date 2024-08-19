import os
import json


def extract_units(schema_data):
    dimensioned_schema_data = {}
    # Iterate through the definitions
    for model_key, model_value in schema_data.get("definitions", {}).items():
        model_properties = model_value.get("properties", {})
        for prop_key, prop_value in model_properties.items():
            if "units" in prop_value:
                # Building the required output format
                if model_key not in dimensioned_schema_data:
                    dimensioned_schema_data[model_key] = {}
                dimensioned_schema_data[model_key][prop_key] = prop_value["units"]
    return dimensioned_schema_data


if __name__ == "__main__":
    file_dir = os.path.dirname(__file__)
    json_schema_path = os.path.join(file_dir, "resources", "ASHRAE229.schema.json")
    output_path = os.path.join(file_dir, "resources", "schema_units.json")

    with open(json_schema_path) as f:
        data = json.load(f)

    data = extract_units(data)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
