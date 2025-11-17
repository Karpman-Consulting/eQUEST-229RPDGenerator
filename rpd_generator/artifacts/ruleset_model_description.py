import copy

from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.base_node import Base, BaseNode
from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.artifacts.building_segment import BuildingSegment
from rpd_generator.artifacts.building import Building
from rpd_generator.bdl_structure.bdl_commands.circulation_loop import (
    ServiceWaterHeatingUse,
)

EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
EndUseOptions = SchemaEnums.schema_enums["EndUseOptions"]
BDL_FuelMeterKeywords = BDLEnums.bdl_enums["FuelMeterKeywords"]
BDL_FuelTypes = BDLEnums.bdl_enums["FuelTypes"]
BDL_ElecGeneratorKeywords = BDLEnums.bdl_enums["ElecGeneratorKeywords"]
BDL_UtilityRateKeywords = BDLEnums.bdl_enums["UtilityRateKeywords"]
BDL_SiteParameterKeywords = BDLEnums.bdl_enums["SiteParameterKeywords"]
BDL_ElecGeneratorTypes = BDLEnums.bdl_enums["ElecGeneratorTypes"]
BDL_UtilityRateTypes = BDLEnums.bdl_enums["UtilityRateTypes"]
BDL_AirflowConditionOptions = BDLEnums.bdl_enums["AirflowConditionOptions"]


fuel_type_map = {
    BDL_FuelTypes.ELECTRICITY: EnergySourceOptions.ELECTRICITY,
    BDL_FuelTypes.NATURAL_GAS: EnergySourceOptions.NATURAL_GAS,
    BDL_FuelTypes.LPG: EnergySourceOptions.PROPANE,
    BDL_FuelTypes.FUEL_OIL: EnergySourceOptions.FUEL_OIL,
    BDL_FuelTypes.DIESEL_OIL: EnergySourceOptions.OTHER,
    BDL_FuelTypes.COAL: EnergySourceOptions.OTHER,
    BDL_FuelTypes.METHANOL: EnergySourceOptions.OTHER,
    BDL_FuelTypes.OTHER_FUEL: EnergySourceOptions.OTHER,
    EnergySourceOptions.PURCHASED_HOT_WATER: EnergySourceOptions.PURCHASED_HOT_WATER,
    EnergySourceOptions.PURCHASED_CHILLED_WATER: EnergySourceOptions.PURCHASED_CHILLED_WATER,
    EnergySourceOptions.ON_SITE_RENEWABLES: EnergySourceOptions.ON_SITE_RENEWABLES,
}
utility_rate_service_map = {
    BDL_UtilityRateTypes.ELECTRICITY: EnergySourceOptions.ELECTRICITY,
    BDL_UtilityRateTypes.NATURAL_GAS: EnergySourceOptions.NATURAL_GAS,
    BDL_UtilityRateTypes.STEAM: EnergySourceOptions.PURCHASED_HOT_WATER,
    BDL_UtilityRateTypes.CHILLED_WATER: EnergySourceOptions.PURCHASED_CHILLED_WATER,
    BDL_UtilityRateTypes.ELECTRIC_SALE: EnergySourceOptions.ON_SITE_RENEWABLES,
    BDL_UtilityRateTypes.LPG: EnergySourceOptions.PROPANE,
    BDL_UtilityRateTypes.FUEL_OIL: EnergySourceOptions.FUEL_OIL,
    BDL_UtilityRateTypes.DIESEL_OIL: EnergySourceOptions.OTHER,
    BDL_UtilityRateTypes.COAL: EnergySourceOptions.OTHER,
    BDL_UtilityRateTypes.METHANOL: EnergySourceOptions.OTHER,
    BDL_UtilityRateTypes.OTHER_FUEL: EnergySourceOptions.OTHER,
}


