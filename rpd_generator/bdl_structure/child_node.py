from .base_node import BaseNode


class ChildNode(BaseNode):
    """Base class for all child nodes in the tree."""

    def __init__(self, u_name, parent):
        super().__init__(u_name)
        self.parent = parent
        self.parent.add_child(self)

    def __repr__(self):
        return f"ChildNode('{self.u_name, self.parent}')"
