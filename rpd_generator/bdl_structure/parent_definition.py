from .base_definition import BaseDefinition


class ParentDefinition(BaseDefinition):
    """
    Class for BDL commands that are parents to nodes in the tree but are not nodes in the tree themselves
    """

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.children = []

    def __repr__(self):
        return f"ParentDefinition('{self.u_name}')"

    def add_child(self, child):
        """Add a child to the definition."""
        self.children.append(child)
