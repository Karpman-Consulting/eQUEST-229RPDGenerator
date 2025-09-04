from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.utilities.curve_funcs import calculate_cubic
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
HeatingSystemOptions = SchemaEnums.schema_enums["HeatingSystemOptions"]
CoolingSystemOptions = SchemaEnums.schema_enums["CoolingSystemOptions"]
FanSystemSupplyFanControlOptions = SchemaEnums.schema_enums[
    "FanSystemSupplyFanControlOptions"
]
FanSystemOperationOptions = SchemaEnums.schema_enums["FanSystemOperationOptions"]
FanSystemTemperatureControlOptions = SchemaEnums.schema_enums[
    "FanSystemTemperatureControlOptions"
]
FanSpecificationMethodOptions = SchemaEnums.schema_enums[
    "FanSpecificationMethodOptions"
]
AirEconomizerOptions = SchemaEnums.schema_enums["AirEconomizerOptions"]
EnergyRecoveryOptions = SchemaEnums.schema_enums["EnergyRecoveryOptions"]
EnergyRecoveryOperationOptions = SchemaEnums.schema_enums[
    "EnergyRecoveryOperationOptions"
]
EnergyRecoverySupplyAirTemperatureControlOptions = SchemaEnums.schema_enums[
    "EnergyRecoverySupplyAirTemperatureControlOptions"
]
DemandControlVentilationControlOptions = SchemaEnums.schema_enums[
    "DemandControlVentilationControlOptions"
]
HumidificationOptions = SchemaEnums.schema_enums["HumidificationOptions"]
HeatpumpAuxiliaryHeatOptions = SchemaEnums.schema_enums["HeatpumpAuxiliaryHeatOptions"]
CoolingMetricOptions = SchemaEnums.schema_enums["CoolingMetricOptions"]
HeatingMetricOptions = SchemaEnums.schema_enums["HeatingMetricOptions"]


BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_SystemKeywords = BDLEnums.bdl_enums["SystemKeywords"]
BDL_ZoneKeywords = BDLEnums.bdl_enums["ZoneKeywords"]
BDL_MasterMeterKeywords = BDLEnums.bdl_enums["MasterMeterKeywords"]
BDL_SystemTypes = BDLEnums.bdl_enums["SystemTypes"]
BDL_SystemHeatingTypes = BDLEnums.bdl_enums["SystemHeatingTypes"]
BDL_SystemCoolingTypes = BDLEnums.bdl_enums["SystemCoolingTypes"]
BDL_CoolControlOptions = BDLEnums.bdl_enums["SystemCoolControlOptions"]
BDL_HeatControlOptions = BDLEnums.bdl_enums["SystemHeatControlOptions"]
BDL_SystemFanControlOptions = BDLEnums.bdl_enums["SystemFanControlOptions"]
BDL_NightCycleControlOptions = BDLEnums.bdl_enums["SystemNightCycleControlOptions"]
BDL_EconomizerOptions = BDLEnums.bdl_enums["SystemEconomizerOptions"]
BDL_EnergyRecoveryTypes = BDLEnums.bdl_enums["SystemEnergyRecoveryTypes"]
BDL_EnergyRecoveryOptions = BDLEnums.bdl_enums["SystemEnergyRecoveryOptions"]
BDL_EnergyRecoveryOperationOptions = BDLEnums.bdl_enums[
    "SystemEnergyRecoveryOperationOptions"
]
BDL_EnergyRecoveryTemperatureControlOptions = BDLEnums.bdl_enums[
    "SystemEnergyRecoveryTemperatureControlOptions"
]
BDL_SystemMinimumOutdoorAirControlOptions = BDLEnums.bdl_enums[
    "SystemMinimumOutdoorAirControlOptions"
]
BDL_FanPlacementOptions = BDLEnums.bdl_enums["SystemFanPlacementOptions"]
BDL_IndoorFanModeOptions = BDLEnums.bdl_enums["SystemIndoorFanModeOptions"]
BDL_HumidificationOptions = BDLEnums.bdl_enums["SystemHumidificationOptions"]
BDL_DualDuctFanOptions = BDLEnums.bdl_enums["SystemDualDuctFanOptions"]
BDL_ReturnFanOptions = BDLEnums.bdl_enums["SystemReturnFanLocationOptions"]
BDL_HPSupplementSourceOptions = BDLEnums.bdl_enums["HPSupplementSourceOptions"]
BDL_OutputCoolingTypes = BDLEnums.bdl_enums["OutputCoolingTypes"]
BDL_OutputHeatingTypes = BDLEnums.bdl_enums["OutputHeatingTypes"]
BDL_ReturnAirPathOptions = BDLEnums.bdl_enums["SystemReturnAirPathOptions"]
BDL_WLHPCategoryOptions = BDLEnums.bdl_enums["SystemWLHPCategoryOptions"]
BDL_SystemCondenserTypes = BDLEnums.bdl_enums["SystemCondenserTypes"]
BDL_CondenserKeywords = BDLEnums.bdl_enums["CondenserKeywords"]
BDL_ZoneFanControlOptions = BDLEnums.bdl_enums["ZoneFanControlOptions"]
BDL_ZoneTypeOptions = BDLEnums.bdl_enums["ZoneTypeOptions"]


