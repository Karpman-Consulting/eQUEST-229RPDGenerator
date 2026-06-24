class Ruleset:

    SCHEMA_FILENAME = "ASHRAE229.schema.json"

    def __init__(self, name, enum_filename=None, output_filename=None):
        self.name = name
        self.enum_schema_filename = enum_filename
        self.output_schema_filename = output_filename

    def __repr__(self):
        return f"Ruleset(name='{self.name}', enum_schema_filename='{self.enum_schema_filename}', output_schema_filename='{self.output_schema_filename}')"
