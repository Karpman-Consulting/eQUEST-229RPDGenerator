from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


SurfaceClassificationOptions = SchemaEnums.schema_enums["SurfaceClassificationOptions"]
SurfaceAdjacencyOptions = SchemaEnums.schema_enums["SurfaceAdjacencyOptions"]
StatusOptions = SchemaEnums.schema_enums["StatusOptions"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_UndergroundWallKeywords = BDLEnums.bdl_enums["UndergroundWallKeywords"]
BDL_ConstructionKeywords = BDLEnums.bdl_enums["ConstructionKeywords"]
BDL_LayerKeywords = BDLEnums.bdl_enums["LayerKeywords"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]
BDL_FloorKeywords = BDLEnums.bdl_enums["FloorKeywords"]
BDL_WallLocationOptions = BDLEnums.bdl_enums["WallLocationOptions"]
BDL_ConstructionTypes = BDLEnums.bdl_enums["ConstructionTypes"]


class BelowGradeWall(ChildNode):
    """BelowGradeWall object in the tree."""

    bdl_command = BDL_Commands.UNDERGROUND_WALL

    CEILING_TILT_THRESHOLD = 60
    FLOOR_TILT_THRESHOLD = 120

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        self.rmd.undg_wall_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.underground_wall_data_structure = {}

        # data elements with children
        self.optical_properties = {}

        # data elements with no children
        self.classification = None
        self.construction = None
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
        return f"BelowGradeWall(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for below grade wall object."""

        self.area = self.determine_surface_area()

        self.tilt = self.try_float(self.get_inp(BDL_UndergroundWallKeywords.TILT))

        self.classification = self.determine_surface_classification()

        self.construction = self.get_inp(BDL_UndergroundWallKeywords.CONSTRUCTION)

        parent_floor_azimuth = self.parent.parent.try_float(
            self.parent.parent.get_inp(BDL_FloorKeywords.AZIMUTH)
        )
        parent_space_azimuth = self.parent.try_float(
            self.parent.get_inp(BDL_SpaceKeywords.AZIMUTH)
        )
        surface_azimuth = self.try_float(
            self.get_inp(BDL_UndergroundWallKeywords.AZIMUTH)
        )
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

        self.adjacent_to = SurfaceAdjacencyOptions.GROUND

        self.does_cast_shade = self.boolean_map.get(
            self.get_inp(BDL_UndergroundWallKeywords.SHADING_SURFACE)
        )

        self.absorptance_solar_interior = self.try_float(
            self.get_inp(BDL_UndergroundWallKeywords.INSIDE_SOL_ABS)
        )

        reflectance_visible_interior = self.try_float(
            self.get_inp(BDL_UndergroundWallKeywords.INSIDE_VIS_REFL)
        )
        if reflectance_visible_interior is not None:
            self.absorptance_visible_interior = 1 - reflectance_visible_interior

        if self.classification == SurfaceClassificationOptions.WALL:
            self.populate_c_factor()

        if self.classification == SurfaceClassificationOptions.FLOOR:
            self.populate_f_factor()

    def populate_data_group(self):
        """Populate schema structure for below grade wall object."""

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

        self.underground_wall_data_structure = {
            "id": self.u_name,
            "optical_properties": self.optical_properties,
        }
        self.populate_data_elements()

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "construction",
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

    def insert_to_rpd(self):
        """Insert below grade wall object into the rpd data structure."""
        zone = self.rmd.space_map.get(self.parent.u_name)
        zone.surfaces.append(self.underground_wall_data_structure)

    def determine_surface_area(self):
        area = self.try_float(self.get_inp(BDL_UndergroundWallKeywords.AREA))
        if area is None:
            height = self.try_float(self.get_inp(BDL_UndergroundWallKeywords.HEIGHT))
            width = self.try_float(self.get_inp(BDL_UndergroundWallKeywords.WIDTH))
            if height is not None and width is not None:
                area = height * width
        if area is None:
            polygon = self.get_obj(self.get_inp(BDL_UndergroundWallKeywords.POLYGON))
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

    def populate_c_factor(self):
        """
        Populate the C-factor for below-grade vertical walls by removing the interior air film resistance
        """
        construction = self.get_obj(
            self.get_inp(BDL_UndergroundWallKeywords.CONSTRUCTION)
        )
        u_factor = construction.u_factor
        if u_factor:
            construction.c_factor = 1 / (1 / u_factor - 0.68)

    def populate_f_factor(self):
        """
        Populate the F-factor for below-grade horizontal walls by referencing the calculated value in the Floor object
        """
        construction = self.get_obj(
            self.get_inp(BDL_UndergroundWallKeywords.CONSTRUCTION)
        )
        if (
            self.parent.parent.f_factor
            and not construction.used_for_multiple_slabs_on_different_z
        ):
            construction.f_factor = self.parent.parent.f_factor
