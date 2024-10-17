from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BoilerCombustionOptions = SchemaEnums.schema_enums["BoilerCombustionOptions"]
EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
BoilerEfficiencyMetricOptions = SchemaEnums.schema_enums[
    "BoilerEfficiencyMetricOptions"
]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_BoilerKeywords = BDLEnums.bdl_enums["BoilerKeywords"]
BDL_BoilerTypes = BDLEnums.bdl_enums["BoilerTypes"]
BDL_FuelTypes = BDLEnums.bdl_enums["FuelTypes"]
BDL_MasterMeterKeywords = BDLEnums.bdl_enums["MasterMeterKeywords"]


class Boiler(BaseNode):
    """Boiler object in the tree."""

    bdl_command = BDL_Commands.BOILER

    draft_type_map = {
        BDL_BoilerTypes.HW_BOILER: BoilerCombustionOptions.NATURAL,
        BDL_BoilerTypes.HW_BOILER_W_DRAFT: BoilerCombustionOptions.FORCED,
        BDL_BoilerTypes.ELEC_HW_BOILER: BoilerCombustionOptions.NATURAL,
        BDL_BoilerTypes.STM_BOILER: BoilerCombustionOptions.NATURAL,
        BDL_BoilerTypes.STM_BOILER_W_DRAFT: BoilerCombustionOptions.FORCED,
        BDL_BoilerTypes.ELEC_STM_BOILER: BoilerCombustionOptions.NATURAL,
        BDL_BoilerTypes.HW_CONDENSING: BoilerCombustionOptions.FORCED,
    }
    energy_source_map = {
        BDL_BoilerTypes.HW_BOILER: None,
        BDL_BoilerTypes.HW_BOILER_W_DRAFT: None,
        BDL_BoilerTypes.ELEC_HW_BOILER: EnergySourceOptions.ELECTRICITY,
        BDL_BoilerTypes.STM_BOILER: None,
        BDL_BoilerTypes.STM_BOILER_W_DRAFT: None,
        BDL_BoilerTypes.ELEC_STM_BOILER: EnergySourceOptions.ELECTRICITY,
        BDL_BoilerTypes.HW_CONDENSING: None,
    }
    fuel_type_map = {
        BDL_FuelTypes.NATURAL_GAS: EnergySourceOptions.NATURAL_GAS,
        BDL_FuelTypes.LPG: EnergySourceOptions.PROPANE,
        BDL_FuelTypes.FUEL_OIL: EnergySourceOptions.FUEL_OIL,
        BDL_FuelTypes.DIESEL_OIL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.COAL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.METHANOL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.OTHER_FUEL: EnergySourceOptions.OTHER,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.boiler_names.append(u_name)

        self.boiler_data_structure = {}

        # data elements with children
        self.output_validation_points = []
        self.efficiency_metrics = []
        self.efficiency = []

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
        fuel_meter_ref = self.keyword_value_pairs.get(BDL_BoilerKeywords.FUEL_METER)
        fuel_meter = self.rmd.bdl_obj_instances.get(fuel_meter_ref)
        # If the fuel meter is not found, then it must be a MasterMeter.
        if fuel_meter is None:
            # TODO get the fuel type of the master fuel meter, this assumes always Natural Gas
            fuel_type = BDL_FuelTypes.NATURAL_GAS
        else:
            fuel_meter_type = fuel_meter.keyword_value_pairs.get(
                BDL_MasterMeterKeywords.TYPE
            )
            fuel_type = self.fuel_type_map.get(fuel_meter_type)
        self.energy_source_map.update(
            {
                BDL_BoilerTypes.HW_BOILER: fuel_type,
                BDL_BoilerTypes.HW_BOILER_W_DRAFT: fuel_type,
                BDL_BoilerTypes.STM_BOILER: fuel_type,
                BDL_BoilerTypes.STM_BOILER_W_DRAFT: fuel_type,
                BDL_BoilerTypes.HW_CONDENSING: fuel_type,
            }
        )

        self.loop = self.keyword_value_pairs.get(BDL_BoilerKeywords.HW_LOOP)

        self.energy_source_type = self.energy_source_map.get(
            self.keyword_value_pairs.get(BDL_BoilerKeywords.TYPE)
        )

        self.draft_type = self.draft_type_map.get(
            self.keyword_value_pairs.get(BDL_BoilerKeywords.TYPE)
        )
        self.minimum_load_ratio = self.try_float(
            self.keyword_value_pairs.get(BDL_BoilerKeywords.MIN_RATIO)
        )

        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)
        for key in [
            "Boilers - Design Parameters - Capacity",
            "Boilers - Rated Capacity at Peak (Btu/hr)",
        ]:
            if key in output_data:
                output_data[key] = self.try_convert_units(
                    output_data[key], "Btu/hr", "MMBtu/hr"
                )

        self.design_capacity = self.try_abs(
            output_data.get("Boilers - Design Parameters - Capacity")
        )
        self.rated_capacity = self.try_abs(
            output_data.get("Boilers - Rated Capacity at Peak (Btu/hr)")
        )
        self.auxiliary_power = output_data.get(
            "Boilers - Design Parameters - Auxiliary Power"
        )
        if self.energy_source_type == EnergySourceOptions.ELECTRICITY:
            boiler_e_i_r = output_data.get(
                "Boilers - Design Parameters - Electric Input Ratio"
            )
            if boiler_e_i_r:
                self.efficiency.append(1 / boiler_e_i_r)
                self.efficiency_metrics.append(BoilerEfficiencyMetricOptions.THERMAL)
            if boiler_e_i_r and boiler_e_i_r == 1:
                self.efficiency.extend([1, 1])
                self.efficiency_metrics.extend(
                    [
                        BoilerEfficiencyMetricOptions.COMBUSTION,
                        BoilerEfficiencyMetricOptions.ANNUAL_FUEL_UTILIZATION,
                    ]
                )

        else:
            boiler_f_i_r = output_data.get(
                "Boilers - Design Parameters - Fuel Input Ratio"
            )
            if boiler_f_i_r:
                self.efficiency.append(1 / boiler_f_i_r)
                self.efficiency_metrics.append(BoilerEfficiencyMetricOptions.THERMAL)
                self.efficiency.append(1 / boiler_f_i_r + 0.02)
                self.efficiency_metrics.append(BoilerEfficiencyMetricOptions.COMBUSTION)
                # EQUATIONS DERIVED FROM PRM REFERENCE MANUAL
                if 0.825 > self.efficiency[0] > 0.8:
                    self.efficiency.append((self.efficiency[0] - 0.725) / 0.1)
                    self.efficiency_metrics.append(
                        BoilerEfficiencyMetricOptions.ANNUAL_FUEL_UTILIZATION
                    )
                elif 0.825 <= self.efficiency[0] <= 0.98:
                    self.efficiency.append((self.efficiency[0] - 0.105) / 0.875)
                    self.efficiency_metrics.append(
                        BoilerEfficiencyMetricOptions.ANNUAL_FUEL_UTILIZATION
                    )

        # Assign pump data elements populated from the boiler keyword value pairs
        pump_name = self.keyword_value_pairs.get(BDL_BoilerKeywords.HW_PUMP)
        if pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.loop] * pump.qty

    def get_output_requests(self):
        """Get the output requests for the boiler object."""

        requests = {
            "Boilers - Design Parameters - Capacity": (
                2315003,
                self.u_name,
                "",
            ),
            "Boilers - Design Parameters - Flow": (
                2315004,
                self.u_name,
                "",
            ),
            "Boilers - Design Parameters - Electric Input Ratio": (
                2315005,
                self.u_name,
                "",
            ),
            "Boilers - Design Parameters - Fuel Input Ratio": (
                2315006,
                self.u_name,
                "",
            ),
            "Boilers - Design Parameters - Auxiliary Power": (
                2315007,
                self.u_name,
                "",
            ),
            "Boilers - Rated Capacity at Peak (Btu/hr)": (
                2315901,
                self.u_name,
                "",
            ),
        }
        return requests

    def populate_data_group(self):
        """Populate schema structure for boiler object."""
        self.boiler_data_structure = {
            "id": self.u_name,
            "efficiency": self.efficiency,
            "efficiency_metrics": self.efficiency_metrics,
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
