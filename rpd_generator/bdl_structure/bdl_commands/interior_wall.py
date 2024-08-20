from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums


SurfaceClassificationOptions = SchemaEnums.schema_enums["SurfaceClassificationOptions"]
SurfaceAdjacencyOptions = SchemaEnums.schema_enums["SurfaceAdjacencyOptions"]
AdditionalSurfaceAdjacencyOptions2019ASHRAE901 = SchemaEnums.schema_enums[
    "AdditionalSurfaceAdjacencyOptions2019ASHRAE901"
]
StatusOptions = SchemaEnums.schema_enums["StatusOptions"]


class InteriorWall(
    ChildNode, ParentNode
):  # Inherit ChildNode first so that the MRO does not try to call ParentNode.__init__ twice
    """InteriorWall object in the tree."""

    bdl_command = "INTERIOR-WALL"

    CEILING_TILT_THRESHOLD = 60
    FLOOR_TILT_THRESHOLD = 120

    adjacency_map = {
        "STANDARD": SurfaceAdjacencyOptions.INTERIOR,
        "AIR": None,  # Omit the associated 229 Surface if INT-WALL-TYPE = AIR
        "ADIABATIC": SurfaceAdjacencyOptions.IDENTICAL,
        "INTERNAL": None,  # Omit the associated 229 Surface if INT-WALL-TYPE = INTERNAL
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

        # data elements for surface optical properties
        self.absorptance_thermal_exterior = None
        self.absorptance_solar_exterior = None
        self.absorptance_visible_exterior = None
        self.absorptance_thermal_interior = None
        self.absorptance_solar_interior = None
        self.absorptance_visible_interior = None

    def __repr__(self):
        return f"InteriorWall(u_name='{self.u_name}', parent='{self.parent}')"

    def populate_data_elements(self):
        """Populate data elements for interior wall object."""
        self.adjacent_to = self.adjacency_map.get(
            self.keyword_value_pairs.get("INT-WALL-TYPE")
        )
        if self.adjacent_to is None:
            self.omit = True
            return

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
            self.classification = SurfaceClassificationOptions.CEILING
        elif self.tilt is not None and self.tilt >= self.FLOOR_TILT_THRESHOLD:
            self.classification = SurfaceClassificationOptions.FLOOR
        else:
            self.classification = SurfaceClassificationOptions.WALL

        self.azimuth = self.try_float(self.keyword_value_pairs.get("AZIMUTH"))

        if self.adjacent_to == SurfaceAdjacencyOptions.INTERIOR:
            self.adjacent_zone = self.rmd.space_map[
                self.keyword_value_pairs.get("NEXT-TO")
            ].u_name

        self.does_cast_shade = self.boolean_map.get(
            self.keyword_value_pairs.get("SHADING-SURFACE")
        )

        self.absorptance_solar_interior = self.try_float(
            self.keyword_value_pairs.get("INSIDE-SOL-ABS")
        )

        reflectance_visible_interior = self.try_float(
            self.keyword_value_pairs.get("INSIDE-VIS-REFL")
        )
        if reflectance_visible_interior is not None:
            self.absorptance_visible_interior = 1 - reflectance_visible_interior

    def get_output_requests(self):
        requests = {}
        if self.area is None and self.keyword_value_pairs.get("LOCATION") == "TOP":
            requests["Roof Area"] = (1106006, "", self.u_name)
        return requests

    def populate_data_group(self):
        """Populate schema structure for interior wall object."""
        self.construction = self.rmd.bdl_obj_instances.get(
            self.keyword_value_pairs.get("CONSTRUCTION")
        ).construction_data_structure

        surface_optical_property_attributes = [
            "absorptance_thermal_exterior",
            "absorptance_solar_exterior",
            "absorptance_visible_exterior",
            "absorptance_thermal_interior",
            "absorptance_solar_interior",
            "absorptance_visible_interior",
        ]

        for attr in surface_optical_property_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.surface_optical_properties[attr] = value

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
