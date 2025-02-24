from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_PolygonKeywords = BDLEnums.bdl_enums["CurveFitKeywords"]


class Polygon(BaseDefinition):
    """Polygon object in the tree."""

    bdl_command = BDL_Commands.POLYGON

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.coordinates = []
        self.area = None

    def __repr__(self):
        return f"Polygon(u_name='{self.u_name}')"

    def populate_data_elements(self):
        self.coordinates = [
            tuple(map(float, map(str.strip, v)))
            for i in range(1, 121)
            if (v := self.get_inp(f"V{i}"))
        ]

        self.calculate_area_of_polygon_coords()

    def calculate_area_of_polygon_coords(self):
        """Compute and store the area of a polygon using its vertex coordinates."""

        area = 0
        for i in range(len(self.coordinates)):
            x0, y0 = self.coordinates[i]
            x1, y1 = self.coordinates[(i + 1) % len(self.coordinates)]
            area += x0 * y1 - x1 * y0
        self.area = abs(area) / 2
