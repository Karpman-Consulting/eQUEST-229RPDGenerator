from rpd_generator.bdl_structure.base_node import BaseNode


class ChildNode(BaseNode):
    """Base class for all child nodes in the tree."""

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, rmd)
        self.parent = parent
        parent.add_child(self)