class System(ParentNode):
    """System object in the tree."""

    bdl_command = BDL_Commands.SYSTEM
    zonal_system_types = [
        BDL_SystemTypes.UHT,
        BDL_SystemTypes.UVT,
        BDL_SystemTypes.FC,
        BDL_SystemTypes.HP,
        BDL_SystemTypes.PTAC,
    ]
    reheat_system_types = [
        BDL_SystemTypes.MZS,
        BDL_SystemTypes.DDS,
        BDL_SystemTypes.SZCI,
        BDL_SystemTypes.IU,
        BDL_SystemTypes.VAVS,
        BDL_SystemTypes.RHFS,
        BDL_SystemTypes.HVSYS,
        BDL_SystemTypes.CBVAV,
        BDL_SystemTypes.PMZS,
        BDL_SystemTypes.PVAVS,
        BDL_SystemTypes.PIU,
        BDL_SystemTypes.FNSYS,
        BDL_SystemTypes.PTGSD,
        BDL_SystemTypes.SZRH,
        BDL_SystemTypes.DOAS,
    ]
    terminal_selection_system_types = [
        BDL_SystemTypes.MZS,
        BDL_SystemTypes.DDS,
        BDL_SystemTypes.SZCI,
        BDL_SystemTypes.IU,
        BDL_SystemTypes.VAVS,
        BDL_SystemTypes.RHFS,
        BDL_SystemTypes.RHFS,
        BDL_SystemTypes.HVSYS,
        BDL_SystemTypes.CBVAV,
        BDL_SystemTypes.PMZS,
        BDL_SystemTypes.PVAVS,
        BDL_SystemTypes.PIU,
        BDL_SystemTypes.FNSYS,
        BDL_SystemTypes.PTGSD,
    ]
    BDL_condenser_output_cool_type_map = {
        BDL_SystemCondenserTypes.AIR_COOLED: BDL_OutputCoolingTypes.DX_AIR_COOLED,
        BDL_SystemCondenserTypes.WATER_COOLED: BDL_OutputCoolingTypes.DX_WATER_COOLED,
        BDL_SystemCondenserTypes.EVAP_PRECOOLED: None,
        BDL_SystemCondenserTypes.EVAP_COOLED: None,
    }
    BDL_condenser_output_heat_type_map = {
        BDL_SystemCondenserTypes.AIR_COOLED: BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED,
        BDL_SystemCondenserTypes.WATER_COOLED: BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED,
        BDL_SystemCondenserTypes.EVAP_PRECOOLED: None,
        BDL_SystemCondenserTypes.EVAP_COOLED: None,
    }
    humidification_map = {
        BDL_HumidificationOptions.NONE: HumidificationOptions.NONE,
        BDL_HumidificationOptions.ELECTRIC: HumidificationOptions.OTHER,
        BDL_HumidificationOptions.HOT_WATER: HumidificationOptions.OTHER,
        BDL_HumidificationOptions.STEAM: HumidificationOptions.OTHER,
        BDL_HumidificationOptions.FURNACE: HumidificationOptions.OTHER,
        BDL_HumidificationOptions.HEAT_PUMP: HumidificationOptions.OTHER,
        BDL_HumidificationOptions.DHW_LOOP: HumidificationOptions.OTHER,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        # On initialization the parent building segment is not known. It is set in the Space object methods.
        self.parent_building_segment = self.get_obj("Default Building Segment")

        self.vrf_sys_condenser = None

        if u_name not in self.rmd.bdl_obj_instances:
            self.rmd.system_names.append(u_name)
            self.rmd.bdl_obj_instances[u_name] = self

        # used to store the unique 229 schema ID for zonal systems, so that the original BDL u_name may be preserved
        self.sys_id = None

        self.system_data_structure = {}

        self.omit = False
        self.is_terminal = False
        self.is_zonal_system = False
        self.is_derived_system = False
        self.bdl_output_cool_type = None
        self.bdl_output_heat_type = None
        self.preheat_system_type = None

        # Store object instances for the system for easy access
        self.fan_system = None
        self.supply_fan = None
        self.relief_fan = None
        self.return_fan = None
        self.heating_supply_fan = None
        self.air_energy_recovery = None
        self.air_economizer = None
        self.heating_system = None
        self.cooling_system = None
        self.preheat_system = None

        self.humidification_type = None

    def __repr__(self):
        return f"System(u_name='{self.u_name}')"

    def create_zonal_systems(self):
        """Create a new system for every zone assigned to this system, starting after the first zone.
        Use the current System object for the first zone assigned to the zonal system"""

        for zone in self.children[1:]:
            # Don't create systems for unconditioned or plenum zones
            if zone.get_inp(BDL_ZoneKeywords.TYPE) in [
                BDL_ZoneTypeOptions.UNCONDITIONED,
                BDL_ZoneTypeOptions.PLENUM,
            ]:
                continue

            sys_id = f"{self.u_name} - {zone.u_name}"
            zone_system = System(self.u_name, self.rmd)
            zone_system.sys_id = sys_id
            zone_system.add_child(zone)
            zone.parent = zone_system
            zone_system.is_derived_system = True
            zone_system.keyword_value_pairs = self.keyword_value_pairs.copy()
            zone_system.populate_data_elements()
            self.rmd.bdl_obj_instances[sys_id] = zone_system

        # Remove zones after processing
        self.children = self.children[:1]

    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader."""
        system_type = self.get_inp(BDL_SystemKeywords.TYPE)

        if system_type == BDL_SystemTypes.SUM:
            self.omit = True
            return

        if system_type in self.zonal_system_types:
            self.is_zonal_system = True
            if not self.is_derived_system:
                self.create_zonal_systems()

        self.update_system_mapping()
        heat_type = HeatingSystem.heat_type_map.get(
            self.get_inp(BDL_SystemKeywords.HEAT_SOURCE)
        )
        cool_type = CoolingSystem.cool_type_map.get(
            self.get_inp(BDL_SystemKeywords.COOL_SOURCE)
        )

        has_heat = heat_type not in [None, HeatingSystemOptions.NONE] or (
            system_type == BDL_SystemTypes.HP
            and self.get_inp(BDL_SystemKeywords.WLHP_CATEGORY)
            in [
                BDL_WLHPCategoryOptions.WATER_LOOP,
                BDL_WLHPCategoryOptions.GROUND_WATER,
                BDL_WLHPCategoryOptions.GROUND_LOOP,
            ]
        )
        has_cool = CoolingSystem.system_cooling_type_map.get(
            self.get_inp(BDL_SystemKeywords.TYPE)
        ) not in [None, CoolingSystemOptions.NONE] or (
            system_type == BDL_SystemTypes.HP
        )
        has_preheat = self.get_inp(BDL_SystemKeywords.PREHEAT_SOURCE) and self.get_inp(
            BDL_SystemKeywords.PREHEAT_SOURCE
        ) not in [None, BDL_SystemHeatingTypes.NONE]
        has_economizer = (
            self.get_inp(BDL_SystemKeywords.OA_CONTROL)
            and self.get_inp(BDL_SystemKeywords.OA_CONTROL)
            != BDL_EconomizerOptions.FIXED
        )
        has_energy_recovery = (
            self.get_inp(BDL_SystemKeywords.RECOVER_EXHAUST)
            and self.get_inp(BDL_SystemKeywords.RECOVER_EXHAUST)
            != BDL_EnergyRecoveryOptions.NO
        )

        self.is_terminal = (
            len(self.children) == 1
            and system_type not in self.reheat_system_types
            and heat_type
            in [
                HeatingSystemOptions.FLUID_LOOP,
                HeatingSystemOptions.NONE,
            ]
            and cool_type
            in [
                CoolingSystemOptions.FLUID_LOOP,
                CoolingSystemOptions.NONE,
            ]
            and not has_preheat
            and not has_economizer
            and not has_energy_recovery
        )

        if self.is_terminal:
            self.omit = True
            return

        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)
        for key in ["Cooling Capacity", "Heating Capacity"]:
            if key in output_data:
                output_data[key] = self.try_convert_units(
                    output_data[key], "kBtu/hr", "Btu/hr"
                )

        self.humidification_type = self.humidification_map.get(
            self.get_inp(BDL_SystemKeywords.HUMIDIFIER_TYPE)
        )

        self.fan_system = FanSystem(self)
        self.fan_system.populate_data_elements(output_data)

        self.populate_fans(output_data)

        if has_cool:
            self.cooling_system = CoolingSystem(self)
            self.cooling_system.populate_data_elements(output_data)
            self.cooling_system.populate_data_group()

        if has_heat:
            self.heating_system = HeatingSystem(self)
            self.heating_system.populate_data_elements(output_data)
            self.heating_system.populate_data_group()

        if has_preheat:
            self.preheat_system = PreheatSystem(self)
            self.preheat_system.populate_data_elements(output_data)
            self.preheat_system.populate_data_group()

        if has_economizer:
            self.air_economizer = AirEconomizer(self)
            self.air_economizer.populate_data_elements()
            self.air_economizer.populate_data_group()
            self.fan_system.maximum_outdoor_airflow = self.supply_fan.design_airflow

        else:
            self.fan_system.maximum_outdoor_airflow = (
                self.fan_system.minimum_outdoor_airflow
            )

        if has_energy_recovery:
            self.air_energy_recovery = AirEnergyRecovery(self)
            self.air_energy_recovery.populate_data_elements()
            self.air_energy_recovery.populate_data_group()
            if self.air_energy_recovery.outdoor_airflow is None:
                self.air_energy_recovery.outdoor_airflow = (
                    self.fan_system.minimum_outdoor_airflow
                )

    def get_output_requests(self):
        """Get the output requests for the system dependent on various system component types."""
        requests = {
            "Outside Air Ratio": (2201005, self.u_name, ""),
            "Cooling Capacity": (2201006, self.u_name, ""),
            "Sensible Heat Ratio": (2201007, self.u_name, ""),
            "Heating Capacity": (2201008, self.u_name, ""),
            "Supply Fan - Airflow": (2201012, self.u_name, ""),
            "Supply Fan - Power": (2201014, self.u_name, ""),
            "Supply Fan - Min Flow Ratio": (2201022, self.u_name, ""),
        }

        return_or_relief = self.get_inp(
            BDL_SystemKeywords.RETURN_STATIC
        ) or self.get_inp(BDL_SystemKeywords.RETURN_KW_FLOW)

        if return_or_relief:
            requests["Return Fan - Airflow"] = (
                2201023,
                self.u_name,
                "",
            )
            requests["Return Fan - Power"] = (
                2201025,
                self.u_name,
                "",
            )

        if self.get_inp(BDL_SystemKeywords.DDS_TYPE) == BDL_DualDuctFanOptions.DUAL_FAN:
            requests["Heating Supply Fan - Airflow"] = (
                2201034,
                self.u_name,
                "",
            )
            requests["Heating Supply Fan - Power"] = (2201036, self.u_name, "")

        if self.is_zonal_system:
            requests["Supply Fan - Power"] = (
                2201047,
                self.u_name,
                self.children[0].u_name,
            )
            requests["Supply Fan - Airflow"] = (
                2201045,
                self.u_name,
                self.children[0].u_name,
            )
            match self.bdl_output_cool_type:
                case BDL_OutputCoolingTypes.CHILLED_WATER:
                    # Design data for Cooling - chilled water - ZONE - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (
                        2203505,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Design data for Cooling - chilled water - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203506,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - chilled water - ZONE - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (
                        2203516,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - chilled water - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203517,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputCoolingTypes.DX_AIR_COOLED:
                    # Design data for Cooling - DX air cooled - ZONE - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (
                        2203557,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Design data for Cooling - DX air cooled - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203558,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - DX air cooled - ZONE - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (
                        2203566,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - DX air cooled - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203567,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputCoolingTypes.DX_WATER_COOLED:
                    # Design data for Cooling - DX water cooled - ZONE - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (
                        2203587,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Design data for Cooling - DX water cooled - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203588,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - DX water cooled - ZONE - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (
                        2203596,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - DX water cooled - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203597,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputCoolingTypes.VRF:
                    # Design data for Cooling - VRF - ZONE - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (
                        2203619,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Design data for Cooling - VRF - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203620,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - VRF - ZONE - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (
                        2203628,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Cooling - VRF - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203629,
                        self.u_name,
                        self.children[0].u_name,
                    )

            match self.bdl_output_heat_type:
                case BDL_OutputHeatingTypes.FURNACE:
                    # Design data for Heating - furnace - ZONE - capacity, btu/hr
                    requests["Design Heating Capacity"] = (
                        2203708,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED:
                    # Design data for Heating - heat pump air cooled - ZONE - capacity, btu/hr
                    requests["Design Heating Capacity"] = (
                        2203784,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Heating - heat pump air cooled - ZONE - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (
                        2203790,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED:
                    # Design data for Heating - heat pump water cooled - ZONE - capacity, btu/hr
                    requests["Design Heating Capacity"] = (
                        2203805,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Heating - heat pump water cooled - ZONE - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (
                        2203811,
                        self.u_name,
                        self.children[0].u_name,
                    )
                case BDL_OutputHeatingTypes.VRF:
                    # Design data for Heating - VRF - ZONE - capacity, btu/hr
                    requests["Design Heating Capacity"] = (
                        2203828,
                        self.u_name,
                        self.children[0].u_name,
                    )
                    # Rated data for Heating - VRF - ZONE - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (
                        2203834,
                        self.u_name,
                        self.children[0].u_name,
                    )

        else:
            match self.bdl_output_cool_type:
                case BDL_OutputCoolingTypes.CHILLED_WATER:
                    # Design data for Cooling - chilled water - SYSTEM - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (2203015, self.u_name, "")
                    # Design data for Cooling - chilled water - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203016, self.u_name, "")
                    # Rated data for Cooling - chilled water - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (2203026, self.u_name, "")
                    # Rated data for Cooling - chilled water - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203027, self.u_name, "")
                case BDL_OutputCoolingTypes.DX_AIR_COOLED:
                    # Design data for Cooling - DX air cooled - SYSTEM - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (2203083, self.u_name, "")
                    # Design data for Cooling - DX air cooled - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203084, self.u_name, "")
                    # Rated data for Cooling - DX air cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (2203092, self.u_name, "")
                    # Rated data for Cooling - DX air cooled - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203093, self.u_name, "")
                case BDL_OutputCoolingTypes.DX_WATER_COOLED:
                    # Design data for Cooling - DX water cooled - SYSTEM - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (2203143, self.u_name, "")
                    # Design data for Cooling - DX water cooled - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203144, self.u_name, "")
                    # Rated data for Cooling - DX water cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (2203152, self.u_name, "")
                    # Rated data for Cooling - DX water cooled - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203153, self.u_name, "")
                case BDL_OutputCoolingTypes.VRF:
                    # Design data for Cooling - VRF - SYSTEM - capacity, btu/hr
                    requests["Design Cooling Capacity"] = (2203207, self.u_name, "")
                    # Design data for Cooling - VRF - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203208, self.u_name, "")
                    # Rated data for Cooling - VRF - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling Capacity"] = (2203216, self.u_name, "")
                    # Rated data for Cooling - VRF - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203217, self.u_name, "")

            match self.bdl_output_heat_type:
                case BDL_OutputHeatingTypes.FURNACE:
                    requests["Design Heating Capacity"] = (2203296, self.u_name, "")
                case BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED:
                    # Design data for Heating - heat pump air cooled - SYSTEM - capacity, btu/hr
                    requests["Design Heating Capacity"] = (2203372, self.u_name, "")
                    # Rated data for Heating - heat pump air cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (2203378, self.u_name, "")
                case BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED:
                    # Design data for Heating - heat pump water cooled - SYSTEM - capacity, btu/hr
                    requests["Design Heating Capacity"] = (2203414, self.u_name, "")
                    # Rated data for Heating - heat pump water cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (2203420, self.u_name, "")
                case BDL_OutputHeatingTypes.VRF:
                    # Design data for Heating - VRF - SYSTEM - capacity, btu/hr
                    requests["Design Heating Capacity"] = (2203460, self.u_name, "")
                    # Rated data for Heating - VRF - SYSTEM - capacity, btu/hr
                    requests["Rated Heating Capacity"] = (2203466, self.u_name, "")

            match self.preheat_system_type:
                case HeatingSystemOptions.FLUID_LOOP:
                    # Design Preheat - hot water - SYSTEM - capacity, btu/hr
                    requests["Design Preheat Capacity"] = (
                        2203269,
                        self.u_name,
                        "",
                    )
                case HeatingSystemOptions.ELECTRIC_RESISTANCE:
                    # Design Preheat - electric - SYSTEM - capacity, btu/hr
                    requests["Design Preheat Capacity"] = (
                        2203346,
                        self.u_name,
                        "",
                    )
                case HeatingSystemOptions.FURNACE:
                    # Design Preheat - furnace - SYSTEM - capacity, btu/hr
                    requests["Design Preheat Capacity"] = (
                        2203311,
                        self.u_name,
                        "",
                    )

        return requests

    def populate_data_group(self):
        """
        Populate schema structure for system object.
        System configurations that typically are at the zone and include a compressor (such as packaged terminal air
        conditioning, packaged terminal heat pumps, window air conditioning units, and water loop heat pumps) should be
        reported in the schema using HeatingSystem and CoolingSystem. Systems that include gas or electric furnaces
        should be reported in the schema using HeatingSystem. System configurations that are at the zone and only
        include fans and coils (such as four-pipe fan coil, two-pipe fan coil, radiant systems, baseboards, and chilled
        beams) should be reported in the schema using Terminal with the chilled water and hot water systems described
        in the cooling_source and heating_source data elements (and any other relevant Terminal Data elements).
        Evaporative cooling systems should be described in CoolingSystem. Passive diffusers with no coil or fan should
        be described in Terminal. One FanSystem for each HeatingVentilatingAirConditioningSystem so if a direct outdoor
        air system is used a second Zone Terminal should be specified with a separate
        HeatingVentilatingAirConditioningSystem.
        """
        if self.omit:
            return

        else:
            # Set the default building segment for systems that have no zones directly assigned (DOAS)
            if self.parent_building_segment is None:
                self.parent_building_segment = self.rmd.default_building_segment

            for attr in dir(self):
                value = getattr(self, attr, None)

                if value is None:
                    continue

            if self.is_derived_system:
                self.system_data_structure["id"] = self.sys_id
            else:
                self.system_data_structure["id"] = self.u_name

            self.fan_system.populate_data_group()

            self.system_data_structure.update(
                {
                    "fan_system": self.fan_system.data_structure,
                }
            )

            for attr in ["heating_system", "cooling_system", "preheat_system"]:
                subsystem = getattr(self, attr)
                if subsystem:
                    self.system_data_structure[attr] = subsystem.data_structure

            for attr in ["humidification_type"]:
                value = getattr(self, attr)
                if value is not None:
                    self.system_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert system data structure into the rpd data structure."""
        if self.omit:
            return
        self.parent_building_segment.hvac_systems.append(self.system_data_structure)

    def update_system_mapping(self):
        """Update various system mapping based on the system component types."""
        CoolingSystem.system_cooling_type_map.update(
            {
                BDL_SystemTypes.PIU: CoolingSystem.cool_type_map.get(
                    self.get_inp(BDL_SystemKeywords.COOL_SOURCE)
                ),
                BDL_SystemTypes.DOAS: CoolingSystem.cool_type_map.get(
                    self.get_inp(BDL_SystemKeywords.COOL_SOURCE)
                ),
            }
        )
        HeatingSystem.BDL_output_heat_type_map.update(
            {
                BDL_SystemHeatingTypes.HEAT_PUMP: self.BDL_condenser_output_heat_type_map.get(
                    self.get_inp(BDL_SystemKeywords.CONDENSER_TYPE)
                )
            }
        )

        self.bdl_output_heat_type = HeatingSystem.BDL_output_heat_type_map.get(
            self.get_inp(BDL_SystemKeywords.HEAT_SOURCE)
        )
        self.bdl_output_cool_type = self.BDL_condenser_output_cool_type_map.get(
            self.get_inp(BDL_SystemKeywords.CONDENSER_TYPE)
        )
        self.preheat_system_type = PreheatSystem.heat_type_map.get(
            self.get_inp(BDL_SystemKeywords.PREHEAT_SOURCE)
        )

        HeatingSystem.BDL_output_system_heating_type_map.update(
            {
                BDL_SystemTypes.PTAC: self.bdl_output_heat_type,
                BDL_SystemTypes.PSZ: self.bdl_output_heat_type,
                BDL_SystemTypes.PMZS: self.bdl_output_heat_type,
                BDL_SystemTypes.PVAVS: self.bdl_output_heat_type,
                BDL_SystemTypes.PVVT: self.bdl_output_heat_type,
                BDL_SystemTypes.SZRH: self.bdl_output_heat_type,
                BDL_SystemTypes.VAVS: self.bdl_output_heat_type,
                BDL_SystemTypes.RHFS: self.bdl_output_heat_type,
                BDL_SystemTypes.DDS: self.bdl_output_heat_type,
                BDL_SystemTypes.MZS: self.bdl_output_heat_type,
                BDL_SystemTypes.PIU: self.bdl_output_heat_type,
                BDL_SystemTypes.FC: self.bdl_output_heat_type,
                BDL_SystemTypes.IU: self.bdl_output_heat_type,
                BDL_SystemTypes.UVT: self.bdl_output_heat_type,
                BDL_SystemTypes.UHT: self.bdl_output_heat_type,
                BDL_SystemTypes.RESYS2: self.bdl_output_heat_type,
                BDL_SystemTypes.CBVAV: self.bdl_output_heat_type,
                BDL_SystemTypes.DOAS: self.bdl_output_heat_type,
            }
        )
        CoolingSystem.BDL_output_system_cooling_type_map.update(
            {
                BDL_SystemTypes.PIU: self.bdl_output_cool_type,
                BDL_SystemTypes.DOAS: self.bdl_output_cool_type,
                BDL_SystemTypes.PSZ: self.bdl_output_cool_type,
                BDL_SystemTypes.PMZS: self.bdl_output_cool_type,
                BDL_SystemTypes.PVAVS: self.bdl_output_cool_type,
                BDL_SystemTypes.PVVT: self.bdl_output_cool_type,
                BDL_SystemTypes.RESYS2: self.bdl_output_cool_type,
            }
        )

        self.bdl_output_heat_type = (
            HeatingSystem.BDL_output_system_heating_type_map.get(
                self.get_inp(BDL_SystemKeywords.TYPE)
            )
        )
        self.bdl_output_cool_type = (
            CoolingSystem.BDL_output_system_cooling_type_map.get(
                self.get_inp(BDL_SystemKeywords.TYPE)
            )
        )

    def get_loop_energy_source(self, loop):
        """Get the energy source type for the loop. Used to populate the energy_source_type."""
        energy_source_set = set()
        for boiler_name in self.rmd.boiler_names:
            boiler = self.get_obj(boiler_name)
            if boiler.loop == loop.u_name:
                energy_source_set.add(boiler.energy_source_type)

        for steam_meter_name in self.rmd.steam_meter_names:
            steam_meter = self.get_obj(steam_meter_name)
            if steam_meter.loop == loop.u_name:
                energy_source_set.add(steam_meter.energy_source_type)

        for chiller_name in self.rmd.chiller_names:
            chiller = self.get_obj(chiller_name)
            if chiller.heat_recovery_loop == loop.u_name:
                energy_source_set.add(EnergySourceOptions.ELECTRICITY)

        for domestic_water_heater_name in self.rmd.domestic_water_heater_names:
            domestic_water_heater = self.get_obj(domestic_water_heater_name)
            if domestic_water_heater.hot_water_loop == loop.u_name:
                energy_source_set.add(domestic_water_heater.heater_fuel_type)

        if len(energy_source_set) == 1:
            return energy_source_set.pop()
        else:
            return EnergySourceOptions.OTHER

    def get_furnace_energy_source(self):
        """Get the energy source type for the furnace. Used to populate the energy_source_type."""
        heat_fuel_meter = self.get_obj(self.get_inp(BDL_SystemKeywords.HEAT_FUEL_METER))
        if heat_fuel_meter:
            return heat_fuel_meter.fuel_type
        else:
            master_meters = self.get_obj(self.rmd.master_meters)
            if master_meters:
                heat_fuel_meter = self.get_obj(
                    master_meters.get_inp(BDL_MasterMeterKeywords.HEAT_FUEL_METER)
                )
                if heat_fuel_meter:
                    return heat_fuel_meter.fuel_type

    def populate_fans(self, output_data):
        # There is always a supply fan for a fan system in eQUEST, so it is always populated
        self.supply_fan = Fan(self)
        self.supply_fan.name = self.u_name + " SupplyFan"
        self.supply_fan.design_airflow = output_data.get("Supply Fan - Airflow")
        self.supply_fan.design_electric_power = output_data.get("Supply Fan - Power")
        if self.get_inp(BDL_SystemKeywords.SUPPLY_FLOW) is not None:
            self.supply_fan.is_airflow_calculated = False
        if self.supply_fan.is_airflow_calculated is None:
            self.supply_fan.is_airflow_calculated = (
                # If any zone served by the system has assigned flow rates, the fan is not sized based on design day
                not any(
                    child_zone.get_inp(BDL_ZoneKeywords.ASSIGNED_FLOW)
                    or child_zone.get_inp(BDL_ZoneKeywords.HASSIGNED_FLOW)
                    or child_zone.get_inp(BDL_ZoneKeywords.FLOW_AREA)
                    or child_zone.get_inp(BDL_ZoneKeywords.HFLOW_AREA)
                    or child_zone.get_inp(BDL_ZoneKeywords.AIR_CHANGES_HR)
                    or child_zone.get_inp(BDL_ZoneKeywords.HAIR_CHANGES_HR)
                    or child_zone.get_inp(BDL_ZoneKeywords.MIN_FLOW_AREA)
                    or child_zone.get_inp(BDL_ZoneKeywords.HMIN_FLOW_AREA)
                    for child_zone in self.children
                )
            )
        self.supply_fan.specification_method = (
            FanSpecificationMethodOptions.DETAILED
            if self.get_inp(BDL_SystemKeywords.SUPPLY_STATIC) is not None
            else FanSpecificationMethodOptions.SIMPLE
        )
        self.supply_fan.design_pressure_rise = self.try_float(
            self.get_inp(BDL_SystemKeywords.SUPPLY_STATIC)
        )
        self.supply_fan.motor_efficiency = self.try_float(
            self.get_inp(BDL_SystemKeywords.SUPPLY_MTR_EFF)
        )
        supply_mech_eff = self.try_float(
            self.get_inp(BDL_SystemKeywords.SUPPLY_MECH_EFF)
        )
        if self.supply_fan.motor_efficiency and supply_mech_eff:
            self.supply_fan.total_efficiency = (
                self.supply_fan.motor_efficiency * supply_mech_eff
            )
        if not self.fan_system.fan_control == FanSystemSupplyFanControlOptions.CONSTANT:
            self.supply_fan.populate_operating_points("Supply")

        # Determine if there is either a return or relief fan
        return_or_relief = (
            self.get_inp(BDL_SystemKeywords.RETURN_STATIC) is not None
            or self.get_inp(BDL_SystemKeywords.RETURN_KW_FLOW) is not None
        )
        # If there is a return or relief fan and its location is set to RELIEF
        if (
            return_or_relief
            and self.get_inp(BDL_SystemKeywords.RETURN_FAN_LOC)
            == BDL_ReturnFanOptions.RELIEF
        ):
            self.relief_fan = Fan(self)
            self.relief_fan.name = self.u_name + " ReliefFan"
            self.relief_fan.design_airflow = output_data.get(
                "Return Fan - Airflow", None
            )
            self.relief_fan.design_electric_power = output_data.get(
                "Return Fan - Power", None
            )
            if self.get_inp(BDL_SystemKeywords.RETURN_FLOW) is not None:
                self.relief_fan.is_airflow_calculated = False
            if self.relief_fan.is_airflow_calculated is None:
                self.relief_fan.is_airflow_calculated = (
                    self.supply_fan.is_airflow_calculated
                )
            self.relief_fan.specification_method = (
                FanSpecificationMethodOptions.DETAILED
                if self.get_inp(BDL_SystemKeywords.RETURN_STATIC) is not None
                else FanSpecificationMethodOptions.SIMPLE
            )
            self.relief_fan.design_pressure_rise = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_STATIC)
            )
            self.relief_fan.motor_efficiency = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_MTR_EFF)
            )
            return_mech_eff = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_MECH_EFF)
            )
            if self.relief_fan.motor_efficiency and return_mech_eff:
                self.relief_fan.total_efficiency = (
                    self.relief_fan.motor_efficiency * return_mech_eff
                )
            if (
                not self.fan_system.fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
            ):
                self.relief_fan.populate_operating_points("Relief")

        # If the return or relief fan location is not set to RELIEF, it is categorized as a return fan
        elif return_or_relief:
            self.return_fan = Fan(self)
            self.return_fan.name = self.u_name + " ReturnFan"
            self.return_fan.design_airflow = output_data.get(
                "Return Fan - Airflow", None
            )
            self.return_fan.design_electric_power = output_data.get(
                "Return Fan - Power"
            )
            if self.get_inp(BDL_SystemKeywords.RETURN_FLOW) is not None:
                self.return_fan.is_airflow_calculated = False
            if self.return_fan.is_airflow_calculated is None:
                self.return_fan.is_airflow_calculated = (
                    self.supply_fan.is_airflow_calculated
                )

            self.return_fan.specification_method = (
                FanSpecificationMethodOptions.DETAILED
                if self.get_inp(BDL_SystemKeywords.RETURN_STATIC) is not None
                else FanSpecificationMethodOptions.SIMPLE
            )
            self.return_fan.design_pressure_rise = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_STATIC)
            )
            self.return_fan.motor_efficiency = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_MTR_EFF)
            )
            return_mech_eff = self.try_float(
                self.get_inp(BDL_SystemKeywords.RETURN_MECH_EFF)
            )
            if self.return_fan.motor_efficiency and return_mech_eff:
                self.return_fan.total_efficiency = (
                    self.return_fan.motor_efficiency * return_mech_eff
                )
            if (
                not self.fan_system.fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
            ):
                self.return_fan.populate_operating_points("Return")

        # If the system is a dual duct system and the dual duct fan option is dual fan, there is a heating supply fan
        if self.get_inp(BDL_SystemKeywords.DDS_TYPE) == BDL_DualDuctFanOptions.DUAL_FAN:
            self.heating_supply_fan = Fan(self)
            self.heating_supply_fan.name = self.u_name + " HeatingSupplyFan"
            self.heating_supply_fan.design_airflow = output_data.get(
                "Heating Supply Fan - Airflow"
            )
            self.heating_supply_fan.design_electric_power = output_data.get(
                "Heating Supply Fan - Power"
            )
            if self.get_inp(BDL_SystemKeywords.HSUPPLY_FLOW) is not None:
                self.heating_supply_fan.is_airflow_calculated = False
            if self.heating_supply_fan.is_airflow_calculated is None:
                self.heating_supply_fan.is_airflow_calculated = (
                    # If any zone served by the system has assigned flow rates, the fan is not sized based on design day
                    any(
                        child_zone.get_inp(BDL_ZoneKeywords.HASSIGNED_FLOW)
                        or child_zone.get_inp(BDL_ZoneKeywords.HFLOW_AREA)
                        or child_zone.get_inp(BDL_ZoneKeywords.HAIR_CHANGES_HR)
                        or child_zone.get_inp(BDL_ZoneKeywords.HMIN_FLOW_AREA)
                        for child_zone in self.children
                    )
                )
            self.heating_supply_fan.specification_method = (
                FanSpecificationMethodOptions.DETAILED
                if self.get_inp(BDL_SystemKeywords.HSUPPLY_STATIC) is not None
                else FanSpecificationMethodOptions.SIMPLE
            )
            self.heating_supply_fan.design_pressure_rise = self.try_float(
                self.get_inp(BDL_SystemKeywords.HSUPPLY_STATIC)
            )
            self.heating_supply_fan.motor_efficiency = self.try_float(
                self.get_inp(BDL_SystemKeywords.HSUPPLY_MTR_EFF)
            )
            hsupply_mech_eff = self.try_float(
                self.get_inp(BDL_SystemKeywords.HSUPPLY_MECH_EFF)
            )
            if self.heating_supply_fan.motor_efficiency and hsupply_mech_eff:
                self.heating_supply_fan.total_efficiency = (
                    self.heating_supply_fan.motor_efficiency * hsupply_mech_eff
                )
            if (
                not self.fan_system.fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
            ):
                self.heating_supply_fan.populate_operating_points("HeatingSupply")


