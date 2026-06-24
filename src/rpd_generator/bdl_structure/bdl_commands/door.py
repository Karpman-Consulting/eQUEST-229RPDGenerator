import copy
from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

SubsurfaceClassificationOptions = SchemaEnums.schema_enums[
    "SubsurfaceClassificationOptions"
]
SubsurfaceDynamicGlazingOptions = SchemaEnums.schema_enums[
    "SubsurfaceDynamicGlazingOptions"
]
StatusOptions = SchemaEnums.schema_enums["StatusOptions"]
SubsurfaceSubclassificationOptions2019ASHRAE901 = SchemaEnums.schema_enums[
    "SubsurfaceSubclassificationOptions2019ASHRAE901"
]
SubsurfaceFrameOptions2019ASHRAE901 = SchemaEnums.schema_enums[
    "SubsurfaceFrameOptions2019ASHRAE901"
]
SurfaceAdjacencyOptions = SchemaEnums.schema_enums["SurfaceAdjacencyOptions"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_DoorKeywords = BDLEnums.bdl_enums["DoorKeywords"]
BDL_ConstructionKeywords = BDLEnums.bdl_enums["ConstructionKeywords"]
BDL_ConstructionTypes = BDLEnums.bdl_enums["ConstructionTypes"]
BDL_WallLocationOptions = BDLEnums.bdl_enums["WallLocationOptions"]
BDL_ExteriorWallKeywords = BDLEnums.bdl_enums["ExteriorWallKeywords"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]


class Door(ChildNode):
    """Door object in the tree."""

    bdl_command = BDL_Commands.DOOR

    door_subclassification_map = {
        1: SubsurfaceSubclassificationOptions2019ASHRAE901.SWINGING_DOOR,
        2: SubsurfaceSubclassificationOptions2019ASHRAE901.NONSWINGING_DOOR,
        3: SubsurfaceSubclassificationOptions2019ASHRAE901.SECTIONAL_GARAGE_DOOR,
        4: SubsurfaceSubclassificationOptions2019ASHRAE901.METAL_COILING_DOOR,
        5: SubsurfaceSubclassificationOptions2019ASHRAE901.OTHER,
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        self.rmd.door_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.door_data_structure = {}

        # data elements with no children
        self.classification = None
        self.subclassification = None
        self.is_operable = None
        self.has_open_sensor = None
        self.framing_type = None
        self.glazed_area = None
        self.opaque_area = None
        self.u_factor = None
        self.dynamic_glazing_type = None
        self.solar_heat_gain_coefficient = None
        self.maximum_solar_heat_gain_coefficient = None
        self.visible_transmittance = None
        self.minimum_visible_transmittance = None
        self.depth_of_overhang = None
        self.has_shading_overhang = None
        self.has_shading_sidefins = None
        self.has_manual_interior_shades = None
        self.solar_transmittance_multiplier_summer = None
        self.solar_transmittance_multiplier_winter = None
        self.has_automatic_shades = None
        self.status_type = None

    def __repr__(self):
        return f"Door(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for door object."""
        self.classification = SubsurfaceClassificationOptions.DOOR
        self.subclassification = self.door_subclassification_map.get(
            self.try_int(self.get_inp(BDL_DoorKeywords.C_TYPE))
        )
        self.u_factor = self.calc_u_factor()
        height = self.try_float(self.get_inp(BDL_DoorKeywords.HEIGHT))
        width = self.try_float(self.get_inp(BDL_DoorKeywords.WIDTH))
        if height is not None and width is not None:
            self.opaque_area = height * width
            self.glazed_area = 0

    def populate_data_group(self):
        """Populate schema structure for door object."""
        self.door_data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "subclassification",
            "is_operable",
            "framing_type",
            "glazed_area",
            "opaque_area",
            "u_factor",
            "dynamic_glazing_type",
            "solar_heat_gain_coefficient",
            "maximum_solar_heat_gain_coefficient",
            "has_shading_overhang",
            "has_shading_sidefins",
            "has_manual_interior_shades",
            "solar_transmittance_multiplier_summer",
            "solar_transmittance_multiplier_winter",
            "has_automatic_shades",
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.door_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert door object into the rpd data structure."""
        # Parent wall (Python object)
        wall_obj = self.get_obj(self.parent.u_name)
        if not wall_obj:
            return

        # Resolve base zone via space
        base_zone = self.rmd.space_map.get(wall_obj.parent.u_name)
        if not base_zone:
            return

        building_segment = base_zone.parent_building_segment

        # Space-level replication
        space_multiplier = (
            self.try_int(wall_obj.parent.get_inp(BDL_SpaceKeywords.MULTIPLIER, 1)) or 1
        )
        space_replications = space_multiplier - 1

        # Zone-level replication
        zone_replications = base_zone.replications or 0

        # Find all wall data structures this door belongs to
        def matching_wall_dicts():
            results = []
            for zone_ds in building_segment.zones:
                for surface in zone_ds.get("surfaces", []):
                    if surface.get("id", "").startswith(self.parent.u_name):
                        results.append(surface)
            return results

        wall_dicts = matching_wall_dicts()
        if not wall_dicts:
            return

        # Append door (and replicas) to each wall dict
        for wall_rep_idx, wall_ds in enumerate(wall_dicts):
            # Base door
            if wall_rep_idx == 0:
                wall_ds["subsurfaces"].append(self.door_data_structure)
            else:
                clone = copy.deepcopy(self.door_data_structure)
                self.increment_ids(clone, wall_rep_idx)
                wall_ds["subsurfaces"].append(clone)

            # Space replications
            for s in range(1, space_replications + 1):
                clone = copy.deepcopy(self.door_data_structure)
                self.increment_ids(clone, s)
                if wall_rep_idx:
                    self.increment_ids(clone, wall_rep_idx)
                wall_ds["subsurfaces"].append(clone)

    def calc_u_factor(self):
        """Calculate the U-factor for the door."""
        construction_obj = self.get_obj(self.get_inp(BDL_DoorKeywords.CONSTRUCTION))
        ext_air_film_resistance = 0.17
        int_air_film_resistance = 0.68
        if self.parent.adjacent_to == SurfaceAdjacencyOptions.EXTERIOR:
            if construction_obj and construction_obj.u_factor is not None:
                u_factor = 1 / (
                    1 / construction_obj.u_factor
                    + ext_air_film_resistance
                    + int_air_film_resistance
                )
                return u_factor
            else:
                return None
        else:
            if construction_obj and construction_obj.u_factor is not None:
                u_factor = 1 / (
                    1 / construction_obj.u_factor + 2 * int_air_film_resistance
                )
                return u_factor
            else:
                return None
