from .base_node import BaseNode


class ParentNode(BaseNode):
    """Base class for all parent nodes in the tree."""

    def __init__(self, obj_id):
        super().__init__(obj_id)
        self.children = []

    def add_child(self, child):
        """Add a child to the node."""
        self.children.append(child)