class FanSystem:

    supply_fan_control_map = {
        BDL_SystemFanControlOptions.CONSTANT_VOLUME: FanSystemSupplyFanControlOptions.CONSTANT,
        BDL_SystemFanControlOptions.SPEED: FanSystemSupplyFanControlOptions.VARIABLE_SPEED_DRIVE,
        #  "": FanSystemSupplyFanControlOptions.MULTISPEED",  no eQUEST options map to MULTISPEED in DOE2.3
        BDL_SystemFanControlOptions.INLET: FanSystemSupplyFanControlOptions.INLET_VANE,
        BDL_SystemFanControlOptions.DISCHARGE: FanSystemSupplyFanControlOptions.DISCHARGE_DAMPER,
        BDL_SystemFanControlOptions.FAN_EIR_FPLR: FanSystemSupplyFanControlOptions.VARIABLE_SPEED_DRIVE,
    }
    occupied_fan_operation_map = {
        BDL_IndoorFanModeOptions.CONTINUOUS: FanSystemOperationOptions.CONTINUOUS,
        BDL_IndoorFanModeOptions.INTERMITTENT: FanSystemOperationOptions.CYCLING,
    }
    unoccupied_fan_operation_map = {
        BDL_NightCycleControlOptions.CYCLE_ON_ANY: FanSystemOperationOptions.CYCLING,
        BDL_NightCycleControlOptions.CYCLE_ON_FIRST: FanSystemOperationOptions.CYCLING,
        BDL_NightCycleControlOptions.STAY_OFF: FanSystemOperationOptions.KEEP_OFF,
        BDL_NightCycleControlOptions.ZONE_FANS_ONLY: FanSystemOperationOptions.OTHER,
    }
    dcv_map = {
        BDL_SystemMinimumOutdoorAirControlOptions.FRAC_OF_DESIGN_FLOW: DemandControlVentilationControlOptions.NONE,
        BDL_SystemMinimumOutdoorAirControlOptions.FRAC_OF_HOURLY_FLOW: DemandControlVentilationControlOptions.NONE,
        BDL_SystemMinimumOutdoorAirControlOptions.DCV_RETURN_SENSOR: DemandControlVentilationControlOptions.CO2_RETURN_AIR,
        BDL_SystemMinimumOutdoorAirControlOptions.DCV_ZONE_SENSORS: DemandControlVentilationControlOptions.CO2_ZONE,
    }
    single_zone_system_types = [
        BDL_SystemTypes.PSZ,
        BDL_SystemTypes.SZRH,
        BDL_SystemTypes.SZCI,
        BDL_SystemTypes.PVVT,
        BDL_SystemTypes.FC,
        BDL_SystemTypes.HP,
        BDL_SystemTypes.UHT,
        BDL_SystemTypes.UVT,
        BDL_SystemTypes.PTAC,
        BDL_SystemTypes.RESYS,
        BDL_SystemTypes.RESYS2,
    ]
    single_duct_system_types = [
        BDL_SystemTypes.PVAVS,
        BDL_SystemTypes.VAVS,
        BDL_SystemTypes.CBVAV,
        BDL_SystemTypes.RHFS,
        BDL_SystemTypes.PIU,
        BDL_SystemTypes.IU,
    ]
    multi_duct_system_types = [
        BDL_SystemTypes.MZS,
        BDL_SystemTypes.PMZS,
        BDL_SystemTypes.DDS,
    ]

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.supply_fans = []
        self.return_fans = []
        self.exhaust_fans = []
        self.relief_fans = []
        self.air_economizer = {}
        self.air_energy_recovery = {}

        self.temperature_control = None
        self.operation_during_occupied = None
        self.operation_during_unoccupied = None
        self.has_lockout_central_heat_during_unoccupied = None
        self.fan_control = None
        self.reset_differential_temperature = None
        self.supply_air_temperature_reset_load_fraction = None
        self.supply_air_temperature_reset_schedule = None
        self.fan_volume_reset_type = None
        self.fan_volume_reset_fraction = None
        self.operating_schedule = None
        self.minimum_airflow = None
        self.minimum_outdoor_airflow = None
        self.maximum_outdoor_airflow = None
        self.air_filter_merv_rating = None
        self.has_fully_ducted_return = None
        self.demand_control_ventilation_control = None

    def populate_data_elements(self, output_data):
        self.name = self.parent_system.u_name + " FanSys"
        self.has_fully_ducted_return = (
            self.parent_system.get_inp(BDL_SystemKeywords.RETURN_AIR_PATH)
            == BDL_ReturnAirPathOptions.DUCT
        )
        self.fan_control = self.supply_fan_control_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.FAN_CONTROL)
        )
        self.temperature_control = self.get_temperature_control()
        self.operating_schedule = self.parent_system.get_inp(
            BDL_SystemKeywords.FAN_SCHEDULE
        )
        self.demand_control_ventilation_control = self.dcv_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.MIN_OA_METHOD)
        )
        cool_control = self.parent_system.get_inp(BDL_SystemKeywords.COOL_CONTROL)
        min_reset_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOL_MIN_RESET_T)
        )
        max_reset_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOL_MAX_RESET_T)
        )
        if (
            cool_control == BDL_CoolControlOptions.WARMEST
            and min_reset_t is not None
            and max_reset_t is not None
        ):
            self.reset_differential_temperature = max_reset_t - min_reset_t
        supply_fan_airflow = output_data.get("Supply Fan - Airflow")
        supply_min_flow_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.MIN_FLOW_RATIO)
        )
        supply_min_fan_ratio = output_data.get("Supply Fan - Min Flow Ratio")
        oa_ratio = output_data.get("Outside Air Ratio")
        if oa_ratio is not None and supply_fan_airflow is not None:
            self.minimum_outdoor_airflow = oa_ratio * supply_fan_airflow
        if supply_min_fan_ratio is not None and supply_fan_airflow is not None:
            self.minimum_airflow = supply_min_fan_ratio * supply_fan_airflow
        # Set fan control of systems that have a min flow ratio of 1
        if supply_min_flow_ratio == 1:
            self.fan_control = FanSystemSupplyFanControlOptions.CONSTANT
        # Override fan control of systems that have CONSTANT_VOLUME fans with a minimum flow ratio less than 1
        elif (
            supply_min_fan_ratio is not None
            and supply_min_fan_ratio < 1
            and self.fan_control == FanSystemSupplyFanControlOptions.CONSTANT
        ):
            self.fan_control = FanSystemSupplyFanControlOptions.DISCHARGE_DAMPER
        self.operation_during_unoccupied = self.unoccupied_fan_operation_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.NIGHT_CYCLE_CTRL)
        )
        self.operation_during_occupied = self.populate_fan_operation_during_occupied()

    def populate_data_group(self):
        self.parent_system.supply_fan.populate_data_group()
        if self.parent_system.relief_fan:
            self.parent_system.relief_fan.populate_data_group()
        if self.parent_system.return_fan:
            self.parent_system.return_fan.populate_data_group()
        if self.parent_system.heating_supply_fan:
            self.parent_system.heating_supply_fan.populate_data_group()

        self.data_structure.update(
            {
                "id": self.name,
                "supply_fans": [self.parent_system.supply_fan.data_structure],
            }
        )
        if self.parent_system.heating_supply_fan:
            self.data_structure["supply_fans"].append(
                self.parent_system.heating_supply_fan.data_structure
            )
        if self.parent_system.return_fan:
            self.data_structure["return_fans"] = [
                self.parent_system.return_fan.data_structure
            ]
        if self.parent_system.relief_fan:
            self.data_structure["relief_fans"] = [
                self.parent_system.relief_fan.data_structure
            ]
        if self.parent_system.air_energy_recovery:
            self.data_structure["air_energy_recovery"] = (
                self.parent_system.air_energy_recovery.data_structure
            )
        if self.parent_system.air_economizer:
            self.data_structure["air_economizer"] = (
                self.parent_system.air_economizer.data_structure
            )

        fan_system_data_elements = [
            "reporting_name",
            "notes",
            "temperature_control",
            "operation_during_occupied",
            "operation_during_unoccupied",
            "has_lockout_central_heat_during_unoccupied",
            "fan_control",
            "reset_differential_temperature",
            "supply_air_temperature_reset_load_fraction",
            "supply_air_temperature_reset_schedule",
            "fan_volume_reset_type",
            "fan_volume_reset_fraction",
            "operating_schedule",
            "minimum_airflow",
            "minimum_outdoor_airflow",
            "maximum_outdoor_airflow",
            "air_filter_merv_rating",
            "has_fully_ducted_return",
            "demand_control_ventilation_control",
        ]
        for attr in fan_system_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def get_temperature_control(self):
        system_type = self.parent_system.get_inp(BDL_SystemKeywords.TYPE)
        cool_control = self.parent_system.get_inp(BDL_SystemKeywords.COOL_CONTROL)
        cool_set_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOL_SET_T)
        )
        cool_max_reset_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOL_MAX_RESET_T)
        )
        heat_control = self.parent_system.get_inp(BDL_SystemKeywords.HEAT_CONTROL)
        heat_set_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.HEAT_SET_T)
        )
        heat_max_reset_t = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.HEAT_MAX_RESET_T)
        )
        min_flow_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.MIN_FLOW_RATIO)
        )

        if system_type in self.multi_duct_system_types:
            return FanSystemTemperatureControlOptions.OTHER

        elif system_type in self.single_duct_system_types:

            if (
                cool_control == BDL_CoolControlOptions.CONSTANT
                and heat_control == BDL_HeatControlOptions.CONSTANT
            ):
                if heat_set_t and cool_set_t and heat_set_t >= cool_set_t:
                    return FanSystemTemperatureControlOptions.CONSTANT
                else:
                    return FanSystemTemperatureControlOptions.OTHER

            elif cool_control == BDL_CoolControlOptions.WARMEST:
                if heat_set_t and cool_max_reset_t and heat_set_t >= cool_max_reset_t:
                    return FanSystemTemperatureControlOptions.ZONE_RESET
                elif (
                    heat_max_reset_t
                    and cool_max_reset_t
                    and heat_max_reset_t >= cool_max_reset_t
                ):
                    return FanSystemTemperatureControlOptions.ZONE_RESET
                else:
                    return FanSystemTemperatureControlOptions.OTHER

            elif cool_control == BDL_CoolControlOptions.SCHEDULED:
                return FanSystemTemperatureControlOptions.SCHEDULED

            elif cool_control == BDL_CoolControlOptions.RESET:
                return FanSystemTemperatureControlOptions.OUTDOOR_AIR_RESET

        elif system_type in self.single_zone_system_types:
            if min_flow_ratio and min_flow_ratio < 1:
                if cool_set_t and heat_set_t and cool_set_t == heat_set_t:
                    return FanSystemTemperatureControlOptions.CONSTANT
                else:
                    return FanSystemTemperatureControlOptions.OTHER
            else:
                return FanSystemTemperatureControlOptions.ZONE_RESET

        elif system_type == BDL_SystemTypes.DOAS:
            pass

    def populate_fan_operation_during_occupied(self):
        fan_sch = self.parent_system.get_obj(
            self.parent_system.get_inp(BDL_SystemKeywords.FAN_SCHEDULE)
        )

        if (
            self.parent_system.get_inp(BDL_SystemKeywords.TYPE)
            == BDL_SystemTypes.RESVVT
        ):
            return FanSystemOperationOptions.CYCLING

        elif (
            self.parent_system.get_inp(BDL_SystemKeywords.TYPE) == BDL_SystemTypes.DOAS
        ):
            if not fan_sch:
                return FanSystemOperationOptions.CONTINUOUS
            elif all(value == -999 for value in fan_sch.hourly_values):
                return FanSystemOperationOptions.CONTINUOUS

            doas_occ_sch = self.get_doas_occ_sch()
            all_occupied_off = True
            all_occupied_on = True
            for i, hour in enumerate(doas_occ_sch):
                if hour == 1:
                    value = fan_sch.hourly_values[i]
                    if value not in [0, -1]:
                        all_occupied_off = False
                    if value not in [1, -999]:
                        all_occupied_on = False
            if all_occupied_off:
                return FanSystemOperationOptions.KEEP_OFF
            if all_occupied_on:
                return FanSystemOperationOptions.CONTINUOUS
            return FanSystemOperationOptions.OTHER

        elif self.parent_system.get_inp(BDL_SystemKeywords.TYPE) in [
            BDL_SystemTypes.PTAC,
            BDL_SystemTypes.HP,
            BDL_SystemTypes.UVT,
            BDL_SystemTypes.UHT,
            BDL_SystemTypes.PSZ,
            BDL_SystemTypes.PVVT,
            BDL_SystemTypes.RESYS2,
            BDL_SystemTypes.EVAP_COOL,
            BDL_SystemTypes.FC,
            BDL_SystemTypes.SZRH,
        ]:
            if not fan_sch:
                return self.occupied_fan_operation_map.get(
                    self.parent_system.get_inp(BDL_SystemKeywords.INDOOR_FAN_MODE)
                )

            has_one = False
            has_neg_999 = False
            is_all_0 = True
            is_all_1 = True
            for value in fan_sch.hourly_values:
                if is_all_0 and value != 0:
                    is_all_0 = False
                if is_all_1 and value != 1:
                    is_all_1 = False
                if not has_one and value == 1:
                    has_one = True
                elif not has_neg_999 and value == -999:
                    has_neg_999 = True

            # Handle special case where all fan schedule values are 0 so unoccupied/occupied cannot be distinguished
            if is_all_0:
                return self.unoccupied_fan_operation_map.get(
                    self.parent_system.get_inp(BDL_SystemKeywords.NIGHT_CYCLE_CTRL)
                )
            if is_all_1:
                self.operation_during_unoccupied = self.occupied_fan_operation_map.get(
                    self.parent_system.get_inp(BDL_SystemKeywords.INDOOR_FAN_MODE)
                )

            mixed_operation = has_one and has_neg_999
            if mixed_operation:
                return FanSystemOperationOptions.OTHER
            if has_one:  # and not mixed_operation implied to reach here
                return self.occupied_fan_operation_map.get(
                    self.parent_system.get_inp(BDL_SystemKeywords.INDOOR_FAN_MODE)
                )
            if has_neg_999:  # and not mixed_operation implied to reach here
                return FanSystemOperationOptions.CYCLING

        else:
            if fan_sch:
                # Handle special case where all fan schedule values are 0 so unoccupied/occupied cannot be distinguished
                if all(value == 0 for value in fan_sch.hourly_values):
                    return self.unoccupied_fan_operation_map.get(
                        self.parent_system.get_inp(BDL_SystemKeywords.NIGHT_CYCLE_CTRL)
                    )
                if all(value == 1 for value in fan_sch.hourly_values):
                    self.operation_during_unoccupied = (
                        FanSystemOperationOptions.CONTINUOUS
                    )

                if any(value == -999 for value in fan_sch.hourly_values):
                    # TODO raise this error in a window of the GUI
                    raise ValueError(
                        f"""Fan schedule {fan_sch.u_name} for system {self.parent_system.u_name} is not allowed to have -999 values. These
                        flags are not accurately supported by DOE 2.3 (see help text Volume 2: Dictionary > HVAC Components 
                        > SYSTEM > Airside Control > Fan Availability)"""
                    )

            return (
                FanSystemOperationOptions.CONTINUOUS
            )  # if there is no fan schedule or the fan schedule has 1s

    def get_doas_occ_sch(self):
        systems_served = [
            obj_inst
            for obj_inst in list(
                map(self.parent_system.get_obj, self.parent_system.rmd.system_names)
            )
            if obj_inst.get_inp(BDL_SystemKeywords.DOA_SYSTEM)
            == self.parent_system.u_name
        ]
        system_fan_schedules = {
            schedule
            for system in systems_served
            for schedule in [
                self.parent_system.get_obj(
                    system.get_inp(BDL_SystemKeywords.FAN_SCHEDULE)
                )
            ]
            if schedule is not None
        }
        occupied_hours = [
            1 if any(hour == 1 for hour in hours) else 0
            for hours in zip(
                *(schedule.hourly_values for schedule in system_fan_schedules)
            )
        ]
        return occupied_hours


