import json


class BaseNode:
    """
    Base class for all nodes in the tree.
    'Node' refers to rpd_generator objects that map directly to a 229 schema data group.
    """

    def __init__(self, u_name):
        self.keyword_value_pairs = {}
        self.schema_structure = {}
        self.obj_id = u_name

    def __repr__(self):
        return f"BaseNode('{self.obj_id}')"

    def get_object_json(self):
        """Return the object json of the node."""
        return json.dumps(self.schema_structure)

    def populate_schema_structure(self):
        """This method will be overridden by each child class"""
        return None

    def add_input(self, keyword, value):
        """Insert a keyword-value pair for the BDL command."""
        self.keyword_value_pairs[keyword] = value
