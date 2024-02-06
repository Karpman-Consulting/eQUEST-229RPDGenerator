from .base_node import BaseNode


class ChildNode(BaseNode):
    """Base class for all child nodes in the tree."""

    def __init__(self, u_name, parent):
        super().__init__(u_name)
        self.parent = parent
