class BaseDefinition:
    """
    Base class for BDL commands that are not nodes in the tree, but used to populate 229 schema data elements.
    """

    def __init__(self, u_name):
        self.u_name = u_name
        self.keyword_value_pairs = {}
        self.schema_structure = {}

    def __repr__(self):
        return f"BaseDefinition('{self.u_name}')"

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        # TODO for repeated keywords create list and append values
        self.keyword_value_pairs = key_val_dict

    def populate_schema_structure(self):
        """This method will be overridden by each child class"""
        return None