class Fan:
    fan_power_curves = {
        BDL_SystemFanControlOptions.SPEED: [
            0.00153028,
            0.00520806,
            1.1086242,
            -0.11635563,
        ],
        BDL_SystemFanControlOptions.INLET: [
            0.35071223,
            0.30805350,
            -0.5413736,
            0.87198823,
        ],
        BDL_SystemFanControlOptions.DISCHARGE: [
            0.37073425,
            0.97250253,
            -0.3424076,
            0.0,
        ],
        BDL_SystemFanControlOptions.DEFAULT_FAN_CTRL: [
            0.37073425,
            0.97250253,
            -0.3424076,
            0.0,
        ],
        BDL_SystemFanControlOptions.CYCLING: [0.0, 1.0, 0.0, 0.0],
    }

    def __init__(self, parent=None):
        self.parent = parent
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.design_airflow = None
        self.is_airflow_calculated = None
        self.specification_method = None
        self.design_electric_power = None
        self.design_pressure_rise = None
        self.motor_nameplate_power = None
        self.shaft_power = None
        self.total_efficiency = None
        self.motor_efficiency = None
        self.motor_heat_to_airflow_fraction = None
        self.motor_heat_to_zone_fraction = None
        self.motor_location_zone = None
        self.status_type = None
        self.operating_points = []

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        if self.operating_points:
            self.data_structure["operating_points"] = self.operating_points

        fan_data_elements = [
            "reporting_name",
            "notes",
            "design_airflow",
            "is_airflow_calculated",
            "specification_method",
            "design_electric_power",
            "design_pressure_rise",
            "motor_nameplate_power",
            "shaft_power",
            "total_efficiency",
            "motor_efficiency",
            "motor_heat_to_airflow_fraction",
            "motor_heat_to_zone_fraction",
            "motor_location_zone",
            "status_type",
        ]

        for attr in fan_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def populate_operating_points(self, fan_type):
        if fan_type not in ["Supply", "Return", "Relief", "HeatingSupply", "Terminal"]:
            raise ValueError(
                f"Invalid fan type: {fan_type}. Expected 'Supply', 'Return', 'Relief', or 'HeatingSupply'."
            )

        if fan_type == "Supply":
            fan_control_method = self.parent.get_inp(BDL_SystemKeywords.FAN_CONTROL)
            fan_placement = self.parent.get_inp(BDL_SystemKeywords.FAN_PLACEMENT)
            if not fan_control_method == BDL_SystemFanControlOptions.FAN_EIR_FPLR:
                curve_coeffs = self.fan_power_curves.get(fan_control_method)
            else:
                curve = self.parent.get_obj(
                    self.parent.get_inp(BDL_SystemKeywords.FAN_EIR_FPLR)
                )
                curve_coeffs = curve.coefficients

        elif fan_type == "Terminal":
            fan_control_method = self.parent.get_inp(BDL_ZoneKeywords.ZONE_FAN_CTRL)
            fan_placement = None
            if fan_control_method == BDL_ZoneFanControlOptions.CONSTANT_VOLUME:
                curve_coeffs = self.fan_power_curves.get(
                    BDL_SystemFanControlOptions.CYCLING
                )
            elif fan_control_method == BDL_ZoneFanControlOptions.VARIABLE_VOLUME:
                curve = self.parent.get_obj(
                    self.parent.get_inp(BDL_ZoneKeywords.ZONE_FAN_KW_FPLR)
                )
                curve_coeffs = curve.coefficients
            else:
                curve_coeffs = None

        elif fan_type in ["Return", "Relief"]:
            fan_control_method = self.parent.get_inp(
                BDL_SystemKeywords.RETURN_FAN_CONTR
            )
            fan_placement = self.parent.get_inp(BDL_SystemKeywords.RETURN_FAN_LOC)
            if not fan_control_method == BDL_SystemFanControlOptions.FAN_EIR_FPLR:
                curve_coeffs = self.fan_power_curves.get(fan_control_method)
            else:
                curve = self.parent.get_obj(
                    self.parent.get_inp(BDL_SystemKeywords.RETURN_EIR_FPLR)
                )
                curve_coeffs = curve.coefficients

        else:  # fan_type == "HeatingSupply":
            fan_control_method = self.parent.get_inp(BDL_SystemKeywords.HFAN_CONTROL)
            fan_placement = self.parent.get_inp(BDL_SystemKeywords.HFAN_PLACEMENT)
            if not fan_control_method == BDL_SystemFanControlOptions.FAN_EIR_FPLR:
                curve_coeffs = self.fan_power_curves.get(fan_control_method)
            else:
                curve = self.parent.get_obj(
                    self.parent.get_inp(BDL_SystemKeywords.HFAN_EIR_FPLR)
                )
                curve_coeffs = curve.coefficients

        if curve_coeffs:
            multiplier = (
                1.11 if fan_placement == BDL_FanPlacementOptions.BLOW_THROUGH else 1.0
            )
            for i in range(0, 110, 10):
                airflow_ratio = i / 100
                electric_input_ratio = calculate_cubic(
                    curve_coeffs, airflow_ratio, 0, 1
                )
                self.operating_points.append(
                    {
                        "airflow": self.design_airflow * airflow_ratio,
                        "power": self.design_electric_power
                        * electric_input_ratio
                        * multiplier,
                    }
                )


