from rpd_generator.bdl_structure.base_node import BaseNode


class Pump(BaseNode):
    """Pump object in the tree."""

    bdl_command = "PUMP"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.qty = None
        self.pump_data_structures = []
        self.output_data = None
        # data elements with children
        self.output_validation_points = []

        # data elements with no children
        self.loop_or_piping = []
        self.specification_method = []
        self.design_electric_power = []
        # self.motor_nameplate_power = None  # Commented because eQUEST does not support this attribute, nor will we
        self.design_head = []
        self.impeller_efficiency = []
        self.motor_efficiency = []
        self.speed_control = []
        self.design_flow = []
        self.is_flow_sized_based_on_design_day = []

    def __repr__(self):
        return f"Pump(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate the schema data elements for the pump object."""
        self.qty = int(self.try_float(self.keyword_value_pairs.get("NUMBER")))
        requests = self.get_output_requests()
        self.output_data = self.get_output_data(requests)
        self.loop_or_piping = [None] * self.qty
        self.speed_control = [None] * self.qty
        self.is_flow_sized_based_on_design_day = [None] * self.qty

        spec_method = (
            "SIMPLE"
            if self.keyword_value_pairs.get("PUMP-KW") is not None
            else "DETAILED"
        )
        design_head = self.try_float(self.keyword_value_pairs.get("HEAD"))

        self.specification_method = [spec_method] * self.qty

        if spec_method == "SIMPLE":
            self.design_electric_power = [
                self.try_float(self.keyword_value_pairs.get("PUMP-KW"))
            ] * self.qty
        else:
            self.design_electric_power = [
                self.output_data.get("Pump - Power (kW)")
            ] * self.qty

        self.design_head = [design_head] * self.qty

        self.impeller_efficiency = [
            self.output_data.get("Pump - Mechanical Eff (frac)")
        ] * self.qty

        self.motor_efficiency = [
            self.output_data.get("Pump - Motor Eff (frac)")
        ] * self.qty

        self.design_flow = [self.output_data.get("Pump - Flow (gal/min)")] * self.qty

    def get_output_requests(self):
        """Get the output requests for the pump object."""
        #      2401001,  12,  1,  4,  9,  0,  1,  1,  0,  1, 2061,  8,  1,  0,    0   ; Pump - Number of Pumps
        #      2401002,  12,  1,  4, 18,  1,  1,  1,  0, 52, 2061,  8,  1,  0,    0   ; Pump - Flow (gal/min)
        #      2401003,  12,  1,  4, 19,  1,  1,  1,  0,128, 2061,  8,  1,  0,    0   ; Pump - Head (ft)
        #      2401004,  12,  1,  4, 20,  1,  1,  1,  0,128, 2061,  8,  1,  0,    0   ; Pump - Head Setpoint (ft)
        #      2401005,  12,  1,  4, 24,  1,  1,  1,  0, 28, 2061,  8,  1,  0,    0   ; Pump - Power (kW)
        #      2401006,  12,  1,  4, 25,  1,  1,  1,  0, 22, 2061,  8,  1,  0,    0   ; Pump - Mechanical Eff (frac)
        #      2401007,  12,  1,  4, 26,  1,  1,  1,  0, 22, 2061,  8,  1,  0,    0   ; Pump - Motor Eff (frac)
        requests = {
            "Pump - Flow (gal/min)": (2401002, "", self.u_name),
            "Pump - Power (kW)": (2401005, "", self.u_name),
            "Pump - Mechanical Eff (frac)": (2401006, "", self.u_name),
            "Pump - Motor Eff (frac)": (2401007, "", self.u_name),
        }
        return requests

    def populate_data_group(self):
        """Populate the schema data structure for the pump object."""

        no_children_attributes = [
            "loop_or_piping",
            "specification_method",
            "design_electric_power",
            "design_head",
            "impeller_efficiency",
            "motor_efficiency",
            "speed_control",
            "design_flow",
            "is_flow_sized_based_on_design_day",
        ]

        for i in range(self.qty):
            pump_data_structure = {
                "id": self.u_name + f" {i}".replace(" 0", ""),
                "output_validation_points": [],
            }
            # Iterate over the no_children_attributes list and populate if the value is not None
            for attr in no_children_attributes:
                values = getattr(self, attr, None)
                value = values[i]
                if value is not None:
                    pump_data_structure[attr] = value
            self.pump_data_structures.append(pump_data_structure)

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.pumps.extend(self.pump_data_structures)
