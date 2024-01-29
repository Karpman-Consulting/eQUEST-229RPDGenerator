from .base_definition import BaseDefinition


class ParentDefinition(BaseDefinition):
    """
    Base class for BDL commands that are not nodes in the tree, but used to populate 229 schema data elements.
    """

    def __init__(self, u_name):
        super().__init__(u_name)
        self.children = []

    def __repr__(self):
        return f"ParentDefinition('{self.u_name}')"

    def add_child(self, child):
        """Add a child to the definition."""
        self.children.append(child)
