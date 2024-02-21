from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class InteriorWall(
    ChildNode, ParentNode
):  # Inherit ChildNode first so that the MRO does not try to call ParentNode.__init__ twice
    """InteriorWall object in the tree."""

    bdl_command = "INTERIOR-WALL"
    used_constructions = []

    int_wall_type_map = {
        "STANDARD": "INTERIOR",
        "AIR": "OMIT",  # Ignore air walls and omit the associated RCT Surface if INT-WALL-TYPE = AIR
        "ADIABATIC": "IDENTICAL",
        "INTERNAL": "OMIT",  # Ignore internal walls and omit the associated RCT Surface if INT-WALL-TYPE = INTERNAL
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)

        self.interior_wall_data_structure = {}
        self.omit = False

        # data elements with children
        self.subsurfaces = []
        self.construction = {}
        self.surface_optical_properties = {}

        # data elements with no children
        self.classification = None
        self.area = None
        self.tilt = None
        self.azimuth = None
        self.adjacent_to = None
        self.adjacent_zone = None
        self.does_cast_shade = None
        self.status_type = None

    def __repr__(self):
        return f"InteriorWall(u_name='{self.u_name}', parent='{self.parent}')"

    def populate_data_elements(self):
        """Populate data elements for interior wall object."""
        int_wall_type = self.int_wall_type_map.get(
            self.keyword_value_pairs.get("INT-WALL-TYPE")
        )
        if int_wall_type == "OMIT":
            self.omit = True
            return

        self.area = self.try_float(self.keyword_value_pairs.get("AREA"))
        if self.area is None:
            height = self.try_float(self.keyword_value_pairs.get("HEIGHT"))
            width = self.try_float(self.keyword_value_pairs.get("WIDTH"))
            if height is not None and width is not None:
                self.area = height * width

        self.tilt = self.try_float(self.keyword_value_pairs.get("TILT"))

        self.azimuth = self.try_float(self.keyword_value_pairs.get("AZIMUTH"))

        self.adjacent_to = int_wall_type
        if int_wall_type == "INTERIOR":
            self.adjacent_zone = self.keyword_value_pairs.get("NEXT-TO")

        self.does_cast_shade = self.boolean_map.get(
            self.keyword_value_pairs.get("SHADING-SURFACE")
        )

    def populate_data_group(self):
        """Populate schema structure for interior wall object."""
        self.interior_wall_data_structure = {
            "id": self.u_name,
            "subsurfaces": self.subsurfaces,
            "construction": self.construction,
            "surface_optical_properties": self.surface_optical_properties,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "area",
            "tilt",
            "azimuth",
            "adjacent_to",
            "adjacent_zone",
            "does_cast_shade",
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.interior_wall_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert interior wall object into the rpd data structure."""
        if self.omit:
            return
        zone = rmd.space_map.get(self.parent.u_name)
        zone.surfaces.append(self.interior_wall_data_structure)
