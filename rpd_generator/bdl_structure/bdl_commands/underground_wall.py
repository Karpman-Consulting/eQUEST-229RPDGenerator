from rpd_generator.bdl_structure.child_node import ChildNode


class BelowGradeWall(ChildNode):
    """BelowGradeWall object in the tree."""

    bdl_command = "UNDERGROUND-WALL"
    used_constructions = []

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)

        self.underground_wall_data_structure = {}

        # data elements with children
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
        return f"BelowGradeWall(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for below grade wall object."""
        is_shading_map = {
            "YES": True,
            "NO": False,
        }

        self.area = self.keyword_value_pairs.get("AREA")
        if (
            self.area is None
            and self.keyword_value_pairs.get("HEIGHT") is not None
            and self.keyword_value_pairs.get("WIDTH") is not None
        ):
            self.area = float(self.keyword_value_pairs.get("HEIGHT", 0)) * float(
                self.keyword_value_pairs.get("WIDTH", 0)
            )
        if self.area is not None:
            self.area = float(self.area)

        self.tilt = self.keyword_value_pairs.get("TILT")
        if self.tilt is not None:
            self.tilt = float(self.tilt)

        self.azimuth = self.keyword_value_pairs.get("AZIMUTH")
        if self.azimuth is not None:
            self.azimuth = float(self.azimuth)

        self.adjacent_to = "GROUND"

        self.does_cast_shade = is_shading_map.get(
            self.keyword_value_pairs.get("SHADING-SURFACE")
        )

    def populate_data_group(self):
        """Populate schema structure for below grade wall object."""
        self.underground_wall_data_structure = {
            "id": self.u_name,
            "construction": self.construction,
            "surface_optical_properties": self.surface_optical_properties,
        }
        self.populate_data_elements()

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
                self.underground_wall_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert below grade wall object into the rpd data structure."""
        zone = rmd.space_map.get(self.parent.u_name)
        zone.surfaces.append(self.underground_wall_data_structure)