class HeatingSystem:

    BDL_output_heat_type_map = {
        BDL_SystemHeatingTypes.HEAT_PUMP: None,  # Mapping updated based on condenser type
        BDL_SystemHeatingTypes.FURNACE: BDL_OutputHeatingTypes.FURNACE,
        BDL_SystemHeatingTypes.ELECTRIC: BDL_OutputHeatingTypes.ELECTRIC,
        BDL_SystemHeatingTypes.HOT_WATER: BDL_OutputHeatingTypes.HOT_WATER,
        BDL_SystemHeatingTypes.CONDENSING_UNIT: BDL_OutputHeatingTypes.VRF,
    }
    BDL_output_system_heating_type_map = {
        BDL_SystemTypes.PTAC: None,  # Mapping updated in populate_data_elements method  # Unavailable in DOE 2.3
        BDL_SystemTypes.PSZ: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.PMZS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.PVAVS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.PVVT: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.HP: BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED,
        BDL_SystemTypes.SZRH: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.VAVS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.RHFS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.DDS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.MZS: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.PIU: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.FC: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.IU: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.UVT: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.UHT: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.RESYS2: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.CBVAV: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.SUM: None,
        BDL_SystemTypes.DOAS: None,  # Mapping updated in populate_data_elements method
    }
    heat_type_map = {
        BDL_SystemHeatingTypes.NONE: HeatingSystemOptions.NONE,
        BDL_SystemHeatingTypes.ELECTRIC: HeatingSystemOptions.ELECTRIC_RESISTANCE,
        BDL_SystemHeatingTypes.HOT_WATER: HeatingSystemOptions.FLUID_LOOP,
        BDL_SystemHeatingTypes.FURNACE: HeatingSystemOptions.FURNACE,
        BDL_SystemHeatingTypes.HEAT_PUMP: HeatingSystemOptions.HEAT_PUMP,
        BDL_SystemHeatingTypes.CONDENSING_UNIT: HeatingSystemOptions.HEAT_PUMP,
        BDL_SystemHeatingTypes.DHW_LOOP: HeatingSystemOptions.OTHER,
        BDL_SystemHeatingTypes.STEAM: HeatingSystemOptions.OTHER,
    }
    heatpump_aux_type_map = {
        BDL_HPSupplementSourceOptions.ELECTRIC: HeatpumpAuxiliaryHeatOptions.ELECTRIC_RESISTANCE,
        BDL_HPSupplementSourceOptions.HOT_WATER: HeatpumpAuxiliaryHeatOptions.OTHER,
        BDL_HPSupplementSourceOptions.FURNACE: HeatpumpAuxiliaryHeatOptions.FURNACE,
    }
    heat_eff_metric_map = {
        BDL_OutputHeatingTypes.ELECTRIC: {
            None: HeatingMetricOptions.THERMAL_EFFICIENCY
        },
        BDL_OutputHeatingTypes.FURNACE: {None: HeatingMetricOptions.THERMAL_EFFICIENCY},
        BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED: {
            17: HeatingMetricOptions.HEAT_PUMP_COEFFICIENT_OF_PERFORMANCE_LOW_TEMPERATURE_NO_FAN,
            47: HeatingMetricOptions.HEAT_PUMP_COEFFICIENT_OF_PERFORMANCE_HIGH_TEMPERATURE_NO_FAN,
        },
        BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED: {
            68: HeatingMetricOptions.COEFFICIENT_OF_PERFORMANCE_WATER_TO_AIR_WATER_LOOP_NO_FAN,
            50: HeatingMetricOptions.COEFFICIENT_OF_PERFORMANCE_WATER_TO_AIR_GROUND_WATER_NO_FAN,
            32: HeatingMetricOptions.COEFFICIENT_OF_PERFORMANCE_BRINE_TO_AIR_GROUND_LOOP_NO_FAN,
        },
    }

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.type = None
        self.energy_source_type = None
        self.hot_water_loop = None
        self.water_source_heat_pump_loop = None
        self.design_capacity = None
        self.rated_capacity = None
        self.oversizing_factor = None
        self.is_calculated_size = None
        self.heating_coil_setpoint = None
        self.efficiency_metric_values = []
        self.efficiency_metric_types = []
        self.heatpump_auxiliary_heat_type = None
        self.heatpump_auxiliary_heat_high_shutoff_temperature = None
        self.heatpump_low_shutoff_temperature = None

    def populate_data_elements(self, output_data):
        self.name = self.parent_system.u_name + " HeatSys"
        self.type = self.heat_type_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.HEAT_SOURCE)
        )
        if self.parent_system.get_inp(
            BDL_SystemKeywords.TYPE
        ) == BDL_SystemTypes.HP and self.parent_system.get_inp(
            BDL_SystemKeywords.WLHP_CATEGORY
        ) in [
            BDL_WLHPCategoryOptions.WATER_LOOP,
            BDL_WLHPCategoryOptions.GROUND_WATER,
            BDL_WLHPCategoryOptions.GROUND_LOOP,
        ]:
            self.type = HeatingSystemOptions.HEAT_PUMP
        self.hot_water_loop = self.parent_system.get_inp(BDL_SystemKeywords.HW_LOOP)
        self.water_source_heat_pump_loop = self.parent_system.get_inp(
            BDL_SystemKeywords.CW_LOOP
        )
        self.heating_coil_setpoint = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.HEAT_SET_T)
        )
        self.heatpump_auxiliary_heat_type = self.heatpump_aux_type_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.HP_SUPP_SOURCE)
        )
        self.heatpump_auxiliary_heat_high_shutoff_temperature = (
            self.parent_system.try_float(
                self.parent_system.get_inp(BDL_SystemKeywords.MAX_HP_SUPP_T)
            )
        )
        self.heatpump_low_shutoff_temperature = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.MIN_HP_T)
        )

        sizing_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.SIZING_RATIO)
        )
        heat_sizing_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.HEAT_SIZING_RATI)
        )
        if sizing_ratio is not None and heat_sizing_ratio is not None:
            self.oversizing_factor = max(0, sizing_ratio * heat_sizing_ratio - 1)

        self.rated_capacity = self.parent_system.try_abs(
            self.parent_system.try_float(
                self.parent_system.get_inp(BDL_SystemKeywords.HEATING_CAPACITY)
            )
        )
        if not self.rated_capacity:
            self.rated_capacity = self.parent_system.try_abs(
                output_data.get("Rated Heating Capacity")
            )
        if not self.rated_capacity:
            self.rated_capacity = self.parent_system.try_abs(
                output_data.get("Heating Capacity")
            )
        self.design_capacity = self.parent_system.try_abs(
            output_data.get("Design Heating Capacity")
        )
        if not self.design_capacity:
            self.design_capacity = self.parent_system.try_abs(
                output_data.get("Heating Capacity")
            )

        if self.parent_system.is_zonal_system:
            self.is_calculated_size = (
                not self.parent_system.get_inp(BDL_SystemKeywords.HEATING_CAPACITY)
                and not self.parent_system.children[0].get_inp(
                    BDL_ZoneKeywords.MAX_HEAT_RATE
                )
                and not self.parent_system.children[0].get_inp(
                    BDL_ZoneKeywords.HEATING_CAPACITY
                )
            )
        else:
            self.is_calculated_size = not self.parent_system.get_inp(
                BDL_SystemKeywords.HEATING_CAPACITY
            )

        if self.type in [
            HeatingSystemOptions.FLUID_LOOP,
            HeatingSystemOptions.OTHER,
        ]:
            loop_name = self.parent_system.get_inp(BDL_SystemKeywords.HW_LOOP)
            loop = self.parent_system.get_obj(loop_name)
            if loop:
                self.energy_source_type = self.parent_system.get_loop_energy_source(
                    loop
                )
        elif self.type in [
            HeatingSystemOptions.ELECTRIC_RESISTANCE,
            HeatingSystemOptions.HEAT_PUMP,
        ]:
            self.energy_source_type = EnergySourceOptions.ELECTRICITY
        elif self.type == HeatingSystemOptions.FURNACE:
            self.energy_source_type = self.parent_system.get_furnace_energy_source()
        elif self.type == HeatingSystemOptions.NONE:
            self.energy_source_type = EnergySourceOptions.NONE

        self.populate_heating_eff_metric_and_value()

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        heating_system_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "energy_source_type",
            "hot_water_loop",
            "water_source_heat_pump_loop",
            "design_capacity",
            "rated_capacity",
            "oversizing_factor",
            "is_calculated_size",
            "heating_coil_setpoint",
            "efficiency_metric_values",
            "efficiency_metric_types",
            "heatpump_auxiliary_heat_type",
            "heatpump_auxiliary_heat_high_shutoff_temperature",
            "heatpump_low_shutoff_temperature",
        ]

        for attr in heating_system_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def populate_heating_eff_metric_and_value(self):
        """Populate the heating system efficiency metric and efficiency value."""
        heating_eir = self.parent_system.get_inp(BDL_SystemKeywords.HEATING_EIR)
        furnace_hir = self.parent_system.get_inp(BDL_SystemKeywords.FURNACE_HIR)
        rated_ect = self.parent_system.get_inp(BDL_SystemKeywords.HT_RATED_ECT)

        metric_type = None
        entering_condenser_temperature = (
            self.parent_system.try_float(rated_ect)
            if rated_ect is not None
            and self.parent_system.bdl_output_heat_type
            in [
                BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED,
                BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED,
            ]
            else None
        )

        if (
            self.parent_system.bdl_output_heat_type in self.heat_eff_metric_map
            and self.parent_system.bdl_output_heat_type != BDL_OutputHeatingTypes.VRF
        ):
            metric_type = self.heat_eff_metric_map[
                self.parent_system.bdl_output_heat_type
            ].get(entering_condenser_temperature, HeatingMetricOptions.OTHER)

        if not metric_type:
            return

        eff_cop = (
            1 / self.parent_system.try_float(heating_eir)
            if heating_eir is not None
            else None
        )
        eff_et = (
            1
            if self.parent_system.bdl_output_heat_type
            == BDL_OutputHeatingTypes.ELECTRIC
            else (
                1 / self.parent_system.try_float(furnace_hir)
                if furnace_hir is not None
                else None
            )
        )

        if metric_type == HeatingMetricOptions.THERMAL_EFFICIENCY:
            self.efficiency_metric_values.append(eff_et)
        else:
            self.efficiency_metric_values.append(eff_cop)

        self.efficiency_metric_types.append(metric_type)


