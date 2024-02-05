import json


class BaseNode:
    """
    Base class for all nodes in the tree.
    'Node' refers to rpd_generator objects that map directly to a 229 schema data group.
    """

    def __init__(self, u_name):
        self.u_name = u_name
        self.reporting_name = None
        self.notes = None
        self.keyword_value_pairs = {}
        self.schema_structure = {}

    def __repr__(self):
        return f"BaseNode('{self.u_name}')"

    def populate_data_group(self):
        """This method will be overridden by each child class"""
        return None

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        # TODO for repeated keywords create list and append values
        self.keyword_value_pairs = key_val_dict
