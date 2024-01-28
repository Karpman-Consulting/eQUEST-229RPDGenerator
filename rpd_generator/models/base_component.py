class BaseComponent:
    """
    Base class for BDL commands that are not nodes in the tree, but used to populate 229 schema data elements.
    """

    def __init__(self):
        self.keyword_value_pairs = {}
        self.schema_structure = {}
