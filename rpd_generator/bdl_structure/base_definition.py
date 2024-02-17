class BaseDefinition:
    """
    Base class for BDL commands that are not nodes in the tree, but used to populate 229 schema data elements.
    """

    def __init__(self, u_name, rmd):
        self.rmd = rmd
        self.u_name = u_name
        self.keyword_value_pairs = {}

    def __repr__(self):
        return f"BaseDefinition('{self.u_name}')"

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        # TODO for repeated keywords create list and append values
        self.keyword_value_pairs = key_val_dict

    def populate_data_elements(self):
        """This method will be overridden by each child class"""
        return None
