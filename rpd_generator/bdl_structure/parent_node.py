from rpd_generator.bdl_structure.base_node import BaseNode


class ParentNode(BaseNode):
    """Base class for all parent nodes in the tree."""

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.children = []

    def __repr__(self):
        return f"ParentNode('{self.u_name}')"

    def add_child(self, child):
        """Add a child to the node."""
        self.children.append(child)