class RulesetModelDescription(Base):
    """
    This class is used to represent the RulesetModelDescription object in the 229 schema. It also stores additional model-level data.
    """

    """Once development is complete, this can be replaced with a list of all bdl_command attribute values from classes that 
    inherit from BaseNode or BaseDefinition. Each class will also need a priority attribute in this case.
    For now, this is a list of BDL commands that are ready to be processed, in the order they should be processed."""
    COMMAND_PROCESSING_ORDER = [
        "RUN-PERIOD-PD",
        "SITE-PARAMETERS",
        "BUILD-PARAMETERS",
        # Building Parameters must populate before Exterior-Walls, Interior-Walls, Underground-Walls, Windows, Doors
        "MASTER-METERS",
        # Master meters must populate bofore other meters and before Systems, Boilers, DW-Heaters, Chillers
        "FUEL-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
        "ELEC-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
        "STEAM-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
        "CHW-METER",  # Meters must populate before Systems, Boilers, DW-Heaters, Chillers
        "UTILITY-RATE",
        "CURVE-FIT",
        "FIXED-SHADE",
        "GLASS-TYPE",
        "MATERIAL",  # Materials must populate before Layers, Constructions
        "LAYERS",  # Layers must populate before Constructions
        "CONSTRUCTION",  # Constructions must populate before Exterior-Walls, Interior-Walls, Underground-Walls, Doors
        "HOLIDAYS",
        "DAY-SCHEDULE-PD",
        "WEEK-SCHEDULE-PD",
        "SCHEDULE-PD",
        "POLYGON",  # Polygons must populate before Spaces
        "CONDENSING-UNIT",
        "PUMP",  # Pumps must populate before Boiler, Chiller, Heat-Rejection, Circulation-Loop
        "CIRCULATION-LOOP",  # Circulation loops must populate before Boiler, Chiller, DWHeater, Heat-Rejection
        "BOILER",  # Boilers must populate before systems
        "CHILLER",  # Chillers must populate before systems
        "DW-HEATER",  # DWHeaters must populate before systems
        "HEAT-REJECTION",
        "GROUND-LOOP-HX",
        "FLOOR",  # Floors must populate before Spaces
        "SYSTEM",  # Systems must populate before Zones
        "ZONE",  # Zones must populate before Spaces
        "SPACE",  # Spaces must populate before Exterior-Walls, Interior-Walls, Underground-Walls
        "EXTERIOR-WALL",  # Exterior walls must populate before Windows, Doors
        "INTERIOR-WALL",  # Interior walls must populate before Windows, Doors
        "UNDERGROUND-WALL",
        "WINDOW",
        "DOOR",
        "EQUIP-CTRL",
        "LOAD-MANAGEMENT",
        "ELEC-GENERATOR",
    ]

    def __init__(self, obj_id, rpd):
        self.file_path = None
        self.doe2_version = None
        self.doe2_data_path = None

        self.rpd = rpd
        self.has_site_shading = False  # Store the default value for all buildings in the RMD based on presence of FixedShade objects
        self.building_azimuth = None
        # store BDL objects for the model associated with the RMD
        self.bdl_obj_instances = {
            self.rpd.project_name: self.rpd,
            obj_id: self,
            "Default Building": Building("Default Building", self),
        }
        self.default_building_segment = None
        # store unique building area types to create BuildingSegment objects
        self.building_area_types = set()
        # store space names mapped to their zone objects for quick access
        self.space_map = {}
        # store material variants to know when a clone is needed
        self.material_variants = {}  # key = (base_id, thickness), value = material_id
        # store names of specific object types for quick access
        self.site_parameter_name = None
        self.weather_obj = Weather(self)

        self.master_meters = None
        self.electric_meter_names = []
        self.fuel_meter_names = []
        self.steam_meter_names = []
        self.chilled_water_meter_names = []
        self.curve_fit_names = []
        self.utility_rate_names = []
        self.elec_generator_names = []
        self.floor_names = []
        self.system_names = []
        self.zone_names = []
        self.zonal_exh_fan_names = []
        self.ext_wall_names = []
        self.int_wall_names = []
        self.undg_wall_names = []
        self.window_names = []
        self.skylight_names = []
        self.door_names = []
        self.circulation_loop_names = []
        self.boiler_names = []
        self.chiller_names = []
        self.domestic_water_heater_names = []
        self.heat_rejection_names = []
        self.ground_loop_hx_names = []
        self.pump_names = []
        self.equip_ctrl_names = []
        self.service_water_heating_use_names = []

        self.rmd_data_structure = {}

        # data elements with children
        self.calendar = {}
        self.weather = {}
        self.transformers = []
        self.buildings = []
        self.schedules = []
        self.constructions = []
        self.materials = []
        self.fluid_loops = []
        self.service_water_heating_distribution_systems = []
        self.service_water_heating_equipment = []
        self.service_water_heating_uses = []
        self.pumps = []
        self.boilers = []
        self.chillers = []
        self.heat_rejections = []
        self.external_fluid_sources = []
        self.model_output = {}

        # data elements with no children
        self.obj_id = obj_id
        self.reporting_name = None
        self.notes = None
        self.type = SchemaEnums.schema_enums["CommonRulesetModelOptions"].USER
        self.measured_infiltration_pressure_difference = None
        self.is_measured_infiltration_based_on_test = None
        self.altitude = None
        self.site_zone_type = None

    def populate_all_child_data_elements(self, testing=False):
        sorted_commands = self.sort_commands()
        for obj_instance in sorted_commands:
            instance_filter = (
                (BaseNode, BaseDefinition)
                if testing
                else (BaseNode, RulesetModelDescription, BaseDefinition)
            )
            if isinstance(obj_instance, instance_filter):
                obj_instance.populate_data_elements()

    def populate_all_data_groups(self):
        # Repopulate the sorted commands in case objects were added during the populate_data_elements method
        sorted_commands = self.sort_commands()
        for obj_instance in sorted_commands:
            if isinstance(
                obj_instance,
                (
                    BaseNode,
                    RulesetModelDescription,
                    Building,
                    BuildingSegment,
                    ServiceWaterHeatingUse,
                ),
            ):
                obj_instance.populate_data_group()

    def insert_all_to_rpd(self):
        for obj_instance in self.bdl_obj_instances.values():
            if isinstance(
                obj_instance,
                (
                    BaseNode,
                    RulesetModelDescription,
                    Building,
                    BuildingSegment,
                    ServiceWaterHeatingUse,
                ),
            ):
                obj_instance.insert_to_rpd()

    def populate_rmd_data(self, testing=False):
        self.populate_all_child_data_elements(testing)
        self.populate_all_data_groups()

        if not testing:
            self.insert_all_to_rpd()

    def sort_commands(self):
        command_tuples = []
        additional_objs = []

        # Add all objects with a bdl_command attribute to the list
        for obj in self.bdl_obj_instances.values():
            if isinstance(obj, (BaseNode, BaseDefinition)):
                command_tuples.append((obj.bdl_command, obj))
            elif isinstance(
                obj,
                (
                    RulesetModelDescription,
                    Building,
                    BuildingSegment,
                    ServiceWaterHeatingUse,
                ),
            ):
                additional_objs.append(obj)

        order_map = {cmd: i for i, cmd in enumerate(self.COMMAND_PROCESSING_ORDER)}
        sorted_tuples = sorted(
            command_tuples, key=lambda x: order_map.get(x[0], float("inf"))
        )
        return [t[1] for t in sorted_tuples] + additional_objs

    def get_obj(self, u_name):
        """
        Return the object instance by its u_name.
        :param u_name: str
        """
        return self.bdl_obj_instances.get(u_name, None)

    def populate_data_elements(self):
        site_parameter_obj = self.bdl_obj_instances.get(self.site_parameter_name)
        altitude = site_parameter_obj.get_inp(BDL_SiteParameterKeywords.ALTITUDE)
        self.altitude = (
            float(altitude)
            if altitude
            and site_parameter_obj.get_inp(BDL_SiteParameterKeywords.SPECIFY_AIRFLOWS)
            == BDL_AirflowConditionOptions.BLDG_ALTITUDE
            else 0
        )
        requests, str_requests = self.get_output_requests()
        output_data = self.get_output_data(self, requests)
        for key, value in str_requests.items():
            output_data[key] = self.get_single_string_output(self, *value)

        model_output = OutputInstance(self)
        model_output.populate_data_elements(output_data)
        model_output.populate_data_group()
        model_output.insert_to_rpd()

    def get_output_requests(self):
        requests = {
            "Total Site Energy (BTU)": (
                2001001,
                "",
                "",
            ),
            "Unmet Cooling Load Hours": (
                2001022,
                "",
                "",
            ),
            "Unmet Heating Load Hours": (
                2001023,
                "",
                "",
            ),
            "Building Peak Cooling Load": (
                1003003,
                "",
                "",
            ),
            "Building Peak Heating Load": (
                1003005,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Lights": (
                2001009,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Task Lights": (
                2001010,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Misc Equip": (
                2001011,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Space Heating": (
                2001012,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Space Cooling": (
                2001013,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Heat Rejection": (
                2001014,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Pumps & Aux": (
                2001015,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Ventilation Fans": (
                2001016,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Refrigeration Display": (
                2001017,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Ht Pump Supplemental Heat": (
                2001018,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Domestic Hot Water": (
                2001019,
                "",
                "",
            ),
            "Total Site Energy (BTU) - Exterior Usage": (
                2001020,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use": (
                2305001,
                "",
                "",
            ),
            "Elec (all meters) - Peak Demand": (
                2305002,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Lights": (
                2305006,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Task Lights": (
                2305007,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Misc Equip": (
                2305008,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Space Heating": (
                2305009,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Space Cooling": (
                2305010,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Heat Rejection": (
                2305011,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Pumps & Aux": (
                2305012,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Ventilation Fans": (
                2305013,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Refrigeration Display": (
                2305014,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Ht Pump Supplemental Heat": (
                2305015,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Domestic Hot Water": (
                2305016,
                "",
                "",
            ),
            "Elec (all meters) - Elec Use - Exterior Usage": (
                2305017,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Lights": (
                2305019,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Task Lights": (
                2305020,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Misc Equip": (
                2305021,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Space Heating": (
                2305022,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Space Cooling": (
                2305023,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Heat Rejection": (
                2305024,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Pumps & Aux": (
                2305025,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Ventilation Fans": (
                2305026,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Refrigeration Display": (
                2305027,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Ht Pump Supplemental Heat": (
                2305028,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Domestic Hot Water": (
                2305029,
                "",
                "",
            ),
            "Elec (all meters) - Peak - Exterior Usage": (
                2305030,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Lights": (
                2305186,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Task Lights": (
                2305187,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Misc Equip": (
                2305188,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Space Heating": (
                2305189,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Space Cooling": (
                2305190,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Heat Rejection": (
                2305191,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Pumps & Aux": (
                2305192,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Ventilation Fans": (
                2305193,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Refrigeration Display": (
                2305194,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Ht Pump Supplemental Heat": (
                2305195,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Domestic Hot Water": (
                2305196,
                "",
                "",
            ),
            "Elec (all meters) - Coincident Peak - Exterior Usage": (
                2305197,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use": (
                2306001,
                "",
                "",
            ),
            "Fuel (all meters) - Peak Demand": (
                2306002,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Lights": (
                2306006,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Task Lights": (
                2306007,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Misc Equip": (
                2306008,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Space Heating": (
                2306009,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Space Cooling": (
                2306010,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Heat Rejection": (
                2306011,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Pumps & Aux": (
                2306012,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Ventilation Fans": (
                2306013,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Refrigeration Display": (
                2306014,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Ht Pump Supplemental Heat": (
                2306015,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Domestic Hot Water": (
                2306016,
                "",
                "",
            ),
            "Fuel (all meters) - Fuel Use - Exterior Usage": (
                2306017,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Lights": (
                2306019,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Task Lights": (
                2306020,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Misc Equip": (
                2306021,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Space Heating": (
                2306022,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Space Cooling": (
                2306023,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Heat Rejection": (
                2306024,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Pumps & Aux": (
                2306025,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Ventilation Fans": (
                2306026,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Refrigeration Display": (
                2306027,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Ht Pump Supplemental Heat": (
                2306028,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Domestic Hot Water": (
                2306029,
                "",
                "",
            ),
            "Fuel (all meters) - Peak - Exterior Usage": (
                2306030,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Lights": (
                2306186,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Task Lights": (
                2306187,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Misc Equip": (
                2306188,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Space Heating": (
                2306189,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Space Cooling": (
                2306190,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Heat Rejection": (
                2306191,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Pumps & Aux": (
                2306192,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Ventilation Fans": (
                2306193,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Refrigeration Display": (
                2306194,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Ht Pump Supplemental Heat": (
                2306195,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Domestic Hot Water": (
                2306196,
                "",
                "",
            ),
            "Fuel (all meters) - Coincident Peak - Exterior Usage": (
                2306197,
                "",
                "",
            ),
            "Steam (all meters) - Energy": (
                2307001,
                "",
                "",
            ),
            "Steam (all meters) - Peak Demand": (
                2307002,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Lights": (
                2307006,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Task Lights": (
                2307007,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Misc Equip": (
                2307008,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Space Heating": (
                2307009,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Space Cooling": (
                2307010,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Heat Rejection": (
                2307011,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Pumps & Aux": (
                2307012,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Ventilation Fans": (
                2307013,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Refrigeration Display": (
                2307014,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Ht Pump Supplemental Heat": (
                2307015,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Domestic Hot Water": (
                2307016,
                "",
                "",
            ),
            "Steam (all meters) - Energy - Exterior Usage": (
                2307017,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Lights": (
                2307019,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Task Lights": (
                2307020,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Misc Equip": (
                2307021,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Space Heating": (
                2307022,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Space Cooling": (
                2307023,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Heat Rejection": (
                2307024,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Pumps & Aux": (
                2307025,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Ventilation Fans": (
                2307026,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Refrigeration Display": (
                2307027,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Ht Pump Supplemental Heat": (
                2307028,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Domestic Hot Water": (
                2307029,
                "",
                "",
            ),
            "Steam (all meters) - Peak - Exterior Usage": (
                2307030,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Lights": (
                2307186,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Task Lights": (
                2307187,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Misc Equip": (
                2307188,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Space Heating": (
                2307189,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Space Cooling": (
                2307190,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Heat Rejection": (
                2307191,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Pumps & Aux": (
                2307192,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Ventilation Fans": (
                2307193,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Refrigeration Display": (
                2307194,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Ht Pump Supplemental Heat": (
                2307195,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Domestic Hot Water": (
                2307196,
                "",
                "",
            ),
            "Steam (all meters) - Coincident Peak - Exterior Usage": (
                2307197,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy": (
                2308001,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak Demand": (
                2308002,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Lights": (
                2308006,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Task Lights": (
                2308007,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Misc Equip": (
                2308008,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Space Heating": (
                2308009,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Space Cooling": (
                2308010,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Heat Rejection": (
                2308011,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Pumps & Aux": (
                2308012,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Ventilation Fans": (
                2308013,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Refrigeration Display": (
                2308014,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Ht Pump Supplemental Heat": (
                2308015,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Domestic Hot Water": (
                2308016,
                "",
                "",
            ),
            "Chilled Water (all meters) - Energy - Exterior Usage": (
                2308017,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Lights": (
                2308019,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Task Lights": (
                2308020,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Misc Equip": (
                2308021,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Space Heating": (
                2308022,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Space Cooling": (
                2308023,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Heat Rejection": (
                2308024,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Pumps & Aux": (
                2308025,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Ventilation Fans": (
                2308026,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Refrigeration Display": (
                2308027,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Ht Pump Supplemental Heat": (
                2308028,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Domestic Hot Water": (
                2308029,
                "",
                "",
            ),
            "Chilled Water (all meters) - Peak - Exterior Usage": (
                2308030,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Lights": (
                2308186,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Task Lights": (
                2308187,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Misc Equip": (
                2308188,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Space Heating": (
                2308189,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Space Cooling": (
                2308190,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Heat Rejection": (
                2308191,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Pumps & Aux": (
                2308192,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Ventilation Fans": (
                2308193,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Refrigeration Display": (
                2308194,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Ht Pump Supplemental Heat": (
                2308195,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Domestic Hot Water": (
                2308196,
                "",
                "",
            ),
            "Chilled Water (all meters) - Coincident Peak - Exterior Usage": (
                2308197,
                "",
                "",
            ),
        }
        string_requests = {}
        for fuel_meter_name in self.fuel_meter_names:
            string_requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use Units"] = (
                2310001,
                fuel_meter_name,
                "",
            )
            string_requests[f"Fuel (meter {fuel_meter_name}) - Peak Demand Units"] = (
                2310002,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use"] = (
                2310003,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak Demand"] = (
                2310004,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Lights"] = (
                2310008,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Task Lights"] = (
                2310009,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Misc Equip"] = (
                2310010,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Space Heating"] = (
                2310011,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Space Cooling"] = (
                2310012,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Heat Rejection"] = (
                2310013,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Pumps & Aux"] = (
                2310014,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Ventilation Fans"
            ] = (
                2310015,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Refrigeration Display"
            ] = (2310016, fuel_meter_name, "")
            requests[
                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Ht Pump Supplemental Heat"
            ] = (
                2310017,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Domestic Hot Water"
            ] = (
                2310018,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Fuel Use - Exterior Usage"] = (
                2310019,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Lights"] = (
                2310021,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Task Lights"] = (
                2310022,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Misc Equip"] = (
                2310023,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Space Heating"] = (
                2310024,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Space Cooling"] = (
                2310025,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Heat Rejection"] = (
                2310026,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Pumps & Aux"] = (
                2310027,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Ventilation Fans"] = (
                2310028,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Peak - Refrigeration Display"
            ] = (
                2310029,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Peak - Ht Pump Supplemental Heat"
            ] = (
                2310030,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Domestic Hot Water"] = (
                2310031,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Peak - Exterior Usage"] = (
                2310032,
                fuel_meter_name,
                "",
            )
            requests[f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Lights"] = (
                2310202,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Task Lights"
            ] = (
                2310203,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Misc Equip"
            ] = (
                2310204,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Space Heating"
            ] = (
                2310205,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Space Cooling"
            ] = (
                2310206,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Heat Rejection"
            ] = (
                2310207,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Pumps & Aux"
            ] = (
                2310208,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Ventilation Fans"
            ] = (
                2310209,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Refrigeration Display"
            ] = (
                2310210,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Ht Pump Supplemental Heat"
            ] = (
                2310211,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Domestic Hot Water"
            ] = (
                2310212,
                fuel_meter_name,
                "",
            )
            requests[
                f"Fuel (meter {fuel_meter_name}) - Coincident Peak - Exterior Usage"
            ] = (
                2310213,
                fuel_meter_name,
                "",
            )

        for elec_generator_name in self.elec_generator_names:
            elec_generator = self.bdl_obj_instances[elec_generator_name]
            if (
                elec_generator
                and elec_generator.get_inp(BDL_ElecGeneratorKeywords.TYPE)
                == BDL_ElecGeneratorTypes.PV_ARRAY
            ):
                requests[f"PV Array {elec_generator_name} - Energy"] = (
                    2303259,
                    elec_generator_name,
                    "",
                )
                requests[f"PV Array {elec_generator_name} - Peak Demand"] = (
                    2303260,
                    elec_generator_name,
                    "",
                )

        for utility_rate_name in self.utility_rate_names:
            requests[f"{utility_rate_name} - Total Charges"] = (
                3005013,
                utility_rate_name,
                "",
            )

        return requests, string_requests

    def populate_data_group(self):
        """Populate the RMD data structure."""
        self.weather_obj.populate_data_group()
        self.weather_obj.insert_to_rpd()

        self.rmd_data_structure = {
            key: value
            for key, value in {
                "id": self.obj_id,
                "type": self.type,
                "weather": self.weather,
                "calendar": self.calendar,
                "measured_infiltration_pressure_difference": self.measured_infiltration_pressure_difference,
                "is_measured_infiltration_based_on_test": self.is_measured_infiltration_based_on_test,
                "altitude": self.altitude,
                "site_zone_type": self.site_zone_type,
                "buildings": self.buildings,
                "schedules": self.schedules,
                "constructions": self.constructions,
                "materials": self.materials,
                "fluid_loops": self.fluid_loops,
                "service_water_heating_distribution_systems": self.service_water_heating_distribution_systems,
                "service_water_heating_equipment": self.service_water_heating_equipment,
                "service_water_heating_uses": self.service_water_heating_uses,
                "pumps": self.pumps,
                "boilers": self.boilers,
                "chillers": self.chillers,
                "heat_rejections": self.heat_rejections,
                "external_fluid_sources": self.external_fluid_sources,
                "model_output": self.model_output,
            }.items()
            if value is not None
        }

    def insert_to_rpd(self):
        """Insert RMD object into the RPD data structure."""
        self.rpd.ruleset_model_descriptions.append(self.rmd_data_structure)


