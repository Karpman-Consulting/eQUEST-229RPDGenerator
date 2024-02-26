class BaseDefinition:
    """
    Base class for BDL commands that are not nodes in the tree, but used to populate 229 schema data elements.
    """

    boolean_map = {
        "YES": True,
        "NO": False,
    }

    def __init__(self, u_name, rmd):
        self.rmd = rmd
        self.u_name = u_name
        self.keyword_value_pairs = {}

    def __repr__(self):
        return f"BaseDefinition('{self.u_name}')"

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        self.keyword_value_pairs = key_val_dict

    def populate_data_elements(self):
        """This method will be overridden by each child class"""
        return None

    @staticmethod
    def try_float(value):
        """Attempt to convert a value to a float, returning None if it fails."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            # TODO log error for future GUI error window
            return None