class CoolingSystem:
    cool_type_map = {
        BDL_SystemCoolingTypes.ELEC_DX: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemCoolingTypes.CHILLED_WATER: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemCoolingTypes.NONE: CoolingSystemOptions.NONE,
    }
    system_cooling_type_map = {
        BDL_SystemTypes.PTAC: CoolingSystemOptions.DIRECT_EXPANSION,  # Unavailable in DOE 2.3
        BDL_SystemTypes.PSZ: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemTypes.PMZS: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemTypes.PVAVS: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemTypes.PVVT: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemTypes.HP: CoolingSystemOptions.DIRECT_EXPANSION,
        # IS WATER LOOP HEAT PUMP CONSIDERED DIRECT_EXPANSION???
        BDL_SystemTypes.SZRH: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.VAVS: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.RHFS: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.DDS: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.MZS: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.PIU: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.FC: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.IU: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.UVT: CoolingSystemOptions.NONE,
        BDL_SystemTypes.UHT: CoolingSystemOptions.NONE,
        BDL_SystemTypes.RESYS2: CoolingSystemOptions.DIRECT_EXPANSION,
        BDL_SystemTypes.CBVAV: CoolingSystemOptions.FLUID_LOOP,
        BDL_SystemTypes.SUM: CoolingSystemOptions.NONE,
        BDL_SystemTypes.DOAS: None,  # Mapping updated in populate_data_elements method
    }
    cool_eff_metric_map = {
        BDL_OutputCoolingTypes.DX_AIR_COOLED: {
            95: CoolingMetricOptions.FULL_LOAD_COEFFICIENT_OF_PERFORMANCE_NO_FAN
        },
        BDL_OutputCoolingTypes.DX_WATER_COOLED: {
            59: CoolingMetricOptions.COEFFICIENT_OF_PERFORMANCE_WATER_TO_AIR_GROUND_WATER_NO_FAN,
            77: CoolingMetricOptions.COEFFICIENT_OF_PERFORMANCE_BRINE_TO_AIR_GROUND_LOOP_NO_FAN,
            86: CoolingMetricOptions.COEFFICIENT_OF_PERFORMANCE_WATER_TO_AIR_WATER_LOOP_NO_FAN,
        },
    }
    BDL_output_system_cooling_type_map = {
        BDL_SystemTypes.PTAC: BDL_OutputCoolingTypes.DX_AIR_COOLED,  # Unavailable in DOE 2.3
        BDL_SystemTypes.PSZ: None,  # Mapping updated based on condenser type
        BDL_SystemTypes.PMZS: None,  # Mapping updated based on condenser type
        BDL_SystemTypes.PVAVS: None,  # Mapping updated based on condenser type
        BDL_SystemTypes.PVVT: None,  # Mapping updated based on condenser type
        BDL_SystemTypes.HP: BDL_OutputCoolingTypes.DX_WATER_COOLED,
        BDL_SystemTypes.SZRH: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.VAVS: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.RHFS: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.DDS: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.MZS: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.PIU: None,  # Mapping updated in populate_data_elements method
        BDL_SystemTypes.FC: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.IU: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.UVT: CoolingSystemOptions.NONE,
        BDL_SystemTypes.UHT: CoolingSystemOptions.NONE,
        BDL_SystemTypes.RESYS2: None,  # Mapping updated based on condenser type
        BDL_SystemTypes.CBVAV: BDL_OutputCoolingTypes.CHILLED_WATER,
        BDL_SystemTypes.SUM: None,
        BDL_SystemTypes.DOAS: None,  # Mapping updated in populate_data_elements method
    }

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.type = None
        self.design_total_cool_capacity = None
        self.design_sensible_cool_capacity = None
        self.rated_total_cool_capacity = None
        self.rated_sensible_cool_capacity = None
        self.oversizing_factor = None
        self.is_calculated_size = None
        self.chilled_water_loop = None
        self.condenser_water_loop = None
        self.vrf_sys_condenser = None
        self.efficiency_metric_values = None
        self.efficiency_metric_types = None
        self.dehumidification_type = None
        self.cooling_turndown_ratio = None

    def populate_data_elements(self, output_data):
        self.name = self.parent_system.u_name + " CoolSys"
        self.type = self.system_cooling_type_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.TYPE)
        )
        self.chilled_water_loop = self.parent_system.get_inp(
            BDL_SystemKeywords.CHW_LOOP
        )
        self.condenser_water_loop = self.parent_system.get_inp(
            BDL_SystemKeywords.CW_LOOP
        )
        condensing_unit = self.parent_system.get_inp(BDL_SystemKeywords.CONDENSING_UNIT)
        self.vrf_sys_condenser = self.parent_system.get_obj(condensing_unit)
        self.cooling_turndown_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.MIN_UNLOAD_RATIO)
        )
        sizing_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.SIZING_RATIO)
        )
        cool_sizing_ratio = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOL_SIZING_RATI)
        )
        if sizing_ratio is not None and cool_sizing_ratio is not None:
            self.oversizing_factor = max(0, sizing_ratio * cool_sizing_ratio - 1)
        self.rated_total_cool_capacity = self.parent_system.try_abs(
            self.parent_system.try_float(
                self.parent_system.get_inp(BDL_SystemKeywords.COOLING_CAPACITY)
            )
        )
        if not self.rated_total_cool_capacity:
            self.rated_total_cool_capacity = self.parent_system.try_abs(
                output_data.get("Rated Cooling Capacity")
            )
        if not self.rated_total_cool_capacity:
            self.rated_total_cool_capacity = self.parent_system.try_abs(
                output_data.get("Cooling Capacity")
            )
        self.rated_sensible_cool_capacity = self.parent_system.try_abs(
            self.parent_system.try_float(
                self.parent_system.get_inp(BDL_SystemKeywords.COOL_SH_CAP)
            )
        )
        if not self.rated_sensible_cool_capacity:
            rated_shr = self.parent_system.try_abs(output_data.get("Rated Cooling SHR"))
            if rated_shr and self.rated_total_cool_capacity and rated_shr != 1:
                self.rated_sensible_cool_capacity = (
                    rated_shr * self.rated_total_cool_capacity
                )
        if not self.rated_sensible_cool_capacity:
            shr = self.parent_system.try_abs(output_data.get("Sensible Heat Ratio"))
            if shr and self.rated_total_cool_capacity:
                self.rated_sensible_cool_capacity = shr * self.rated_total_cool_capacity
        self.design_total_cool_capacity = self.parent_system.try_abs(
            output_data.get("Design Cooling Capacity")
        )
        if not self.design_total_cool_capacity:
            self.design_total_cool_capacity = self.parent_system.try_abs(
                output_data.get("Cooling Capacity")
            )
        design_shr = self.parent_system.try_abs(output_data.get("Design Cooling SHR"))
        if design_shr and self.design_total_cool_capacity and design_shr != 1:
            self.design_sensible_cool_capacity = (
                design_shr * self.design_total_cool_capacity
            )
        if not self.design_sensible_cool_capacity:
            shr = self.parent_system.try_abs(output_data.get("Sensible Heat Ratio"))
            if shr and self.design_total_cool_capacity:
                self.design_sensible_cool_capacity = (
                    shr * self.design_total_cool_capacity
                )
        if self.parent_system.is_zonal_system:
            self.is_calculated_size = (
                not self.parent_system.get_inp(BDL_SystemKeywords.COOLING_CAPACITY)
                and not self.parent_system.children[0].get_inp(
                    BDL_ZoneKeywords.MAX_COOL_RATE
                )
                and not self.parent_system.children[0].get_inp(
                    BDL_ZoneKeywords.COOLING_CAPACITY
                )
            )
        else:
            self.is_calculated_size = not self.parent_system.get_inp(
                BDL_SystemKeywords.COOLING_CAPACITY
            )

        self.efficiency_metric_values = []
        self.efficiency_metric_types = []
        self.populate_cooling_eff_metric_and_value()

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        cooling_system_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "design_total_cool_capacity",
            "design_sensible_cool_capacity",
            "rated_total_cool_capacity",
            "rated_sensible_cool_capacity",
            "oversizing_factor",
            "is_calculated_size",
            "chilled_water_loop",
            "condenser_water_loop",
            "efficiency_metric_values",
            "efficiency_metric_types",
            "dehumidification_type",
            "cooling_turndown_ratio",
        ]

        for attr in cooling_system_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def populate_cooling_eff_metric_and_value(self):
        """
        Populate the cooling system efficiency metric and the efficiency value.
        """
        cooling_eir, cop, entering_condenser_temperature = None, None, None

        cooling_eir = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.COOLING_EIR)
        )
        if cooling_eir:
            cop = 1 / cooling_eir

        if (
            rated_ect := self.parent_system.get_inp(BDL_SystemKeywords.RATED_ECT)
        ) is not None:
            entering_condenser_temperature = self.parent_system.try_float(rated_ect)

        if (
            self.parent_system.bdl_output_cool_type in self.cool_eff_metric_map
            and self.parent_system.bdl_output_heat_type != BDL_OutputHeatingTypes.VRF
            and cop
        ):
            metric_type = self.cool_eff_metric_map[
                self.parent_system.bdl_output_cool_type
            ].get(entering_condenser_temperature, CoolingMetricOptions.OTHER)
            self.efficiency_metric_types.append(metric_type)
            self.efficiency_metric_values.append(cop)

        elif self.parent_system.bdl_output_heat_type == BDL_OutputHeatingTypes.VRF:
            # Covers VRF, takes the efficiency from the condensing unit
            if (
                self.parent_system.try_float(
                    self.vrf_sys_condenser.get_inp(BDL_CondenserKeywords.COOL_RATED_ODB)
                )
                == 95
            ):
                efficiency_metric_type = (
                    CoolingMetricOptions.FULL_LOAD_COEFFICIENT_OF_PERFORMANCE_NO_FAN
                )

            else:
                efficiency_metric_type = CoolingMetricOptions.OTHER

            cooling_eir = self.vrf_sys_condenser.try_float(
                self.vrf_sys_condenser.get_inp(BDL_CondenserKeywords.COOLING_EIR)
            )
            if cooling_eir:
                self.efficiency_metric_types.append(efficiency_metric_type)
                self.efficiency_metric_values.append(1 / cooling_eir)

        elif (
            self.parent_system.bdl_output_cool_type
            != BDL_OutputCoolingTypes.CHILLED_WATER
            and self.parent_system.bdl_output_cool_type is not None
            and cop
        ):
            self.efficiency_metric_types.append(CoolingMetricOptions.OTHER)
            self.efficiency_metric_values.append(cop)