class Weather:
    def __init__(self, rmd):
        self.rmd = rmd

        self.data_structure = {}

        self.notes = None
        self.ground_temperature_schedule = None
        self.file_name = None
        self.data_source_type = None
        self.climate_zone = None
        self.cooling_dry_bulb_design_day_type = None
        self.cooling_wet_bulb_design_day_type = None
        self.heating_dry_bulb_design_day_type = None

    def __repr__(self):
        return "Weather()"

    def populate_data_group(self):
        no_children_attributes = [
            "notes",
            "ground_temperature_schedule",
            "file_name",
            "data_source_type",
            "climate_zone",
            "cooling_dry_bulb_design_day_type",
            "cooling_wet_bulb_design_day_type",
            "heating_dry_bulb_design_day_type",
        ]
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert Weather object into the RPD data structure."""
        self.rmd.weather = self.data_structure


class OutputInstance:
    """Class to represent an output instance in the RPD data structure."""

    def __init__(self, rmd):
        self.rmd = rmd

        self.data_structure = {}

        self.output_instance_id = f"{rmd.obj_id} Output"
        self.reporting_name = None
        self.notes = None

        # Initialize attributes
        self.unmet_load_hours = None
        self.unmet_load_hours_heating = None
        self.unmet_occupied_load_hours_heating = None
        self.unmet_load_hours_cooling = None
        self.unmet_occupied_load_hours_cooling = None
        # self.building_peak_heating_load = None
        self.building_peak_cooling_load = None
        self.annual_source_results = []
        self.annual_end_use_results = []

    def __repr__(self):
        return f"OutputInstance()"

    def populate_data_elements(self, output_data):
        self.unmet_load_hours_heating = output_data.get("Unmet Heating Load Hours")
        self.unmet_load_hours_cooling = output_data.get("Unmet Cooling Load Hours")
        self.building_peak_cooling_load = output_data.get("Building Peak Cooling Load")
        # self.building_peak_heating_load = output_data.get("Building Peak Heating Load")

        energy_source_types = set()

        # Populate the set of unique energy sources in the model
        if output_data.get("Elec (all meters) - Elec Use"):
            energy_source_types.add(EnergySourceOptions.ELECTRICITY)
        for fuel_meter_name in self.rmd.fuel_meter_names:
            fuel_meter = self.rmd.bdl_obj_instances.get(fuel_meter_name)
            if fuel_meter:
                energy_source_types.add(fuel_meter.get_inp(BDL_FuelMeterKeywords.TYPE))
        if self.rmd.steam_meter_names:
            energy_source_types.add(EnergySourceOptions.PURCHASED_HOT_WATER)
        if self.rmd.chilled_water_meter_names:
            energy_source_types.add(EnergySourceOptions.PURCHASED_CHILLED_WATER)
        if self.rmd.elec_generator_names:
            generators = [
                self.rmd.bdl_obj_instances.get(generator_name)
                for generator_name in self.rmd.elec_generator_names
            ]
            if any(
                generator.get_inp(BDL_ElecGeneratorKeywords.TYPE)
                == BDL_ElecGeneratorTypes.PV_ARRAY
                for generator in generators
            ):
                energy_source_types.add(EnergySourceOptions.ON_SITE_RENEWABLES)

        for energy_source in energy_source_types:
            source_result = SourceResult(self, energy_source)
            source_result.populate_data_elements(output_data)
            source_result.populate_data_group()
            source_result.insert_to_rpd()

    def populate_data_group(self):
        self.data_structure["id"] = self.output_instance_id

        source_result_attributes = [
            "reporting_name",
            "notes",
            "unmet_load_hours",
            "unmet_load_hours_heating",
            "unmet_occupied_load_hours_heating",
            "unmet_load_hours_cooling",
            "unmet_occupied_load_hours_cooling",
            "annual_source_results",
            # "building_peak_heating_load",
            "building_peak_cooling_load",
            "annual_end_use_results",
        ]
        for attr in source_result_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert OutputInstance object into the RPD data structure."""
        self.rmd.model_output = self.data_structure


