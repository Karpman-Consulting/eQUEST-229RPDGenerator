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
