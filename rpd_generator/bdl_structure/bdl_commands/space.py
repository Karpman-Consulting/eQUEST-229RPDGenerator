from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
InfiltrationMethodOptions = SchemaEnums.schema_enums["InfiltrationMethodOptions"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]
BDL_InfiltrationAlgorithmOptions = BDLEnums.bdl_enums["InfiltrationAlgorithmOptions"]
BDL_InternalEnergySourceOptions = BDLEnums.bdl_enums["InternalEnergySourceOptions"]


class Space(ChildNode, ParentNode):
    """Space objects represent the spaces in the building model and populate the Space data group in the 229 schema.
    Derived from ChildNode to access the parent FLOOR object through the 'parent' attribute.
    Derived from ParentNode to access the child INTERIOR-WALL, EXTERIOR-WALL, UNDERGROUND-WALL object(s) through the 'children' attribute.
    """

    bdl_command = BDL_Commands.SPACE

    infiltration_algorithm_map = {
        BDL_InfiltrationAlgorithmOptions.NONE: "None",
        BDL_InfiltrationAlgorithmOptions.AIR_CHANGE: "Air Change Method",
        BDL_InfiltrationAlgorithmOptions.RESIDENTIAL: "Residential Infiltration Coefficient",
        BDL_InfiltrationAlgorithmOptions.S_G: "Sherman-Grimsrud Infiltration Method",
        BDL_InfiltrationAlgorithmOptions.CRACK: "Crack Method",
        BDL_InfiltrationAlgorithmOptions.ASHRAE_ENHANCED: "2005 ASHRAE Handbook Fundamentals - Enhanced Infiltration Method",
    }

    energy_source_map = {
        BDL_InternalEnergySourceOptions.GAS: EnergySourceOptions.NATURAL_GAS,
        BDL_InternalEnergySourceOptions.ELECTRIC: EnergySourceOptions.ELECTRICITY,
        BDL_InternalEnergySourceOptions.HOT_WATER: EnergySourceOptions.NONE,
        BDL_InternalEnergySourceOptions.PROCESS: EnergySourceOptions.NONE,
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        ParentNode.__init__(self, u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.space_data_structure = {}
        self.zone = None

        # data elements with children
        self.interior_lighting = []
        self.miscellaneous_equipment = []
        self.service_water_heating_uses = []

        # data elements with no children
        self.floor_area = None
        self.number_of_occupants = None
        self.occupant_multiplier_schedule = None
        self.occupant_sensible_heat_gain = None
        self.occupant_latent_heat_gain = None
        self.status_type = None
        self.function = None
        self.envelope_space_type = None
        self.lighting_space_type = None
        self.ventilation_space_type = None
        self.service_water_heating_space_type = None

    def __repr__(self):
        return f"Space(u_name='{self.u_name}', parent={self.parent})"

    def populate_data_elements(self):
        """Populate data elements that originate from eQUEST's SPACE command"""
        # Populate space data elements
        self.floor_area = self.try_float(self.get_inp(BDL_SpaceKeywords.AREA))
        self.number_of_occupants = self.try_float(
            self.get_inp(BDL_SpaceKeywords.NUMBER_OF_PEOPLE)
        )
        self.occupant_multiplier_schedule = self.get_inp(
            BDL_SpaceKeywords.PEOPLE_SCHEDULE
        )
        self.occupant_sensible_heat_gain = self.try_float(
            self.get_inp(BDL_SpaceKeywords.PEOPLE_HG_SENS)
        )
        self.occupant_latent_heat_gain = self.try_float(
            self.get_inp(BDL_SpaceKeywords.PEOPLE_HG_LAT)
        )

        # Populate interior lighting data elements
        self.populate_interior_lighting_data_elements()

        # Populate miscellaneous equipment data elements
        self.populate_miscellaneous_equipment_data_elements()

        # Populate zone data elements that originate from Space data
        self.zone = self.rmd.space_map.get(self.u_name)
        self.zone.volume = self.try_float(self.get_inp(BDL_SpaceKeywords.VOLUME))
        self.populate_zone_infiltration()

    def populate_data_group(self):
        """Populate schema structure for space object."""

        self.space_data_structure = {
            "id": self.u_name,
            "interior_lighting": self.interior_lighting,
            "miscellaneous_equipment": self.miscellaneous_equipment,
            "service_water_heating_uses": self.service_water_heating_uses,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "floor_area",
            "number_of_occupants",
            "occupant_multiplier_schedule",
            "occupant_sensible_heat_gain",
            "occupant_latent_heat_gain",
            "status_type",
            "function",
            "envelope_space_type",
            "lighting_space_type",
            "ventilation_space_type",
            "service_water_heating_space_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.space_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert space object into the rpd data structure."""
        # find the zone that has the "SPACE" attribute value equal to the space object's u_name
        self.zone.spaces.append(self.space_data_structure)

    def populate_interior_lighting_data_elements(self):
        space_ltg_scheds = self.get_inp(BDL_SpaceKeywords.LIGHTING_SCHEDUL)
        if space_ltg_scheds is not None:
            if not isinstance(space_ltg_scheds, list):
                space_ltg_scheds = [space_ltg_scheds]
            self.standardize_dict_values(
                self.keyword_value_pairs,
                [BDL_SpaceKeywords.LIGHTING_W_AREA, BDL_SpaceKeywords.LIGHTING_KW],
                self.try_length(space_ltg_scheds),
            )

            for i, sched in enumerate(space_ltg_scheds):
                interior_lighting = InteriorLighting(self, i, sched)
                interior_lighting.populate_data_elements()
                interior_lighting.populate_data_group()
                interior_lighting.insert_to_rpd()

    def populate_miscellaneous_equipment_data_elements(self):
        # Populate one instance of miscellaneous equipment for each schedule associated with equipment or internal energy sources
        misc_eq_counter = 0
        space_misc_eq_scheds = self.get_inp(BDL_SpaceKeywords.EQUIP_SCHEDULE)
        space_int_energy_source_scheds = self.get_inp(BDL_SpaceKeywords.SOURCE_SCHEDULE)

        if space_misc_eq_scheds is not None:
            if not isinstance(space_misc_eq_scheds, list):
                space_misc_eq_scheds = [space_misc_eq_scheds]
            self.standardize_dict_values(
                self.keyword_value_pairs,
                [
                    BDL_SpaceKeywords.EQUIPMENT_W_AREA,
                    BDL_SpaceKeywords.EQUIPMENT_KW,
                    BDL_SpaceKeywords.EQUIP_SENSIBLE,
                    BDL_SpaceKeywords.EQUIP_LATENT,
                ],
                self.try_length(space_misc_eq_scheds),
            )

            for i, sched in enumerate(space_misc_eq_scheds):
                misc_eq_counter += 1
                misc_equipment = MiscellaneousEquipment(
                    self, i, misc_eq_counter, sched, "EQUIPMENT"
                )
                misc_equipment.populate_data_elements()
                misc_equipment.populate_data_group()
                misc_equipment.insert_to_rpd()

        if space_int_energy_source_scheds is not None:
            if not isinstance(space_int_energy_source_scheds, list):
                space_int_energy_source_scheds = [space_int_energy_source_scheds]
            self.standardize_dict_values(
                self.keyword_value_pairs,
                [
                    BDL_SpaceKeywords.SOURCE_TYPE,
                    BDL_SpaceKeywords.SOURCE_POWER,
                    BDL_SpaceKeywords.SOURCE_SENSIBLE,
                    BDL_SpaceKeywords.SOURCE_LATENT,
                ],
                self.try_length(space_int_energy_source_scheds),
            )

            for i, sched in enumerate(space_int_energy_source_scheds):
                misc_eq_counter += 1
                misc_equipment = MiscellaneousEquipment(
                    self, i, misc_eq_counter, sched, "INTERNAL_ENERGY_SOURCE"
                )
                misc_equipment.populate_data_elements()
                misc_equipment.populate_data_group()
                misc_equipment.insert_to_rpd()

    def populate_zone_infiltration(self):
        """Populate infiltration data elements for the zone object."""
        self.zone.infil_id = self.u_name + " Infil"
        self.zone.infil_multiplier_schedule = self.get_inp(
            BDL_SpaceKeywords.INF_SCHEDULE
        )
        infiltration_method = self.get_inp(BDL_SpaceKeywords.INF_METHOD)
        self.zone.infil_algorithm_name = self.infiltration_algorithm_map.get(
            infiltration_method
        )
        if infiltration_method == BDL_InfiltrationAlgorithmOptions.AIR_CHANGE:
            flow_per_area = self.try_float(
                self.get_inp(BDL_SpaceKeywords.INF_FLOW_AREA)
            )
            air_changes_per_hour = self.try_float(
                self.get_inp(BDL_SpaceKeywords.AIR_CHANGES_HR)
            )
            if (
                flow_per_area
                and air_changes_per_hour
                and self.zone.volume
                and self.floor_area
            ):
                self.zone.infil_flow_rate = (
                    flow_per_area * self.floor_area
                    + air_changes_per_hour * self.zone.volume / 60
                )
                self.zone.infil_modeling_method = (
                    InfiltrationMethodOptions.WEATHER_DRIVEN
                )
            elif flow_per_area and self.floor_area:
                self.zone.infil_flow_rate = flow_per_area * self.floor_area
                if self.zone.infil_multiplier_schedule:
                    self.zone.infil_modeling_method = (
                        InfiltrationMethodOptions.CONSTANT_SCHEDULED
                    )
                else:
                    self.zone.infil_modeling_method = InfiltrationMethodOptions.CONSTANT
            elif air_changes_per_hour and self.zone.volume:
                self.zone.infil_flow_rate = air_changes_per_hour * self.zone.volume / 60
                self.zone.infil_modeling_method = (
                    InfiltrationMethodOptions.WEATHER_DRIVEN
                )
            elif flow_per_area == 0 and air_changes_per_hour == 0:
                self.zone.infil_flow_rate = 0
                self.zone.infil_modeling_method = (
                    InfiltrationMethodOptions.WEATHER_DRIVEN
                )

        else:
            # infil_flow_rate will not populate if the infiltration method is not AIR-CHANGE
            self.zone.infil_modeling_method = InfiltrationMethodOptions.WEATHER_DRIVEN


class InteriorLighting:

    def __init__(self, parent_space, i, schedule):

        self.parent_space = parent_space
        self.i = i

        self.data_structure = {}

        self.name = None
        # InteriorLighting data elements
        self.reporting_name = None
        self.notes = None
        self.purpose_type = None
        self.power_per_area = None
        self.lighting_multiplier_schedule = schedule
        self.occupancy_control_type = None
        self.daylighting_control_type = None
        self.are_schedules_used_for_modeling_occupancy_control = None
        self.are_schedules_used_for_modeling_daylighting_control = None

    def populate_data_elements(self):
        self.name = f"{self.parent_space.u_name} IntLtg{self.i + 1}"
        int_ltg_lpd = self.parent_space.try_float(
            self.parent_space.try_access_index(
                self.parent_space.get_inp(BDL_SpaceKeywords.LIGHTING_W_AREA), self.i
            )
        )
        int_ltg_power = self.parent_space.try_float(
            self.parent_space.try_access_index(
                self.parent_space.get_inp(BDL_SpaceKeywords.LIGHTING_KW), self.i
            )
        )

        if int_ltg_lpd is not None and int_ltg_power is not None:
            total_lpd = (
                int_ltg_lpd + int_ltg_power * 1000 / self.parent_space.floor_area
            )
        elif int_ltg_lpd is not None:
            total_lpd = int_ltg_lpd
        elif int_ltg_power is not None:
            total_lpd = int_ltg_power * 1000 / self.parent_space.floor_area
        else:
            total_lpd = None

        self.power_per_area = total_lpd

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        int_lighting_data_elements = [
            "reporting_name",
            "notes",
            "purpose_type",
            "power_per_area",
            "lighting_multiplier_schedule",
            "occupancy_control_type",
            "daylighting_control_type",
            "are_schedules_used_for_modeling_occupancy_control",
            "are_schedules_used_for_modeling_daylighting_control",
        ]

        for attr in int_lighting_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert interior lighting object into the rpd data structure."""
        # find the zone that has the "SPACE" attribute value equal to the space object's u_name
        self.parent_space.interior_lighting.append(self.data_structure)


class MiscellaneousEquipment:

    def __init__(self, parent_space, i, n, schedule, equip_type):
        self.parent_space = parent_space
        self.i = i
        self.n = n
        self.equip_type = equip_type

        self.data_structure = {}

        self.name = None
        # MiscellaneousEquipment data elements
        self.reporting_name = None
        self.notes = None
        self.energy_type = None
        self.power = None
        self.multiplier_schedule = schedule
        self.sensible_fraction = None
        self.latent_fraction = None
        self.remaining_fraction_to_loop = None
        self.energy_from_loop = None
        self.type = None
        self.automatic_controlled_percentage = None

    def populate_data_elements(self):
        misc_eq_id = f"{self.parent_space.u_name} MiscEqp{self.n}"

        if self.equip_type == "EQUIPMENT":
            misc_epd = self.parent_space.try_float(
                self.parent_space.try_access_index(
                    self.parent_space.get_inp(BDL_SpaceKeywords.EQUIPMENT_W_AREA),
                    self.i,
                )
            )
            misc_eq_power = self.parent_space.try_float(
                self.parent_space.try_access_index(
                    self.parent_space.get_inp(BDL_SpaceKeywords.EQUIPMENT_KW), self.i
                )
            )
            total_eq_power = (
                misc_eq_power + misc_epd * self.parent_space.floor_area / 1000
                if misc_eq_power is not None
                and misc_epd is not None
                and self.parent_space.floor_area is not None
                else misc_eq_power
            )

            misc_eq_sensible_fraction = self.parent_space.try_float(
                self.parent_space.try_access_index(
                    self.parent_space.get_inp(BDL_SpaceKeywords.EQUIP_SENSIBLE),
                    self.i,
                )
            )
            misc_eq_latent_fraction = self.parent_space.try_float(
                self.parent_space.try_access_index(
                    self.parent_space.get_inp(BDL_SpaceKeywords.EQUIP_LATENT), self.i
                )
            )

            self.name = misc_eq_id
            self.energy_type = EnergySourceOptions.ELECTRICITY
            self.power = total_eq_power
            self.sensible_fraction = misc_eq_sensible_fraction
            self.latent_fraction = misc_eq_latent_fraction

        elif self.equip_type == "INTERNAL_ENERGY_SOURCE":
            source = self.parent_space.try_access_index(
                self.parent_space.get_inp(BDL_SpaceKeywords.SOURCE_TYPE), self.i
            )
            energy_type = self.parent_space.energy_source_map.get(source)

            self.name = misc_eq_id
            self.energy_type = energy_type
            self.power = self.parent_space.try_convert_units(
                self.parent_space.try_float(
                    self.parent_space.try_access_index(
                        self.parent_space.get_inp(BDL_SpaceKeywords.SOURCE_POWER),
                        self.i,
                    )
                ),
                "Btu/hr",
                "kW",
            )

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        misc_equipment_data_elements = [
            "reporting_name",
            "notes",
            "energy_type",
            "power",
            "multiplier_schedule",
            "sensible_fraction",
            "latent_fraction",
            "remaining_fraction_to_loop",
            "energy_from_loop",
            "type",
            "automatic_controlled_percentage",
        ]

        for attr in misc_equipment_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert miscellaneous equipment object into the rpd data structure."""
        self.parent_space.miscellaneous_equipment.append(self.data_structure)
