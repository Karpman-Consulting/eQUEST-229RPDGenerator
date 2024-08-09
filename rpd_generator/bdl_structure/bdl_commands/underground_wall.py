from rpd_generator.bdl_structure.child_node import ChildNode


class BelowGradeWall(ChildNode):
    """BelowGradeWall object in the tree."""

    bdl_command = "UNDERGROUND-WALL"
    CEILING_TILT_THRESHOLD = 60
    FLOOR_TILT_THRESHOLD = 120

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

        self.area = self.try_float(self.keyword_value_pairs.get("AREA"))
        if self.area is None:
            height = self.try_float(self.keyword_value_pairs.get("HEIGHT"))
            width = self.try_float(self.keyword_value_pairs.get("WIDTH"))
            if height is not None and width is not None:
                self.area = height * width

        self.tilt = self.try_float(self.keyword_value_pairs.get("TILT"))
        if self.tilt is not None and self.tilt < self.CEILING_TILT_THRESHOLD:
            self.classification = "CEILING"
        elif self.tilt is not None and self.tilt >= self.FLOOR_TILT_THRESHOLD:
            self.classification = "FLOOR"
        else:
            self.classification = "WALL"

        self.azimuth = self.try_float(self.keyword_value_pairs.get("AZIMUTH"))

        self.adjacent_to = "GROUND"

        self.does_cast_shade = self.boolean_map.get(
            self.keyword_value_pairs.get("SHADING-SURFACE")
        )

    def populate_data_group(self):
        """Populate schema structure for below grade wall object."""
        self.construction = self.rmd.bdl_obj_instances.get(
            self.keyword_value_pairs.get("CONSTRUCTION")
        ).construction_data_structure

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
