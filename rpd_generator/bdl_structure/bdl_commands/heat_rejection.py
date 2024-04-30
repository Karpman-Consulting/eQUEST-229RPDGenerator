from rpd_generator.bdl_structure.base_node import BaseNode


class HeatRejection(BaseNode):
    """Heat Rejection object in the tree."""

    bdl_command = "HEAT-REJECTION"

    heat_rejection_type_map = {
        "OPEN-TWR": "OPEN_CIRCUIT_COOLING_TOWER",
        "OPEN-TWR&HX": "OPEN_CIRCUIT_COOLING_TOWER",  # Should this be OTHER?
        "FLUID-COOLER": "CLOSED_CIRCUIT_COOLING_TOWER",
        "DRYCOOLER": "DRY_COOLER",
        # "": "EVAPORATIVE_CONDENSER",  # Selecting Evap Condenser in eQUEST crashes the program. Not shown in Helptext.
    }

    fan_spd_ctrl_map = {
        "ONE-SPEED-FAN": "CONSTANT",
        "FLUID-BYPASS": "CONSTANT",
        "TWO-SPEED-FAN": "TWO_SPEED",
        "VARIABLE-SPEED-FAN": "VARIABLE_SPEED",
        "DISCHARGE-DAMPER": "OTHER",
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.heat_rejection_data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = None
        self.fan_type = None
        self.fluid = None
        self.range = None
        self.approach = None
        self.fan_shaft_power = None
        self.fan_motor_efficiency = None
        self.fan_motor_nameplate_power = None
        self.fan_speed_control = None
        self.design_wetbulb_temperature = None
        self.design_water_flowrate = None
        self.rated_water_flowrate = None
        self.leaving_water_setpoint_temperature = None

    def __repr__(self):
        return f"HeatRejection(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for heat rejection object."""
        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)

        self.loop = self.keyword_value_pairs.get("CW-LOOP")

        self.type = self.heat_rejection_type_map.get(
            self.keyword_value_pairs.get("TYPE")
        )

        self.fan_speed_control = self.fan_spd_ctrl_map.get(
            self.keyword_value_pairs.get("CAPACITY-CTRL")
        )

        self.range = self.try_float(self.keyword_value_pairs.get("RATED-RANGE"))

        self.approach = self.try_float(self.keyword_value_pairs.get("RATED-APPROACH"))

        self.design_wetbulb_temperature = self.try_float(
            self.keyword_value_pairs.get("DESIGN-WETBULB")
        )

        self.rated_water_flowrate = self.try_float(
            output_data.get("Cooling Tower - Flow (gal/min)")
        )

        circulation_loop = self.rmd.bdl_obj_instances.get(self.loop)
        if circulation_loop is not None:
            self.leaving_water_setpoint_temperature = (
                circulation_loop.design_supply_temperature[0]
            )

        # Assign pump data elements populated from the heat rejection keyword value pairs
        cw_pump_name = self.keyword_value_pairs.get("CW-PUMP")
        if cw_pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(cw_pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.loop] * pump.qty

    def get_output_requests(self):
        """Return the output requests for the heat rejection object."""
        #      2401021,  12,  1,  7, 21,  1,  1,  1,  0,  4, 2066,  8,  1,  0,    0   ; Cooling Tower - Capacity (Btu/hr)
        #      2401022,  12,  1,  7, 22,  1,  1,  1,  0, 52, 2066,  8,  1,  0,    0   ; Cooling Tower - Flow (gal/min)
        #      2401023,  12,  1,  7, 23,  0,  1,  1,  0,  1, 2066,  8,  1,  0,    0   ; Cooling Tower - Number of Cells
        #      2401024,  12,  1,  7, 24,  1,  1,  1,  0, 28, 2066,  8,  1,  0,    0   ; Cooling Tower - Fan Power per Cell (kW)
        #      2401025,  12,  1,  7, 25,  1,  1,  1,  0, 28, 2066,  8,  1,  0,    0   ; Cooling Tower - Spray Power per Cell (kW)
        #      2401026,  12,  1,  7, 26,  1,  1,  1,  0, 28, 2066,  8,  1,  0,    0   ; Cooling Tower - Auxiliary (kW)
        requests = {
            "Cooling Tower - Capacity (Btu/hr)": (2401021, "", self.u_name),
            "Cooling Tower - Flow (gal/min)": (2401022, "", self.u_name),
            "Cooling Tower - Number of Cells": (2401023, "", self.u_name),
            "Cooling Tower - Fan Power per Cell (kW)": (2401024, "", self.u_name),
            "Cooling Tower - Spray Power per Cell (kW)": (2401025, "", self.u_name),
            "Cooling Tower - Auxiliary (kW)": (2401026, "", self.u_name),
        }
        return requests

    def populate_data_group(self):
        """Populate schema structure for heat rejection object."""
        self.heat_rejection_data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "fan_type",
            "fluid",
            "range",
            "approach",
            "fan_shaft_power",
            "fan_motor_efficiency",
            "fan_motor_nameplate_power",
            "fan_speed_control",
            "design_wetbulb_temperature",
            "design_water_flowrate",
            "rated_water_flowrate",
            "leaving_water_setpoint_temperature",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.heat_rejection_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.heat_rejections.append(self.heat_rejection_data_structure)