class SourceResult:
    """Class to represent a source result in the RPD data structure."""

    END_USES_IN_DOE2 = [
        EndUseOptions.INTERIOR_LIGHTING,
        EndUseOptions.MISC_EQUIPMENT,
        EndUseOptions.SPACE_HEATING,
        EndUseOptions.SPACE_COOLING,
        EndUseOptions.HEAT_REJECTION,
        EndUseOptions.PUMPS,
        EndUseOptions.FANS_INTERIOR_VENTILATION,
        EndUseOptions.REFRIGERATION_EQUIPMENT,
        EndUseOptions.HEAT_PUMP_SUPPLEMENTAL_HEATING,
        EndUseOptions.SERVICE_WATER_HEATING,
    ]

    def __init__(self, output_instance, energy_source_type):
        self.rmd = output_instance.rmd
        self.output_instance = output_instance
        self.energy_source_type = energy_source_type

        self.data_structure = {}

        self.reporting_name = None
        self.notes = None
        self.energy_source = None
        self.annual_consumption = None
        self.annual_demand = None
        self.annual_cost = None

    def __repr__(self):
        return f"SourceResult()"

    def populate_data_elements(self, output_data):

        self.energy_source = fuel_type_map.get(self.energy_source_type)

        energy_source_results = {
            "Consumption": {
                "site_energy_use": 0,
                "peak_demand": 0,
                "cost": 0,
            },
            "INTERIOR_LIGHTING": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "SPACE_HEATING": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "HEAT_PUMP_SUPPLEMENTAL_HEATING": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "SPACE_COOLING": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "PUMPS": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "HEAT_REJECTION": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "FANS_INTERIOR_VENTILATION": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "REFRIGERATION_EQUIPMENT": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "SERVICE_WATER_HEATING": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
            "MISC_EQUIPMENT": {
                "site_energy_use": 0,
                "coincident_demand": 0,
                "non_coincident_demand": 0,
            },
        }

        source_results = copy.deepcopy(energy_source_results)
        if self.energy_source_type == EnergySourceOptions.ELECTRICITY:
            source_results["Consumption"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use"
            )
            source_results["Consumption"]["peak_demand"] = output_data.get(
                "Elec (all meters) - Peak Demand"
            )
            source_results["Consumption"]["cost"] = sum(
                output_data.get(f"{utility_rate_name} - Total Charges")
                for utility_rate_name in self.rmd.utility_rate_names
                if self.rmd.bdl_obj_instances.get(utility_rate_name).get_inp(
                    BDL_UtilityRateKeywords.TYPE
                )
                == BDL_UtilityRateTypes.ELECTRICITY
            )

            source_results["INTERIOR_LIGHTING"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["non_coincident_demand"] = (
                output_data.get("Elec (all meters) - Peak - Lights")
            )

            source_results["MISC_EQUIPMENT"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["non_coincident_demand"] = output_data.get(
                "Elec (all meters) - Peak - Misc Equip"
            )

            source_results["SPACE_HEATING"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Space Heating"
            )
            source_results["SPACE_HEATING"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Space Heating"
            )
            source_results["SPACE_HEATING"]["non_coincident_demand"] = output_data.get(
                "Elec (all meters) - Peak - Space Heating"
            )

            source_results["SPACE_COOLING"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Space Cooling"
            )
            source_results["SPACE_COOLING"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Space Cooling"
            )
            source_results["SPACE_COOLING"]["non_coincident_demand"] = output_data.get(
                "Elec (all meters) - Peak - Space Cooling"
            )

            source_results["HEAT_REJECTION"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["non_coincident_demand"] = output_data.get(
                "Elec (all meters) - Peak - Heat Rejection"
            )

            source_results["PUMPS"]["site_energy_use"] = output_data.get(
                "Elec (all meters) - Elec Use - Pumps & Aux"
            )
            source_results["PUMPS"]["coincident_demand"] = output_data.get(
                "Elec (all meters) - Coincident Peak - Pumps & Aux"
            )
            source_results["PUMPS"]["non_coincident_demand"] = output_data.get(
                "Elec (all meters) - Peak - Pumps & Aux"
            )

            source_results["FANS_INTERIOR_VENTILATION"]["site_energy_use"] = (
                output_data.get("Elec (all meters) - Elec Use - Ventilation Fans")
            )
            source_results["FANS_INTERIOR_VENTILATION"]["coincident_demand"] = (
                output_data.get(
                    "Elec (all meters) - Coincident Peak - Ventilation Fans"
                )
            )
            source_results["FANS_INTERIOR_VENTILATION"]["non_coincident_demand"] = (
                output_data.get("Elec (all meters) - Peak - Ventilation Fans")
            )

            source_results["REFRIGERATION_EQUIPMENT"]["site_energy_use"] = (
                output_data.get("Elec (all meters) - Elec Use - Refrigeration Display")
            )
            source_results["REFRIGERATION_EQUIPMENT"]["coincident_demand"] = (
                output_data.get(
                    "Elec (all meters) - Coincident Peak - Refrigeration Display"
                )
            )
            source_results["REFRIGERATION_EQUIPMENT"]["non_coincident_demand"] = (
                output_data.get("Elec (all meters) - Peak - Refrigeration Display")
            )

            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["site_energy_use"] = (
                output_data.get(
                    "Elec (all meters) - Elec Use - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Elec (all meters) - Coincident Peak - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                "non_coincident_demand"
            ] = output_data.get("Elec (all meters) - Peak - Ht Pump Supplemental Heat")

            source_results["SERVICE_WATER_HEATING"]["site_energy_use"] = (
                output_data.get("Elec (all meters) - Elec Use - Domestic Hot Water")
            )
            source_results["SERVICE_WATER_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Elec (all meters) - Coincident Peak - Domestic Hot Water"
                )
            )
            source_results["SERVICE_WATER_HEATING"]["non_coincident_demand"] = (
                output_data.get("Elec (all meters) - Peak - Domestic Hot Water")
            )

            for category in source_results:
                for metric in source_results[category]:
                    if metric in ["site_energy_use", "peak_demand"]:
                        source_results[category][metric] *= 3412.969482

        elif self.energy_source_type == EnergySourceOptions.PURCHASED_HOT_WATER:
            source_results["Consumption"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy"
            )
            source_results["Consumption"]["peak_demand"] = output_data.get(
                "Steam (all meters) - Peak Demand"
            )
            source_results["Consumption"]["cost"] = sum(
                output_data.get(f"{utility_rate_name} - Total Charges")
                for utility_rate_name in self.rmd.utility_rate_names
                if self.rmd.bdl_obj_instances.get(utility_rate_name).get_inp(
                    BDL_UtilityRateKeywords.TYPE
                )
                == BDL_UtilityRateTypes.STEAM
            )

            source_results["INTERIOR_LIGHTING"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["non_coincident_demand"] = (
                output_data.get("Steam (all meters) - Peak - Lights")
            )

            source_results["MISC_EQUIPMENT"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["non_coincident_demand"] = output_data.get(
                "Steam (all meters) - Peak - Misc Equip"
            )

            source_results["SPACE_HEATING"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Space Heating"
            )
            source_results["SPACE_HEATING"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Space Heating"
            )
            source_results["SPACE_HEATING"]["non_coincident_demand"] = output_data.get(
                "Steam (all meters) - Peak - Space Heating"
            )

            source_results["SPACE_COOLING"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Space Cooling"
            )
            source_results["SPACE_COOLING"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Space Cooling"
            )
            source_results["SPACE_COOLING"]["non_coincident_demand"] = output_data.get(
                "Steam (all meters) - Peak - Space Cooling"
            )

            source_results["HEAT_REJECTION"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["non_coincident_demand"] = output_data.get(
                "Steam (all meters) - Peak - Heat Rejection"
            )

            source_results["PUMPS"]["site_energy_use"] = output_data.get(
                "Steam (all meters) - Energy - Pumps & Aux"
            )
            source_results["PUMPS"]["coincident_demand"] = output_data.get(
                "Steam (all meters) - Coincident Peak - Pumps & Aux"
            )
            source_results["PUMPS"]["non_coincident_demand"] = output_data.get(
                "Steam (all meters) - Peak - Pumps & Aux"
            )

            source_results["FANS_INTERIOR_VENTILATION"]["site_energy_use"] = (
                output_data.get("Steam (all meters) - Energy - Ventilation Fans")
            )
            source_results["FANS_INTERIOR_VENTILATION"]["coincident_demand"] = (
                output_data.get(
                    "Steam (all meters) - Coincident Peak - Ventilation Fans"
                )
            )
            source_results["FANS_INTERIOR_VENTILATION"]["non_coincident_demand"] = (
                output_data.get("Steam (all meters) - Peak - Ventilation Fans")
            )

            source_results["REFRIGERATION_EQUIPMENT"]["site_energy_use"] = (
                output_data.get("Steam (all meters) - Energy - Refrigeration Display")
            )
            source_results["REFRIGERATION_EQUIPMENT"]["coincident_demand"] = (
                output_data.get(
                    "Steam (all meters) - Coincident Peak - Refrigeration Display"
                )
            )
            source_results["REFRIGERATION_EQUIPMENT"]["non_coincident_demand"] = (
                output_data.get("Steam (all meters) - Peak - Refrigeration Display")
            )

            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["site_energy_use"] = (
                output_data.get(
                    "Steam (all meters) - Energy - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Steam (all meters) - Coincident Peak - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                "non_coincident_demand"
            ] = output_data.get("Steam (all meters) - Peak - Ht Pump Supplemental Heat")

            source_results["SERVICE_WATER_HEATING"]["site_energy_use"] = (
                output_data.get("Steam (all meters) - Energy - Domestic Hot Water")
            )
            source_results["SERVICE_WATER_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Steam (all meters) - Coincident Peak - Domestic Hot Water"
                )
            )
            source_results["SERVICE_WATER_HEATING"]["non_coincident_demand"] = (
                output_data.get("Steam (all meters) - Peak - Domestic Hot Water")
            )

        elif self.energy_source_type == EnergySourceOptions.PURCHASED_CHILLED_WATER:
            source_results["Consumption"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy"
            )
            source_results["Consumption"]["peak_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak Demand"
            )
            source_results["Consumption"]["cost"] = sum(
                output_data.get(f"{utility_rate_name} - Total Charges")
                for utility_rate_name in self.rmd.utility_rate_names
                if self.rmd.bdl_obj_instances.get(utility_rate_name).get_inp(
                    BDL_UtilityRateKeywords.TYPE
                )
                == BDL_UtilityRateTypes.CHILLED_WATER
            )

            source_results["INTERIOR_LIGHTING"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Lights"
            )
            source_results["INTERIOR_LIGHTING"]["non_coincident_demand"] = (
                output_data.get("Chilled Water (all meters) - Peak - Lights")
            )

            source_results["MISC_EQUIPMENT"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Misc Equip"
            )
            source_results["MISC_EQUIPMENT"]["non_coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak - Misc Equip"
            )

            source_results["SPACE_HEATING"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Space Heating"
            )
            source_results["SPACE_HEATING"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Space Heating"
            )
            source_results["SPACE_HEATING"]["non_coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak - Space Heating"
            )

            source_results["SPACE_COOLING"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Space Cooling"
            )
            source_results["SPACE_COOLING"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Space Cooling"
            )
            source_results["SPACE_COOLING"]["non_coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak - Space Cooling"
            )

            source_results["HEAT_REJECTION"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Heat Rejection"
            )
            source_results["HEAT_REJECTION"]["non_coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak - Heat Rejection"
            )

            source_results["PUMPS"]["site_energy_use"] = output_data.get(
                "Chilled Water (all meters) - Energy - Pumps & Aux"
            )
            source_results["PUMPS"]["coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Coincident Peak - Pumps & Aux"
            )
            source_results["PUMPS"]["non_coincident_demand"] = output_data.get(
                "Chilled Water (all meters) - Peak - Pumps & Aux"
            )

            source_results["FANS_INTERIOR_VENTILATION"]["site_energy_use"] = (
                output_data.get(
                    "Chilled Water (all meters) - Energy - Ventilation Fans"
                )
            )
            source_results["FANS_INTERIOR_VENTILATION"]["coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Coincident Peak - Ventilation Fans"
                )
            )
            source_results["FANS_INTERIOR_VENTILATION"]["non_coincident_demand"] = (
                output_data.get("Chilled Water (all meters) - Peak - Ventilation Fans")
            )

            source_results["REFRIGERATION_EQUIPMENT"]["site_energy_use"] = (
                output_data.get(
                    "Chilled Water (all meters) - Energy - Refrigeration Display"
                )
            )
            source_results["REFRIGERATION_EQUIPMENT"]["coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Coincident Peak - Refrigeration Display"
                )
            )
            source_results["REFRIGERATION_EQUIPMENT"]["non_coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Peak - Refrigeration Display"
                )
            )

            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["site_energy_use"] = (
                output_data.get(
                    "Chilled Water (all meters) - Energy - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Coincident Peak - Ht Pump Supplemental Heat"
                )
            )
            source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                "non_coincident_demand"
            ] = output_data.get(
                "Chilled Water (all meters) - Peak - Ht Pump Supplemental Heat"
            )

            source_results["SERVICE_WATER_HEATING"]["site_energy_use"] = (
                output_data.get(
                    "Chilled Water (all meters) - Energy - Domestic Hot Water"
                )
            )
            source_results["SERVICE_WATER_HEATING"]["coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Coincident Peak - Domestic Hot Water"
                )
            )
            source_results["SERVICE_WATER_HEATING"]["non_coincident_demand"] = (
                output_data.get(
                    "Chilled Water (all meters) - Peak - Domestic Hot Water"
                )
            )

        elif self.energy_source_type == EnergySourceOptions.ON_SITE_RENEWABLES:
            source_results["Consumption"]["site_energy_use"] = sum(
                output_data.get(f"Elec (meter {generator_name}) - Elec Use")
                for generator_name in self.rmd.elec_generator_names
                if self.rmd.bdl_obj_instances.get(generator_name).get_inp(
                    BDL_ElecGeneratorKeywords.TYPE
                )
                == BDL_ElecGeneratorTypes.PV_ARRAY
            )
            source_results["Consumption"]["cost"] = sum(
                output_data.get(f"{utility_rate_name} - Total Charges")
                for utility_rate_name in self.rmd.utility_rate_names
                if self.rmd.bdl_obj_instances.get(utility_rate_name).get_inp(
                    BDL_UtilityRateKeywords.TYPE
                )
                == BDL_UtilityRateTypes.ELECTRIC_SALE
            )
            if len(self.rmd.elec_generator_names) == 1:
                source_results["Consumption"]["peak_demand"] = output_data.get(
                    f"Elec (meter {self.rmd.elec_generator_names[0]}) - Peak Demand"
                )

        else:
            # Sum results from utility rates that have the same energy source type
            source_results["Consumption"]["cost"] += sum(
                output_data.get(f"{utility_rate_name} - Total Charges")
                for utility_rate_name in self.rmd.utility_rate_names
                if self.rmd.bdl_obj_instances.get(utility_rate_name).get_inp(
                    BDL_UtilityRateKeywords.TYPE
                )
                == self.energy_source_type
            )
            # Sum results from fuel meters that have the same type
            for fuel_meter_name in self.rmd.fuel_meter_names:
                fuel_meter = self.rmd.bdl_obj_instances.get(fuel_meter_name)
                if fuel_meter:
                    meter_type = fuel_meter.get_inp(BDL_FuelMeterKeywords.TYPE)
                    if meter_type and meter_type == self.energy_source_type:
                        source_results["Consumption"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["INTERIOR_LIGHTING"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Lights"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["INTERIOR_LIGHTING"][
                            "non_coincident_demand"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Lights"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["MISC_EQUIPMENT"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Misc Equip"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["MISC_EQUIPMENT"]["non_coincident_demand"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Misc Equip"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["SPACE_HEATING"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Space Heating"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["SPACE_HEATING"]["non_coincident_demand"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Space Heating"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["SPACE_COOLING"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Space Cooling"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["SPACE_COOLING"]["non_coincident_demand"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Space Cooling"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["HEAT_REJECTION"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Heat Rejection"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["HEAT_REJECTION"]["non_coincident_demand"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Heat Rejection"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["PUMPS"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Pumps & Aux"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["PUMPS"]["non_coincident_demand"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Pumps & Aux"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["FANS_INTERIOR_VENTILATION"][
                            "site_energy_use"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Ventilation Fans"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["FANS_INTERIOR_VENTILATION"][
                            "non_coincident_demand"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Ventilation Fans"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["REFRIGERATION_EQUIPMENT"][
                            "site_energy_use"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Refrigeration Display"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["REFRIGERATION_EQUIPMENT"][
                            "non_coincident_demand"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Refrigeration Display"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                            "site_energy_use"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Ht Pump Supplemental Heat"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                            "non_coincident_demand"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Ht Pump Supplemental Heat"
                            )
                            * fuel_meter.thermal_value
                        )

                        source_results["SERVICE_WATER_HEATING"]["site_energy_use"] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Fuel Use - Domestic Hot Water"
                            )
                            * fuel_meter.thermal_value
                        )
                        source_results["SERVICE_WATER_HEATING"][
                            "non_coincident_demand"
                        ] += (
                            output_data.get(
                                f"Fuel (meter {fuel_meter_name}) - Peak - Domestic Hot Water"
                            )
                            * fuel_meter.thermal_value
                        )

            if len(self.rmd.fuel_meter_names) == 1:
                # Only populate peak demand and coincident demand if there is only one fuel meter
                fuel_meter = self.rmd.bdl_obj_instances.get(
                    self.rmd.fuel_meter_names[0]
                )
                source_results["Consumption"]["peak_demand"] = (
                    output_data.get(f"Fuel (all meters) - Peak Demand")
                    * fuel_meter.thermal_value
                )

                source_results["INTERIOR_LIGHTING"]["coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Coincident Peak - Lights")
                    * fuel_meter.thermal_value
                )

                source_results["MISC_EQUIPMENT"]["coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Coincident Peak - Misc Equip")
                    * fuel_meter.thermal_value
                )

                source_results["SPACE_HEATING"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Space Heating"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["SPACE_COOLING"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Space Cooling"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["HEAT_REJECTION"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Heat Rejection"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["PUMPS"]["coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Coincident Peak - Pumps & Aux")
                    * fuel_meter.thermal_value
                )

                source_results["FANS_INTERIOR_VENTILATION"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Ventilation Fans"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["REFRIGERATION_EQUIPMENT"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Refrigeration Display"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                    "coincident_demand"
                ] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Ht Pump Supplemental Heat"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["SERVICE_WATER_HEATING"]["coincident_demand"] += (
                    output_data.get(
                        "Fuel (all meters) - Coincident Peak - Domestic Hot Water"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["INTERIOR_LIGHTING"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Lights")
                    * fuel_meter.thermal_value
                )

                source_results["MISC_EQUIPMENT"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Misc Equip")
                    * fuel_meter.thermal_value
                )

                source_results["SPACE_HEATING"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Space Heating")
                    * fuel_meter.thermal_value
                )

                source_results["SPACE_COOLING"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Space Cooling")
                    * fuel_meter.thermal_value
                )

                source_results["HEAT_REJECTION"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Heat Rejection")
                    * fuel_meter.thermal_value
                )

                source_results["PUMPS"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Pumps & Aux")
                    * fuel_meter.thermal_value
                )

                source_results["FANS_INTERIOR_VENTILATION"][
                    "non_coincident_demand"
                ] += (
                    output_data.get("Fuel (all meters) - Peak - Ventilation Fans")
                    * fuel_meter.thermal_value
                )

                source_results["REFRIGERATION_EQUIPMENT"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Refrigeration Display")
                    * fuel_meter.thermal_value
                )

                source_results["HEAT_PUMP_SUPPLEMENTAL_HEATING"][
                    "non_coincident_demand"
                ] += (
                    output_data.get(
                        "Fuel (all meters) - Peak - Ht Pump Supplemental Heat"
                    )
                    * fuel_meter.thermal_value
                )

                source_results["SERVICE_WATER_HEATING"]["non_coincident_demand"] += (
                    output_data.get("Fuel (all meters) - Peak - Domestic Hot Water")
                    * fuel_meter.thermal_value
                )

        self.annual_consumption = source_results["Consumption"]["site_energy_use"]
        self.annual_demand = source_results["Consumption"]["peak_demand"]
        self.annual_cost = source_results["Consumption"]["cost"]

        for end_use_type in self.END_USES_IN_DOE2:
            end_use_result = EndUseResult(
                self.output_instance,
                self.energy_source_type,
                end_use_type,
                source_results,
            )
            end_use_result.populate_data_elements()
            end_use_result.populate_data_group()
            end_use_result.insert_to_rpd()

    def populate_data_group(self):
        self.data_structure["id"] = self.energy_source_type

        source_result_attributes = [
            "reporting_name",
            "notes",
            "energy_source",
            "annual_consumption",
            "annual_demand",
            "annual_cost",
        ]
        for attr in source_result_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert the energy source result into the RPD data structure."""
        self.output_instance.annual_source_results.append(self.data_structure)


class EndUseResult:
    """Class to represent an end use result in the RPD data structure."""

    is_regulated_presets = {
        EndUseOptions.INTERIOR_LIGHTING: True,
        EndUseOptions.SPACE_HEATING: True,
        EndUseOptions.HEAT_PUMP_SUPPLEMENTAL_HEATING: True,
        EndUseOptions.SPACE_COOLING: True,
        EndUseOptions.PUMPS: True,
        EndUseOptions.HEAT_REJECTION: True,
        EndUseOptions.FANS_INTERIOR_VENTILATION: True,
        EndUseOptions.REFRIGERATION_EQUIPMENT: True,
        EndUseOptions.SERVICE_WATER_HEATING: True,
        EndUseOptions.MISC_EQUIPMENT: False,
    }

    def __init__(
        self, output_instance, energy_source_type, end_use_type, source_results
    ):
        self.output_instance = output_instance
        self.energy_source_type = energy_source_type
        self.source_results = source_results

        self.data_structure = {}

        self.reporting_name = None
        self.notes = None
        self.type = end_use_type
        self.energy_source = None
        self.annual_site_energy_use = None
        self.annual_site_coincident_demand = None
        self.annual_site_non_coincident_demand = None
        self.is_regulated = None

    def __repr__(self):
        return f"EndUseResult()"

    def populate_data_elements(self):
        self.energy_source = fuel_type_map.get(self.energy_source_type)
        self.annual_site_energy_use = self.source_results[self.type]["site_energy_use"]
        self.annual_site_coincident_demand = self.source_results[self.type][
            "coincident_demand"
        ]
        self.annual_site_non_coincident_demand = self.source_results[self.type][
            "non_coincident_demand"
        ]
        self.is_regulated = self.is_regulated_presets.get(self.type, False)

    def populate_data_group(self):
        self.data_structure["id"] = self.energy_source_type + "-" + self.type

        source_result_attributes = [
            "reporting_name",
            "notes",
            "type",
            "energy_source",
            "annual_site_energy_use",
            "annual_site_coincident_demand",
            "annual_site_non_coincident_demand",
            "is_regulated",
        ]
        for attr in source_result_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert the end use result into the RPD data structure."""
        self.output_instance.annual_end_use_results.append(self.data_structure)
