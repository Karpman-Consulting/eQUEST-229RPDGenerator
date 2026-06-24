from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_CurveFitKeywords = BDLEnums.bdl_enums["CurveFitKeywords"]


class CurveFit(BaseDefinition):
    """CurveFit object in the tree."""

    bdl_command = BDL_Commands.CURVE_FIT

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.curve_fit_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.coefficients = []
        self.minimum_output = None
        self.maximum_output = None

    def __repr__(self):
        return f"CurveFit(u_name='{self.u_name}')"

    def populate_data_elements(self):
        self.coefficients = list(
            map(self.try_float, self.get_inp(BDL_CurveFitKeywords.COEF, []))
        )
        self.minimum_output = self.try_float(
            self.get_inp(BDL_CurveFitKeywords.OUTPUT_MIN)
        )
        self.maximum_output = self.try_float(
            self.get_inp(BDL_CurveFitKeywords.OUTPUT_MAX)
        )
