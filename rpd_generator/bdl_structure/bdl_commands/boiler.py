from rpd_generator.bdl_structure.base_node import BaseNode


class Boiler(BaseNode):
    """Boiler object in the tree."""

    bdl_command = "BOILER"

    draft_type_map = {
        "HW-BOILER": "NATURAL",
        "HW-BOILER-W/DRAFT": "FORCED",
        "ELEC-HW-BOILER": "NATURAL",
        "STM-BOILER": "NATURAL",
        "STM-BOILER-W/DRAFT": "FORCED",
        "ELEC-STM-BOILER": "NATURAL",
        "HW-CONDENSING": "FORCED",
    }
    energy_source_map = {
        "HW-BOILER": None,
        "HW-BOILER-W/DRAFT": None,
        "ELEC-HW-BOILER": "ELECTRICITY",
        "STM-BOILER": None,
        "STM-BOILER-W/DRAFT": None,
        "ELEC-STM-BOILER": "ELECTRICITY",
        "HW-CONDENSING": None,
    }
    fuel_type_map = {
        "NATURAL-GAS": "NATURAL_GAS",
        "LPG": "PROPANE",
        "FUEL-OIL": "FUEL_OIL",
        "DIESEL-OIL": "OTHER",
        "COAL": "OTHER",
        "METHANOL": "OTHER",
        "OTHER-FUEL": "OTHER",
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.boiler_data_structure = {}

        # data elements with children
        self.output_validation_points = []

        # data elements with no children
        self.loop = None
        self.design_capacity = None
        self.rated_capacity = None
        self.minimum_load_ratio = None
        self.draft_type = None
        self.energy_source_type = None
        self.auxiliary_power = None
        self.operation_lower_limit = None
        self.operation_upper_limit = None

    def __repr__(self):
        return f"Boiler(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for boiler object."""
        fuel_meter_ref = self.keyword_value_pairs.get("FUEL-METER")
        fuel_meter = self.rmd.bdl_obj_instances.get(fuel_meter_ref)
        # If the fuel meter is not found, then it must be a MasterMeter.
        if fuel_meter is None:
            # This assumes the Master Fuel Meter is Natural Gas
            fuel_type = "NATURAL_GAS"
        else:
            fuel_meter_type = fuel_meter.keyword_value_pairs.get("TYPE")
            fuel_type = self.fuel_type_map.get(fuel_meter_type)
        self.energy_source_map.update(
            {
                "HW-BOILER": fuel_type,
                "HW-BOILER-W/DRAFT": fuel_type,
                "STM-BOILER": fuel_type,
                "STM-BOILER-W/DRAFT": fuel_type,
                "HW-CONDENSING": fuel_type,
            }
        )

        self.loop = self.keyword_value_pairs.get("HW-LOOP")

        self.energy_source_type = self.energy_source_map.get(
            self.keyword_value_pairs.get("TYPE")
        )

        self.draft_type = self.draft_type_map.get(self.keyword_value_pairs.get("TYPE"))
        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)
        self.auxiliary_power = output_data.get("Boilers - Sizing Info/Boiler - Aux kW")

        # Assign pump data elements populated from the boiler keyword value pairs
        pump_name = self.keyword_value_pairs.get("HW-PUMP")
        if pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.loop] * pump.qty

    def get_output_requests(self):
        """Get the output requests for the boiler object."""
        #      2315001,  59,  1,  2,  5,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Heating Loop
        #      2315002,  59,  1,  2,  1,  2,  1,  4,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Type
        #      2315003,  59,  1,  2, 13,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Capacity
        #      2315004,  59,  1,  2, 14,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Flow
        #      2315005,  59,  1,  2, 15,  1,  1,  1,  0, 22,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Electric Input Ratio
        #      2315006,  59,  1,  2, 16,  1,  1,  1,  0, 22,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Fuel Input Ratio
        #      2315007,  59,  1,  2, 17,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2064   ; Boilers - Design Parameters - Auxiliary Power
        #
        #      2315034,  59,  1,  4, 18,  1, 12,  1,  0,  4,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Heat Load
        #      2315035,  59,  1,  4, 19,  1, 12,  1,  0, 28,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Electrical Use
        #      2315036,  59,  1,  4, 20,  1, 12,  1,  0,  4,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Fuel Use
        #      2315037,  59,  1,  4, 21,  1, 12,  1,  0, 28,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Auxiliary Energy
        #      2315038,  59,  1,  4, 34,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Load Day
        #      2315039,  59,  1,  4, 35,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Load Hour
        #      2315040,  59,  1,  4, 36,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Electric Day
        #      2315041,  59,  1,  4, 37,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Electric Hour
        #      2315042,  59,  1,  4, 38,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Fuel Day
        #      2315043,  59,  1,  4, 39,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Fuel Hour
        #      2315044,  59,  1,  4, 40,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Aux. Day
        #      2315045,  59,  1,  4, 41,  0, 12,  1,  0,  1,    0,  0,  0,  0, 2064   ; Boilers - All Months - Peaks - Peak Aux. Hour

        #      2315901,  59,  1,  6,  1,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2064   ; Boilers - Rated Capacity at Peak (Btu/hr)
        #      2315902,  59,  1,  6,  2,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2064   ; Boilers - Return Water Temperature at Peak (°F)
        #
        #      2315903,  59,  1,  9,  9,  1,  1,  1,  0, 34, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Capacity, MBTU/HR !!! -99999.0 during trials
        #      2315904,  59,  1,  9, 10,  1,  1,  1,  0,128, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Head, FT !!! -99999.0 during trials
        #      2315905,  59,  1,  9, 11,  1,  1,  1,  0, 15, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Static, FT !!! -99999.0 during trials
        #      2315906,  59,  1,  9, 12,  1,  1,  1,  0, 52, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Flow, GPM !!! -99999.0 during trials
        #      2315907,  59,  1,  9, 13,  1,  1,  1,  0, 74, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Delta T, F !!! -99999.0 during trials
        #      2315908,  59,  1,  9, 14,  1,  1,  1,  0,  8, 2062,  8,  1,  0, 2064   ; Boilers - Sizing Info/Circ Loop - Design T, F !!! -99999.0 during trials

        #      2315911,  59,  1,  7,  5,  1,  1,  1,  0, 34,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Capacity
        #      2315912,  59,  1,  7,  6,  1,  1,  1,  0, 23,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Start-up
        #      2315913,  59,  1,  7,  7,  1,  1,  1,  0, 28,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Electric, kW
        #      2315914,  59,  1,  7,  8,  1,  1,  1,  0, 46,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Heat EIR
        #      2315915,  59,  1,  7,  9,  1,  1,  1,  0, 28,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Aux kW
        #      2315916,  59,  1,  7, 10,  1,  1,  1,  0, 34,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - Fuel
        #      2315916,  59,  1,  7, 11,  1,  1,  1,  0, 46,    0,  8,  1,  0, 2064   ; Boilers - Sizing Info/Boiler - HIR !!! THIS DOESN'T WORK !!! SAME ID AS PREVIOUS, RESULTS ARE FOR PREVIOUS. 2315917 DOESN'T WORK EITHER

        #      2401061,  12,  1,  7, 21,  1,  1,  1,  0, 34, 2064,  8,  1,  0,    0   ; Primary Equipment (Boilers) - Capacity (Btu/hr) !!! -99999.0 during trials
        #      2401062,  12,  1,  7, 22,  1,  1,  1,  0, 52, 2064,  8,  1,  0,    0   ; Primary Equipment (Boilers) - Flow (gal/min) !!! -99999.0 during trials
        #      2401063,  12,  1,  7, 23,  1,  1,  1,  0, 22, 2064,  8,  1,  0,    0   ; Primary Equipment (Boilers) - Rated EIR (frac) !!! -99999.0 during trials
        #      2401064,  12,  1,  7, 24,  1,  1,  1,  0, 22, 2064,  8,  1,  0,    0   ; Primary Equipment (Boilers) - Rated HIR (frac) !!! -99999.0 during trials
        #      2401065,  12,  1,  7, 25,  1,  1,  1,  0, 28, 2064,  8,  1,  0,    0   ; Primary Equipment (Boilers) - Auxiliary (kW) !!! -99999.0 during trials

        # Selected requests to populate data elements
        requests = {
            "Boilers - Design Parameters - Fuel Input Ratio": (
                2315006,
                self.u_name,
                "",
            ),
            "Boilers - Rated Capacity at Peak (Btu/hr)": (
                2315901,
                self.u_name,
                "",
            ),
            "Boilers - Return Water Temperature at Peak (°F)": (
                2315902,
                self.u_name,
                "",
            ),
            "Boilers - Sizing Info/Boiler - Capacity": (
                2315911,
                self.u_name,
                "",
            ),
            "Boilers - Sizing Info/Boiler - Heat EIR": (
                2315914,
                self.u_name,
                "",
            ),
            "Boilers - Sizing Info/Boiler - Aux kW": (
                2315915,
                self.u_name,
                "",
            ),
        }
        return requests

    def populate_data_group(self):
        """Populate schema structure for boiler object."""
        self.boiler_data_structure = {
            "id": self.u_name,
            "output_validation_points": self.output_validation_points,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "design_capacity",
            "rated_capacity",
            "minimum_load_ratio",
            "draft_type",
            "energy_source_type",
            "auxiliary_power",
            "operation_lower_limit",
            "operation_upper_limit",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.boiler_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        rmd.boilers.append(self.boiler_data_structure)