class PreheatSystem:

    heat_type_map = {
        BDL_SystemHeatingTypes.NONE: HeatingSystemOptions.NONE,
        BDL_SystemHeatingTypes.ELECTRIC: HeatingSystemOptions.ELECTRIC_RESISTANCE,
        BDL_SystemHeatingTypes.HOT_WATER: HeatingSystemOptions.FLUID_LOOP,
        BDL_SystemHeatingTypes.FURNACE: HeatingSystemOptions.FURNACE,
        BDL_SystemHeatingTypes.HEAT_PUMP: HeatingSystemOptions.HEAT_PUMP,
        BDL_SystemHeatingTypes.CONDENSING_UNIT: HeatingSystemOptions.HEAT_PUMP,
        BDL_SystemHeatingTypes.DHW_LOOP: HeatingSystemOptions.OTHER,
        BDL_SystemHeatingTypes.STEAM: HeatingSystemOptions.OTHER,
    }

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.type = None
        self.energy_source_type = None
        self.hot_water_loop = None
        self.water_source_heat_pump_loop = None
        self.design_capacity = None
        self.rated_capacity = None
        self.oversizing_factor = None
        self.is_calculated_size = None
        self.heating_coil_setpoint = None
        self.efficiency_metric_values = []
        self.efficiency_metric_types = []
        self.heatpump_auxiliary_heat_type = None
        self.heatpump_auxiliary_heat_high_shutoff_temperature = None
        self.heatpump_low_shutoff_temperature = None

    def populate_data_elements(self, output_data):
        self.name = self.parent_system.u_name + " PreheatSys"
        self.type = self.heat_type_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.PREHEAT_SOURCE)
        )
        self.rated_capacity = self.parent_system.try_abs(
            self.parent_system.try_float(
                self.parent_system.get_inp(BDL_SystemKeywords.PREHEAT_CAPACITY)
            )
        )
        self.design_capacity = self.parent_system.try_abs(
            output_data.get("Design Preheat Capacity")
        )
        self.is_calculated_size = not self.parent_system.get_inp(
            BDL_SystemKeywords.PREHEAT_CAPACITY
        )
        self.heating_coil_setpoint = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.PREHEAT_T)
        )
        self.hot_water_loop = self.parent_system.get_inp(BDL_SystemKeywords.PHW_LOOP)
        if self.type in [
            HeatingSystemOptions.FLUID_LOOP,
            HeatingSystemOptions.OTHER,
        ]:
            loop = self.parent_system.get_obj(self.hot_water_loop)
            if loop:
                self.energy_source_type = self.parent_system.get_loop_energy_source(
                    loop
                )
        elif self.type in [
            HeatingSystemOptions.ELECTRIC_RESISTANCE,
            HeatingSystemOptions.HEAT_PUMP,
        ]:
            self.energy_source_type = EnergySourceOptions.ELECTRICITY
        elif self.type == HeatingSystemOptions.FURNACE:
            self.energy_source_type = self.parent_system.get_furnace_energy_source()
        elif self.type == HeatingSystemOptions.NONE:
            self.energy_source_type = EnergySourceOptions.NONE

        self.efficiency_metric_types = []
        self.efficiency_metric_values = []
        self.populate_preheat_eff_metric_and_value()

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        preheat_system_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "energy_source_type",
            "hot_water_loop",
            "water_source_heat_pump_loop",
            "design_capacity",
            "rated_capacity",
            "oversizing_factor",
            "is_calculated_size",
            "heating_coil_setpoint",
            "efficiency_metric_values",
            "efficiency_metric_types",
            "heatpump_auxiliary_heat_type",
            "heatpump_auxiliary_heat_high_shutoff_temperature",
            "heatpump_low_shutoff_temperature",
        ]

        for attr in preheat_system_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def populate_preheat_eff_metric_and_value(self):
        """
        Populate the preheating system efficiency metric and the efficiency value.
        """

        furnace_hir = self.parent_system.get_inp(BDL_SystemKeywords.FURNACE_HIR)
        eff_et = (
            1 / self.parent_system.try_float(furnace_hir)
            if furnace_hir is not None
            else None
        )

        match self.type:
            case HeatingSystemOptions.FURNACE:
                self.efficiency_metric_types.append(
                    HeatingMetricOptions.THERMAL_EFFICIENCY
                )
                self.efficiency_metric_values.append(eff_et)
            case HeatingSystemOptions.ELECTRIC_RESISTANCE:
                self.efficiency_metric_types.append(
                    HeatingMetricOptions.THERMAL_EFFICIENCY
                )
                self.efficiency_metric_values.append(1)


