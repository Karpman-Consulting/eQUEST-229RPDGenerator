import os
import json


def extract_parent_element_data(schema, parent_key=None, refs=None):
    if refs is None:
        refs = {}

    if isinstance(schema, dict):
        for key, value in schema.items():

            if key == "$ref" and value.startswith(
                "ASHRAE229.schema.json#/definitions/"
            ):
                ref_key = value.split("/")[
                    -1
                ]  # Extract the Data Group name from the reference
                if not ref_key.endswith("Options"):  # Filter out Options
                    if ref_key not in refs:
                        refs[ref_key] = [parent_key]
                    else:
                        refs[ref_key].append(parent_key)

            else:
                # Recursively search for more '$ref' entries
                extract_parent_element_data(
                    value, parent_key=key if key != "items" else parent_key, refs=refs
                )
    elif isinstance(schema, list):
        for item in schema:
            extract_parent_element_data(item, parent_key=parent_key, refs=refs)

    return refs


if __name__ == "__main__":
    file_dir = os.path.dirname(__file__)
    json_schema_path = os.path.join(file_dir, "resources", "ASHRAE229.schema.json")
    output_path = os.path.join(file_dir, "resources", "item_parents.json")

    with open(json_schema_path) as f:
        data = json.load(f)

    data = extract_parent_element_data(data)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
