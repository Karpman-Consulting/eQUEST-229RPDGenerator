

class BaseNode:
    """
    Base class for all nodes in the tree.
    'Node' refers to rpd_generator objects that map directly to a 229 schema data group.
    """

    def __init__(self, u_name, rmd):
        self.rmd = rmd
        self.u_name = u_name
        self.reporting_name = None
        self.notes = None
        self.keyword_value_pairs = {}
        self.schema_structure = {}

    def __repr__(self):
        return f"BaseNode('{self.u_name}')"

    def add_inputs(self, key_val_dict):
        """Insert a keyword-value pair for the BDL command."""
        self.keyword_value_pairs = key_val_dict

    def populate_data_group(self):
        """This method will be overridden by each child class"""
        return None

    def populate_data_elements(self):
        """This method will be overridden by each child class"""
        return None

    def insert_to_rpd(self, container):
        """This method will be overridden by each child class"""
        return None

    def get_obj(self, u_name):
        """
        Return the object instance by its u_name.
        :param u_name: str
        """
        return self.rmd.bdl_obj_instances.get(u_name, None)
