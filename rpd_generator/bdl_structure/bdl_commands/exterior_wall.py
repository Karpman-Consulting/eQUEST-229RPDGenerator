from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class ExteriorWall(ChildNode, ParentNode):
    """ExteriorWall object in the tree."""

    bdl_command = "EXTERIOR-WALL"

    CEILING_TILT_THRESHOLD = 60
    FLOOR_TILT_THRESHOLD = 120

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)

        self.exterior_wall_data_structure = {}

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
        return f"ExteriorWall(u_name='{self.u_name}', parent={self.parent})"

    def populate_data_elements(self):
        """Populate data elements for exterior wall object."""
        self.area = self.try_float(self.keyword_value_pairs.get("AREA"))
        if self.area is None:
            height = self.try_float(self.keyword_value_pairs.get("HEIGHT"))
            width = self.try_float(self.keyword_value_pairs.get("WIDTH"))
            if height is not None and width is not None:
                self.area = height * width
        if self.area is None and self.keyword_value_pairs.get("LOCATION") == "TOP":
            requests = self.get_output_requests()
            output_data = self.get_output_data(requests)
            self.area = output_data.get("Roof Area")

        self.tilt = self.try_float(self.keyword_value_pairs.get("TILT"))
        if self.tilt is not None and self.tilt < self.CEILING_TILT_THRESHOLD:
            self.classification = "CEILING"
        elif self.tilt is not None and self.tilt >= self.FLOOR_TILT_THRESHOLD:
            self.classification = "FLOOR"
        else:
            self.classification = "WALL"

        self.azimuth = self.try_float(self.keyword_value_pairs.get("AZIMUTH"))

        self.adjacent_to = "EXTERIOR"
        self.does_cast_shade = self.boolean_map.get(
            self.keyword_value_pairs.get("SHADING-SURFACE")
        )

    def get_output_requests(self):
        requests = {}
        if self.area is None and self.keyword_value_pairs.get("LOCATION") == "TOP":
            requests["Roof Area"] = (1104008, "", self.u_name)
        return requests

    def populate_data_group(self):
        """Populate schema structure for exterior wall object."""
        self.construction = self.rmd.bdl_obj_instances.get(
            self.keyword_value_pairs.get("CONSTRUCTION")
        ).construction_data_structure

        self.exterior_wall_data_structure = {
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
                self.exterior_wall_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert exterior wall object into the rpd data structure."""
        zone = rmd.space_map.get(self.parent.u_name)
        zone.surfaces.append(self.exterior_wall_data_structure)
