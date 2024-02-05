from .base_node import BaseNode


class ChildNode(BaseNode):
    """Base class for all child nodes in the tree."""

    def __init__(self, obj_id, parent):
        super().__init__(obj_id)
        self.parent = parent
        self.parent.add_child(self)

    def __repr__(self):
        return f"ChildNode('{self.obj_id, self.parent}')"
