from rpd_generator.bdl_structure.parent_definition import ParentDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.bdl_structure.bdl_commands.interior_wall import InteriorWall
from rpd_generator.bdl_structure.bdl_commands.underground_wall import (
    BelowGradeWall,
    BDL_UndergroundWallKeywords,
    BDL_ConstructionKeywords,
)

BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_FloorKeywords = BDLEnums.bdl_enums["FloorKeywords"]
BDL_ExteriorWallKeywords = BDLEnums.bdl_enums["ExteriorWallKeywords"]


class Floor(ParentDefinition):
    """Floor object in the tree."""

    bdl_command = BDL_Commands.FLOOR

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self
        self.rmd.floor_names.append(u_name)
        self.f_factor = None

    def __repr__(self):
        return f"Floor(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for floor object."""
        self.populate_f_factor()

    def populate_f_factor(self):
        """
        Populate f_factor for the FLOOR object, to be referenced by all UNDERGROUND-WALL floor surfaces on the FLOOR.
        The calculation considers that multiple FLOOR objects may exist on the same Z coordinate. FLOORs that share
        the same Z coordinate will have the same f_factor. The calcation assumes that all "exposed perimeter" will have
        either an UNDERGROUND-WALL or EXTERIOR-WALL wall surface on the same Z coordinate.
        """
        floors_sharing_z = [
            self,
            *[
                self.get_obj(floor_name)
                for floor_name in self.rmd.floor_names
                if self.get_obj(floor_name).get_inp(BDL_FloorKeywords.Z)
                == self.get_inp(BDL_FloorKeywords.Z)
                and self.get_obj(floor_name) != self
            ],
        ]

        # Calculate exposed perimeter for floors sharing the same Z coordinate
        total_exposed_perimeter = sum(
            surface.try_float(surface.get_inp(BDL_ExteriorWallKeywords.WIDTH)) or 0
            for floor in floors_sharing_z
            for space in floor.children
            for surface in space.children
            if not isinstance(
                surface, InteriorWall
            )  # exposed perimeter can be ExteriorWall or UndergroundWall
            and surface.get_inp(BDL_ExteriorWallKeywords.Z)
            == self.get_inp(BDL_FloorKeywords.Z)
        )
        total_slab_heat_transfer = 0

        for floor, space, surface in (
            (floor, space, surface)
            for floor in floors_sharing_z
            for space in floor.children
            for surface in space.children
        ):
            if not isinstance(surface, BelowGradeWall):
                continue

            tilt = surface.try_float(surface.get_inp(BDL_UndergroundWallKeywords.TILT))
            if tilt is None or tilt < 120:
                continue

            area = surface.try_float(surface.get_inp(BDL_UndergroundWallKeywords.AREA))
            if area is None:
                continue

            construction = self.get_obj(
                surface.get_inp(BDL_UndergroundWallKeywords.CONSTRUCTION)
            )
            u_value = (
                construction.try_float(
                    construction.get_inp(BDL_ConstructionKeywords.U_VALUE)
                )
                if construction
                else None
            )
            if u_value is None:
                continue

            total_slab_heat_transfer += area * u_value

        if total_exposed_perimeter and total_slab_heat_transfer:
            self.f_factor = total_slab_heat_transfer / total_exposed_perimeter
