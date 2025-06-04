import copy

from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


SurfaceClassificationOptions = SchemaEnums.schema_enums["SurfaceClassificationOptions"]
SurfaceAdjacencyOptions = SchemaEnums.schema_enums["SurfaceAdjacencyOptions"]
AdditionalSurfaceAdjacencyOptions2019ASHRAE901 = SchemaEnums.schema_enums[
    "AdditionalSurfaceAdjacencyOptions2019ASHRAE901"
]
StatusOptions = SchemaEnums.schema_enums["StatusOptions"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_InteriorWallKeywords = BDLEnums.bdl_enums["InteriorWallKeywords"]
BDL_ConstructionKeywords = BDLEnums.bdl_enums["ConstructionKeywords"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]
BDL_FloorKeywords = BDLEnums.bdl_enums["FloorKeywords"]
BDL_ConstructionTypes = BDLEnums.bdl_enums["ConstructionTypes"]
BDL_LayerKeywords = BDLEnums.bdl_enums["LayerKeywords"]
BDL_InteriorWallTypes = BDLEnums.bdl_enums["InteriorWallTypes"]
BDL_WallLocationOptions = BDLEnums.bdl_enums["WallLocationOptions"]


class InteriorWall(
    ChildNode, ParentNode
):  # Inherit ChildNode first so that the MRO does not try to call ParentNode.__init__ twice
    """InteriorWall object in the tree."""

    bdl_command = BDL_Commands.INTERIOR_WALL

    CEILING_TILT_THRESHOLD = 60
    FLOOR_TILT_THRESHOLD = 120

    adjacency_map = {
        BDL_InteriorWallTypes.STANDARD: SurfaceAdjacencyOptions.INTERIOR,
        BDL_InteriorWallTypes.AIR: SurfaceAdjacencyOptions.INTERIOR,
        BDL_InteriorWallTypes.ADIABATIC: SurfaceAdjacencyOptions.IDENTICAL,
        BDL_InteriorWallTypes.INTERNAL: SurfaceAdjacencyOptions.INTERIOR,
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        self.rmd.int_wall_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.interior_wall_data_structure = {}

        # data elements with children
        self.subsurfaces = []
        self.construction = {}
        self.optical_properties = {}

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
        self.optical_property_id = self.u_name + " OpticalProps"
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
            self.get_inp(BDL_InteriorWallKeywords.INT_WALL_TYPE)
        )

        self.area = self.determine_surface_area()

        self.tilt = self.try_float(self.get_inp(BDL_InteriorWallKeywords.TILT))

        self.classification = self.determine_surface_classification()

        parent_floor_azimuth = self.try_float(
            self.parent.parent.get_inp(BDL_FloorKeywords.AZIMUTH)
        )
        parent_space_azimuth = self.try_float(
            self.parent.get_inp(BDL_SpaceKeywords.AZIMUTH)
        )
        surface_azimuth = self.try_float(self.get_inp(BDL_InteriorWallKeywords.AZIMUTH))
        if (
            self.rmd.building_azimuth is not None
            and parent_floor_azimuth is not None
            and parent_space_azimuth is not None
            and surface_azimuth is not None
        ):
            self.azimuth = (
                self.rmd.building_azimuth
                + parent_floor_azimuth
                + parent_space_azimuth
                + surface_azimuth
            ) % 360
            if self.azimuth < 0:
                self.azimuth += 360

        if self.adjacent_to == SurfaceAdjacencyOptions.INTERIOR:
            adjacent_zone = self.rmd.space_map.get(
                self.get_inp(BDL_InteriorWallKeywords.NEXT_TO)
            )
            if adjacent_zone is not None:
                self.adjacent_zone = adjacent_zone.u_name

        self.does_cast_shade = self.boolean_map.get(
            self.get_inp(BDL_InteriorWallKeywords.SHADING_SURFACE)
        )

        self.absorptance_solar_interior = self.try_float(
            self.try_access_index(
                self.get_inp(BDL_InteriorWallKeywords.INSIDE_SOL_ABS), 0
            )
        )
        self.absorptance_solar_exterior = self.try_float(
            self.try_access_index(
                self.get_inp(BDL_InteriorWallKeywords.INSIDE_SOL_ABS), 1
            )
        )

        reflectance_visible_interior = self.try_float(
            self.try_access_index(
                self.get_inp(BDL_InteriorWallKeywords.INSIDE_VIS_REFL), 0
            )
        )
        if reflectance_visible_interior is not None:
            self.absorptance_visible_interior = 1 - reflectance_visible_interior
        reflectance_visible_exterior = self.try_float(
            self.try_access_index(
                self.get_inp(BDL_InteriorWallKeywords.INSIDE_VIS_REFL), 1
            )
        )
        if reflectance_visible_exterior is not None:
            self.absorptance_visible_exterior = 1 - reflectance_visible_exterior

    # def get_output_requests(self):
    #     requests = {}
    #     if (
    #         self.area is None
    #         and self.get_inp(BDL_InteriorWallKeywords.LOCATION)
    #         == BDL_WallLocationOptions.TOP
    #     ):
    #         requests["Roof Area"] = (1106006, "", self.u_name)
    #     return requests

    def populate_data_group(self):
        """Populate schema structure for interior wall object."""
        self.construction = copy.deepcopy(
            self.get_obj(
                self.get_inp(BDL_InteriorWallKeywords.CONSTRUCTION)
            ).construction_data_structure
        )

        optical_property_attributes = [
            "optical_property_id",
            "absorptance_thermal_exterior",
            "absorptance_solar_exterior",
            "absorptance_visible_exterior",
            "absorptance_thermal_interior",
            "absorptance_solar_interior",
            "absorptance_visible_interior",
        ]

        for attr in optical_property_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                attr = attr.replace("optical_property_", "")
                self.optical_properties[attr] = value

        self.interior_wall_data_structure = {
            "id": self.u_name,
            "subsurfaces": self.subsurfaces,
            "construction": self.construction,
            "optical_properties": self.optical_properties,
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

    def insert_to_rpd(self):
        """Insert interior wall object into the rpd data structure."""
        zone = self.rmd.space_map.get(self.parent.u_name)
        zone.surfaces.append(self.interior_wall_data_structure)

    def determine_surface_area(self):
        area = self.try_float(self.get_inp(BDL_InteriorWallKeywords.AREA))
        if area is None:
            height = self.try_float(self.get_inp(BDL_InteriorWallKeywords.HEIGHT))
            width = self.try_float(self.get_inp(BDL_InteriorWallKeywords.WIDTH))
            if height is not None and width is not None:
                area = height * width
        if area is None:
            polygon = self.get_obj(self.get_inp(BDL_InteriorWallKeywords.POLYGON))
            if polygon:
                polygon.calculate_area_of_polygon_coords()
                area = polygon.area
        return area

    def determine_surface_classification(self):
        """
        Determine the classification of the surface based on the tilt angle.
        """
        if self.tilt is not None and self.tilt < self.CEILING_TILT_THRESHOLD:
            return SurfaceClassificationOptions.CEILING
        elif self.tilt is not None and self.tilt >= self.FLOOR_TILT_THRESHOLD:
            return SurfaceClassificationOptions.FLOOR
        else:
            return SurfaceClassificationOptions.WALL