class AirEconomizer:

    economizer_map = {
        BDL_EconomizerOptions.FIXED: AirEconomizerOptions.FIXED_FRACTION,
        BDL_EconomizerOptions.OA_TEMP: AirEconomizerOptions.TEMPERATURE,
        BDL_EconomizerOptions.OA_ENTHALPY: AirEconomizerOptions.ENTHALPY,
        BDL_EconomizerOptions.DUAL_TEMP: AirEconomizerOptions.DIFFERENTIAL_TEMPERATURE,
        BDL_EconomizerOptions.DUAL_ENTHALPY: AirEconomizerOptions.DIFFERENTIAL_ENTHALPY,
    }

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.type = None
        self.high_limit_shutoff_temperature = None
        self.is_integrated = None

    def populate_data_elements(self):
        self.name = self.parent_system.u_name + " AirEconomizer"
        self.type = self.economizer_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.OA_CONTROL)
        )
        self.high_limit_shutoff_temperature = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.ECONO_LIMIT_T)
        )
        self.is_integrated = (
            True
            if self.parent_system.get_inp(BDL_SystemKeywords.COOL_SOURCE)
            == BDL_SystemCoolingTypes.CHILLED_WATER
            else not self.parent_system.boolean_map.get(
                self.parent_system.get_inp(BDL_SystemKeywords.ECONO_LOCKOUT)
            )
        )

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        air_economizer_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "high_limit_shutoff_temperature",
            "is_integrated",
        ]
        for attr in air_economizer_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value


class AirEnergyRecovery:

    has_recovery_map = {
        BDL_EnergyRecoveryOptions.NO: EnergyRecoveryOperationOptions.NONE,
        BDL_EnergyRecoveryOptions.RELIEF_ONLY: None,  # Mapping updated in populate_air_energy_recovery method
        BDL_EnergyRecoveryOptions.EXHAUST_ONLY: None,  # Mapping updated in populate_air_energy_recovery method
        BDL_EnergyRecoveryOptions.RELIEF_EXHAUST: None,  # Mapping updated in populate_air_energy_recovery method
        BDL_EnergyRecoveryOptions.YES: None,  # Mapping updated in populate_air_energy_recovery method
    }
    recovery_type_map = {
        BDL_EnergyRecoveryTypes.SENSIBLE_HX: EnergyRecoveryOptions.SENSIBLE_HEAT_EXCHANGE,
        BDL_EnergyRecoveryTypes.ENTHALPY_HX: EnergyRecoveryOptions.ENTHALPY_HEAT_EXCHANGE,
        BDL_EnergyRecoveryTypes.SENSIBLE_WHEEL: EnergyRecoveryOptions.SENSIBLE_HEAT_WHEEL,
        BDL_EnergyRecoveryTypes.ENTHALPY_WHEEL: EnergyRecoveryOptions.ENTHALPY_HEAT_WHEEL,
        BDL_EnergyRecoveryTypes.HEAT_PIPE: EnergyRecoveryOptions.HEAT_PIPE,
    }
    er_operation_map = {
        BDL_EnergyRecoveryOperationOptions.WHEN_FANS_ON: EnergyRecoveryOperationOptions.WHEN_FANS_ON,
        BDL_EnergyRecoveryOperationOptions.WHEN_MIN_OA: EnergyRecoveryOperationOptions.WHEN_MINIMUM_OUTSIDE_AIR,
        BDL_EnergyRecoveryOperationOptions.ERV_SCHEDULE: EnergyRecoveryOperationOptions.SCHEDULED,
        BDL_EnergyRecoveryOperationOptions.OA_EXHAUST_DT: EnergyRecoveryOperationOptions.OTHER,
        BDL_EnergyRecoveryOperationOptions.OA_EXHAUST_DH: EnergyRecoveryOperationOptions.OTHER,
    }
    er_sat_control_map = {
        BDL_EnergyRecoveryTemperatureControlOptions.FLOAT: EnergyRecoverySupplyAirTemperatureControlOptions.OTHER,
        BDL_EnergyRecoveryTemperatureControlOptions.FIXED_SETPT: EnergyRecoverySupplyAirTemperatureControlOptions.FIXED_SETPOINT,
        BDL_EnergyRecoveryTemperatureControlOptions.MIXED_AIR_RESET: EnergyRecoverySupplyAirTemperatureControlOptions.MIXED_AIR_RESET,
    }

    def __init__(self, parent_system):
        self.parent_system = parent_system
        self.data_structure = {}

        self.name = None
        self.reporting_name = None
        self.notes = None

        self.type = None
        self.energy_recovery_operation = None
        self.energy_recovery_supply_air_temperature_control = None
        self.design_sensible_effectiveness = None
        self.design_latent_effectiveness = None
        self.outdoor_airflow = None
        self.exhaust_airflow = None

    def populate_data_elements(self):
        self.name = self.parent_system.u_name + " AirEnergyRecovery"
        recover_exhaust = self.parent_system.get_inp(BDL_SystemKeywords.RECOVER_EXHAUST)
        recovery_type = self.recovery_type_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_RECOVER_TYPE)
        )
        self.has_recovery_map.update(
            {
                BDL_EnergyRecoveryOptions.RELIEF_ONLY: recovery_type,
                BDL_EnergyRecoveryOptions.EXHAUST_ONLY: recovery_type,
                BDL_EnergyRecoveryOptions.RELIEF_EXHAUST: recovery_type,
                BDL_EnergyRecoveryOptions.YES: recovery_type,
            }
        )
        self.type = self.has_recovery_map.get(recover_exhaust)
        self.energy_recovery_operation = self.er_operation_map.get(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_RUN_CTRL)
        )
        self.energy_recovery_supply_air_temperature_control = (
            self.er_sat_control_map.get(
                self.parent_system.get_inp(BDL_SystemKeywords.ERV_TEMP_CTRL)
            )
        )
        self.design_sensible_effectiveness = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_SENSIBLE_EFF)
        )
        self.design_latent_effectiveness = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_LATENT_EFF)
        )
        self.outdoor_airflow = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_OA_FLOW)
        )
        self.exhaust_airflow = self.parent_system.try_float(
            self.parent_system.get_inp(BDL_SystemKeywords.ERV_EXH_FLOW)
        )
        if self.exhaust_airflow is None:
            self.exhaust_airflow = self.outdoor_airflow

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        air_energy_recovery_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "energy_recovery_operation",
            "energy_recovery_supply_air_temperature_control",
            "design_sensible_effectiveness",
            "design_latent_effectiveness",
            "outdoor_airflow",
            "exhaust_airflow",
        ]
        for attr in air_energy_recovery_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value
