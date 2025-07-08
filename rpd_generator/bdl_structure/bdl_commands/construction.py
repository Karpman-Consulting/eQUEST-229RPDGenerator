from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_ConstructionKeywords = BDLEnums.bdl_enums["ConstructionKeywords"]
BDL_ExteriorWallKeywords = BDLEnums.bdl_enums["ExteriorWallKeywords"]
BDL_UndergroundWallKeywords = BDLEnums.bdl_enums["UndergroundWallKeywords"]
BDL_MaterialTypes = BDLEnums.bdl_enums["MaterialTypes"]


class Construction(BaseNode):
    """Construction object in the tree."""

    bdl_command = BDL_Commands.CONSTRUCTION

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.used_for_multiple_slabs_on_different_z = False

        self.construction_data_structure = {}
        self.material_references = None

        # data elements with children
        self.primary_layers = []
        self.framing_layers = []
        self.insulation_locations = []
        self.r_values = []

        # data elements with no children
        self.classification = None
        self.fraction_framing = None
        self.u_factor = None
        self.c_factor = None
        self.f_factor = None
        self.has_radiant_heating = None
        self.has_radiant_cooling = None

    def __repr__(self):
        return f"Construction(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for construction object."""
        layer = self.get_obj(self.get_inp(BDL_ConstructionKeywords.LAYERS))
        # Material references will be empty if construction uses U-Value Input method
        self.material_references = layer.material_references if layer else []

        # This u_factor will be adjusted when used for a surface based on Ext/Int/Underground Wall air film resistances
        self.u_factor = self.try_float(self.get_inp(BDL_ConstructionKeywords.U_VALUE))

        if self.u_factor and self.is_assigned_to_exterior_wall():
            # For exterior walls, the U-factor is adjusted by the exterior air film resistance
            ext_air_film_resistance = 0.17
            self.u_factor = 1 / (1 / self.u_factor + ext_air_film_resistance)

        # Determine if the constructions is assigned to multiple slabs on different Z coordinates
        z_coordinate_set = set()
        for underground_wall_name in self.rmd.undg_wall_names:
            underground_wall = self.get_obj(underground_wall_name)
            if (
                underground_wall.get_inp(BDL_UndergroundWallKeywords.CONSTRUCTION)
                != self.u_name
            ):
                continue

            tilt = underground_wall.try_float(
                underground_wall.get_inp(BDL_UndergroundWallKeywords.TILT)
            )
            if tilt is None or tilt <= 120:
                continue

            z_coordinate_set.add(
                underground_wall.get_inp(BDL_UndergroundWallKeywords.Z)
            )

        self.used_for_multiple_slabs_on_different_z = len(z_coordinate_set) > 1

    def populate_data_group(self):
        """Populate schema structure for construction object."""

        for material_reference in self.material_references or []:
            material = self.get_obj(material_reference)
            if material:
                self.primary_layers.append(material.material_data_structure)

        self.construction_data_structure = {
            "id": self.u_name,
            "primary_layers": self.primary_layers,
            "framing_layers": self.framing_layers,
            "insulation_locations": self.insulation_locations,
            "r_values": self.r_values,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "fraction_framing",
            "u_factor",
            "c_factor",
            "f_factor",
            "has_radiant_heating",
            "has_radiant_cooling",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.construction_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert construction object into the rpd data structure."""
        self.rmd.constructions.append(self.construction_data_structure)

    def is_assigned_to_exterior_wall(self):
        """Check if this construction is assigned to an exterior wall."""
        for exterior_wall_name in self.rmd.ext_wall_names:
            exterior_wall = self.get_obj(exterior_wall_name)
            if (
                exterior_wall.get_inp(BDL_ExteriorWallKeywords.CONSTRUCTION)
                == self.u_name
            ):
                return True
        return False
