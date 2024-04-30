from rpd_generator.bdl_structure.base_node import BaseNode


class Chiller(BaseNode):
    """Chiller object in the tree."""

    bdl_command = "CHILLER"

    compressor_type_map = {
        "ELEC-OPEN-CENT": "CENTRIFUGAL",
        "ELEC-OPEN-REC": "RECIPROCATING",
        "ELEC-HERM-CENT": "CENTRIFUGAL",
        "ELEC-HERM-REC": "RECIPROCATING",
        "ELEC-SCREW": "SCREW",
        "ELEC-HTREC": "OTHER",
        "ABSOR-1": "SINGLE_EFFECT_DIRECT_FIRED_ABSORPTION",
        "ABSOR-2": "DOUBLE_EFFECT_DIRECT_FIRED_ABSORPTION",
        "GAS-ABSOR": "OTHER",
        "ENGINE": "OTHER",
        "HEAT-PUMP": "OMIT",  # Omit because it is not a chiller
        "LOOP-TO-LOOP-HP": "OMIT",  # Omit because it is not a chiller
        "WATER-ECONOMIZER": "OMIT",  # Omit because it is not a chiller
        "STRAINER-CYCLE": "OMIT",  # Omit because it is not a chiller
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.omit = False
        self.chiller_data_structure = {}

        # data elements with children
        self.capacity_validation_points = []
        self.power_validation_points = []

        # data elements with no children
        self.cooling_loop = None
        self.condensing_loop = None
        self.compressor_type = None
        self.energy_source_type = None
        self.design_capacity = None
        self.rated_capacity = None
        self.rated_entering_condenser_temperature = None
        self.rated_leaving_evaporator_temperature = None
        self.minimum_load_ratio = None
        self.design_flow_evaporator = None
        self.design_flow_condenser = None
        self.design_entering_condenser_temperature = None
        self.design_leaving_evaporator_temperature = None
        self.full_load_efficiency = None
        self.part_load_efficiency = None
        self.part_load_efficiency_metric = None
        self.is_chilled_water_pump_interlocked = None
        self.is_condenser_water_pump_interlocked = None
        self.heat_recovery_loop = None
        self.heat_recovery_fraction = None

    def __repr__(self):
        return f"Chiller(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for chiller object."""
        absorp_or_engine = False
        if self.compressor_type_map.get(self.keyword_value_pairs.get("TYPE")) == "OMIT":
            self.omit = True
            return

        elif self.keyword_value_pairs.get("TYPE") in [
            "ABSOR-1",
            "ABSOR-2",
            "GAS-ABSOR",
            "ENGINE",
        ]:
            absorp_or_engine = True

        requests = self.get_output_requests(absorp_or_engine)
        output_data = self.get_output_data(requests)

        self.cooling_loop = self.keyword_value_pairs.get("CHW-LOOP")

        self.condensing_loop = self.keyword_value_pairs.get("CW-LOOP")

        self.heat_recovery_loop = self.keyword_value_pairs.get("HTREC-LOOP")

        self.compressor_type = self.compressor_type_map.get(
            self.keyword_value_pairs.get("TYPE")
        )

        if not absorp_or_engine:
            # This value comes out in tons of refrigeration
            self.design_capacity = self.try_float(
                output_data.get("Elec Chillers - Sizing Info - Capacity")
            )

            # This value comes out in Btu/hr
            self.rated_capacity = self.try_float(
                output_data.get(
                    "Elec Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)"
                )
            )

            self.design_flow_evaporator = self.try_float(
                output_data.get("Elec Chillers - Design Parameters - Flow")
            )

            self.design_flow_condenser = self.try_float(
                output_data.get("Elec Chillers - Design Parameters - Condenser Flow")
            )

        else:
            # This value comes out in tons of refrigeration
            self.design_capacity = self.try_float(
                output_data.get("Abs/Eng Chillers - Sizing Info - Capacity")
            )

            # This value comes out in Btu/hr
            self.rated_capacity = self.try_float(
                output_data.get(
                    "Abs/Eng Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)"
                )
            )

            self.design_flow_evaporator = self.try_float(
                output_data.get("Abs/Eng Chillers - Design Parameters - Flow")
            )

            self.design_flow_condenser = self.try_float(
                output_data.get("Abs/Eng Chillers - Design Parameters - Condenser Flow")
            )

        self.rated_leaving_evaporator_temperature = self.try_float(
            self.keyword_value_pairs.get("RATED-CHW-T")
        )

        self.rated_entering_condenser_temperature = self.try_float(
            self.keyword_value_pairs.get("RATED-COND-T")
        )

        self.design_leaving_evaporator_temperature = self.try_float(
            self.keyword_value_pairs.get("DESIGN-CHW-T")
        )

        self.design_entering_condenser_temperature = self.try_float(
            self.keyword_value_pairs.get("DESIGN-COND-T")
        )

        # Assign pump data elements populated from the boiler keyword value pairs
        chw_pump_name = self.keyword_value_pairs.get("CHW-PUMP")
        if chw_pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(chw_pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.cooling_loop] * pump.qty

        # Assign pump data elements populated from the chiller keyword value pairs
        cw_pump_name = self.keyword_value_pairs.get("CW-PUMP")
        if cw_pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(cw_pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.condensing_loop] * pump.qty

    def get_output_requests(self, absorp_or_engine):
        """Get output data requests for chiller object."""
        #      2318001,  74,  1,  2,  1,  2,  1,  4,  0,  1,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Type
        #      2318002,  74,  1,  2,  5,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Cooling Loop
        #      2318003,  74,  1,  2, 13,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Capacity
        #      2318004,  74,  1,  2, 14,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Flow
        #      2318005,  74,  1,  2, 15,  1,  1,  1,  0, 22,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Electric Input Ratio
        #      2318006,  74,  1,  2, 16,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Auxiliary Power
        #      2318007,  74,  1,  3,  1,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Condenser Loop
        #      2318008,  74,  1,  3,  9,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Condenser Load
        #      2318009,  74,  1,  3, 10,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Condenser Flow
        #      2318010,  74,  1,  5,  1,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Heat Recovery Loop
        #      2318011,  74,  1,  5,  9,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Heat Recovery Capacity
        #      2318012,  74,  1,  5, 10,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Elec Chillers - Design Parameters - Heat Recovery Flow
        #      2318901,  74,  1,  9,  1,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Elec Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)
        #      2318902,  74,  1,  9,  2,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Elec Chillers - Normalized (ARI) Leaving Chilled Water Temperature (°F)
        #      2318903,  74,  1,  9,  3,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Elec Chillers - Normalized (ARI) Entering Condenser Water Temperature (°F)
        #      2318904,  74,  1,  9,  4,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Elec Chillers - Drybulb Temperature @ Peak (°F)
        #      2318905,  74,  1,  9,  5,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Elec Chillers - Wetbulb Temperature @ Peak (°F)
        #      2318907,  74,  1, 10,  1,  2,  1,  4,  0,  1,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Equipment Type
        #      2318908,  74,  1, 10,  5,  1,  1,  1,  0,129,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Capacity
        #      2318909,  74,  1, 10,  6,  1,  1,  1,  0, 23,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Startup, Hours
        #      2318910,  74,  1, 10,  7,  1,  1,  1,  0, 23,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Standby, Hours
        #      2318911,  74,  1, 10,  8,  1,  1,  1,  0, 46,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Cool EIR, BTU/BTU
        #      2318912,  74,  1, 10,  9,  1,  1,  1,  0, 49,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Cool EFF, KW/TON
        #      2318913,  74,  1, 10, 10,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Aux Elec, KW
        #      2318914,  74,  1, 10, 11,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Cond Fan, KW
        #      2318915,  74,  1, 10, 12,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2063   ; Elec Chillers - Sizing Info - Cond Pump, KW
        #      2319001,  75,  1,  2,  1,  2,  1,  4,  0,  1,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Type
        #      2319002,  75,  1,  2,  5,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Cooling Loop
        #      2319003,  75,  1,  2, 13,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Capacity
        #      2319004,  75,  1,  2, 14,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Flow
        #      2319005,  75,  1,  2, 15,  1,  1,  1,  0, 22,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Electric Input Ratio
        #      2319006,  75,  1,  2, 16,  1,  1,  1,  0, 22,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heating Input Ratio
        #      2319007,  75,  1,  2, 17,  1,  1,  1,  0, 28,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Auxiliary Power
        #      2319008,  75,  1,  3,  1,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Condenser Loop
        #      2319009,  75,  1,  3,  9,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Condenser Load
        #      2319010,  75,  1,  3, 10,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Condenser Flow
        #      2319011,  75,  1,  4,  1,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heating Loop (Absorption)
        #      2319012,  75,  1,  4,  9,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heating Loop Load
        #      2319013,  75,  1,  4, 10,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heating Loop Flow
        #      2319014,  75,  1,  5,  1,  2,  1,  8,  0,  1,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heat Recovery Loop
        #      2319015,  75,  1,  5,  9,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heat Recovery Capacity
        #      2319016,  75,  1,  5, 10,  1,  1,  1,  0, 52,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Design Parameters - Heat Recovery Flow
        #      2319901,  74,  1,  9,  1,  1,  1,  1,  0,  4,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)
        #      2319902,  74,  1,  9,  2,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Normalized (ARI) Leaving Chilled Water Temperature (°F)
        #      2319903,  74,  1,  9,  3,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Normalized (ARI) Entering Condenser Water Temperature (°F)
        #      2319904,  74,  1,  9,  4,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Drybulb Temperature @ Peak (°F)
        #      2319905,  74,  1,  9,  5,  1,  1,  1,  0,  8,    0,  0,  0,  0, 2063   ; Abs/Eng Chillers - Wetbulb Temperature @ Peak (°F)
        #

        if not absorp_or_engine:
            requests = {
                "Elec Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)": (
                    2318901,
                    self.u_name,
                    "",
                ),
                "Elec Chillers - Sizing Info - Capacity": (2318908, self.u_name, ""),
                "Elec Chillers - Design Parameters - Flow": (2318004, self.u_name, ""),
                "Elec Chillers - Design Parameters - Condenser Flow": (
                    2318009,
                    self.u_name,
                    "",
                ),
            }
        else:
            requests = {
                "Abs/Eng Chillers - Normalized (ARI) Capacity at Peak (Btu/hr)": (
                    2319901,
                    self.u_name,
                    "",
                ),
                "Abs/Eng Chillers - Sizing Info - Capacity": (2319908, self.u_name, ""),
                "Abs/Eng Chillers - Design Parameters - Flow": (
                    2319004,
                    self.u_name,
                    "",
                ),
                "Abs/Eng Chillers - Design Parameters - Condenser Flow": (
                    2319010,
                    self.u_name,
                    "",
                ),
            }

        return requests

    def populate_data_group(self):
        """Populate schema structure for chiller object."""
        if self.omit:
            return

        self.chiller_data_structure = {
            "id": self.u_name,
            "capacity_validation_points": self.capacity_validation_points,
            "power_validation_points": self.power_validation_points,
        }

        no_children_attributes = [
            "cooling_loop",
            "condending_loop",
            "compressor_type",
            "energy_source_type",
            "design_capacity",
            "rated_capacity",
            "rated_entering_condenser_temperature",
            "rated_leaving_evaporator_temperature",
            "minimum_load_ratio",
            "design_flow_evaporator",
            "design_flow_condenser",
            "design_entering_condenser_temperature",
            "design_leaving_evaporator_temperature",
            "full_load_efficiency",
            "part_load_efficiency",
            "part_load_efficiency_metric",
            "is_chilled_water_pump_interlocked",
            "is_condenser_water_pump_interlocked",
            "heat_recovery_loop",
            "heat_recovery_fraction",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.chiller_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert chiller object into the rpd data structure."""
        if self.omit:
            return

        rmd.chillers.append(self.chiller_data_structure)
