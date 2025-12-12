import copy
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

        if self.classification == SurfaceClassificationOptions.WALL:
            self.populate_c_factor()

        if self.classification == SurfaceClassificationOptions.FLOOR:
            self.populate_f_factor()

        optical_properties = SurfaceOpticalProperties(self)
        optical_properties.populate_data_elements()
        optical_properties.populate_data_group()
        optical_properties.insert_to_rpd()

    def populate_data_group(self):
        """Populate schema structure for below grade wall object."""

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
        base_zone = self.rmd.space_map.get(self.parent.u_name)
        if not base_zone:
            return

        # Space-level replication
        space_multiplier = (
            self.try_int(self.parent.get_inp(BDL_SpaceKeywords.MULTIPLIER, 1)) or 1
        )
        space_replications = space_multiplier - 1

        # Zone-level replication (floor multiplier)
        zone_replications = base_zone.replications or 0

        building_segment = base_zone.parent_building_segment

        def find_zone_data_structure(zone_id):
            for z in building_segment.zones:
                if z.get("id") == zone_id:
                    return z
            return None

        # Helper to append surface with optional replication index
        def append_surface(zone_data_structure, zone_rep_idx=0, space_rep_idx=0):
            if zone_rep_idx == 0 and space_rep_idx == 0:
                zone_data_structure["surfaces"].append(
                    self.underground_wall_data_structure
                )
                return

            clone = copy.deepcopy(self.underground_wall_data_structure)
            # First increment by space replication
            if space_rep_idx:
                self.increment_ids(clone, space_rep_idx)
            # Then increment by zone replication
            if zone_rep_idx:
                self.increment_ids(clone, zone_rep_idx)

            zone_data_structure["surfaces"].append(clone)

        # Base zone
        base_zone_data_structure = find_zone_data_structure(base_zone.u_name)
        if base_zone_data_structure:
            append_surface(base_zone_data_structure)

            for s in range(1, space_replications + 1):
                append_surface(base_zone_data_structure, space_rep_idx=s)

        # Replicated zones
        for z in range(1, zone_replications + 1):
            zone_id = f"{base_zone.u_name} - {z}"
            zone_data_structure = find_zone_data_structure(zone_id)
            if not zone_data_structure:
                continue

            append_surface(zone_data_structure, zone_rep_idx=z)

            for s in range(1, space_replications + 1):
                append_surface(zone_data_structure, zone_rep_idx=z, space_rep_idx=s)

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


class SurfaceOpticalProperties:
    def __init__(self, wall):
        self.wall = wall

        self.data_structure = {}

        # data elements for surface optical properties
        self.absorptance_thermal_exterior = None
        self.absorptance_solar_exterior = None
        self.absorptance_visible_exterior = None
        self.absorptance_thermal_interior = None
        self.absorptance_solar_interior = None
        self.absorptance_visible_interior = None

    def __repr__(self):
        return f"SurfaceOpticalProperties()"

    def populate_data_elements(self):
        self.absorptance_solar_interior = self.wall.try_float(
            self.wall.get_inp(BDL_UndergroundWallKeywords.INSIDE_SOL_ABS)
        )

        reflectance_visible_interior = self.wall.try_float(
            self.wall.get_inp(BDL_UndergroundWallKeywords.INSIDE_VIS_REFL)
        )
        if reflectance_visible_interior is not None:
            self.absorptance_visible_interior = 1 - reflectance_visible_interior

    def populate_data_group(self):
        self.data_structure["id"] = self.wall.u_name + " OpticalProps"

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
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.wall.optical_properties = self.data_structure
