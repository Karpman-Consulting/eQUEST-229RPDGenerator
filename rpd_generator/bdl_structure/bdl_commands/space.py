from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.artifacts.building_segment import BuildingSegment
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
InfiltrationMethodOptions = SchemaEnums.schema_enums["InfiltrationMethodOptions"]
DaylightingControlOptions = SchemaEnums.schema_enums[
    "LightingDaylightingControlOptions"
]
LightingSpaceOptions = SchemaEnums.schema_enums["LightingSpaceOptions2019ASHRAE901TG37"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]
BDL_InfiltrationAlgorithmOptions = BDLEnums.bdl_enums["InfiltrationAlgorithmOptions"]
BDL_InternalEnergySourceOptions = BDLEnums.bdl_enums["InternalEnergySourceOptions"]
BDL_DaylightingControlOptions = BDLEnums.bdl_enums["DaylightingControlOptions"]


class Space(ChildNode, ParentNode):
    """Space objects represent the spaces in the building model and populate the Space data group in the 229 schema.
    Derived from ChildNode to access the parent FLOOR object through the 'parent' attribute.
    Derived from ParentNode to access the child INTERIOR-WALL, EXTERIOR-WALL, UNDERGROUND-WALL object(s) through the 'children' attribute.
    """

    bdl_command = BDL_Commands.SPACE

    energy_source_map = {
        BDL_InternalEnergySourceOptions.GAS: EnergySourceOptions.NATURAL_GAS,
        BDL_InternalEnergySourceOptions.ELECTRIC: EnergySourceOptions.ELECTRICITY,
        BDL_InternalEnergySourceOptions.HOT_WATER: EnergySourceOptions.NONE,
        BDL_InternalEnergySourceOptions.PROCESS: EnergySourceOptions.NONE,
    }

    lighting_space_map = {
        0: None,
        1: LightingSpaceOptions.ATRIUM_LOW_MEDIUM,
        2: LightingSpaceOptions.ATRIUM_HIGH,
        3: LightingSpaceOptions.AUDIENCE_SEATING_AREA_AUDITORIUM,
        4: LightingSpaceOptions.AUDIENCE_SEATING_AREA_CONVENTION_CENTER,
        5: LightingSpaceOptions.AUDIENCE_SEATING_AREA_EXERCISE_CENTER,
        6: LightingSpaceOptions.AUDIENCE_SEATING_AREA_GYMNASIUM,
        7: LightingSpaceOptions.AUDIENCE_SEATING_AREA_MOTION_PICTURE_THEATER,
        8: LightingSpaceOptions.AUDIENCE_SEATING_AREA_PENITENTIARY,
        9: LightingSpaceOptions.AUDIENCE_SEATING_AREA_PERFORMING_ARTS_THEATER,
        10: LightingSpaceOptions.AUDIENCE_SEATING_AREA_RELIGIOUS_FACILITY,
        11: LightingSpaceOptions.AUDIENCE_SEATING_AREA_SPORTS_ARENA,
        12: LightingSpaceOptions.AUDIENCE_SEATING_AREA_TRANSPORTATION_FACILITY,
        13: LightingSpaceOptions.AUDIENCE_SEATING_AREA_ALL_OTHER,
        14: LightingSpaceOptions.BANKING_ACTIVITY_AREA,
        15: LightingSpaceOptions.CLASSROOM_LECTURE_HALL_TRAINING_ROOM_PENITENTIARY,
        16: LightingSpaceOptions.CLASSROOM_LECTURE_HALL_TRAINING_ROOM_SCHOOL,
        17: LightingSpaceOptions.CLASSROOM_LECTURE_HALL_TRAINING_ROOM_ALL_OTHER,
        18: LightingSpaceOptions.CONFERENCE_MEETING_MULTIPURPOSE_ROOM,
        19: LightingSpaceOptions.CONFINEMENT_CELLS,
        20: LightingSpaceOptions.COPY_PRINT_ROOM,
        21: LightingSpaceOptions.CORRIDOR_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
        22: LightingSpaceOptions.CORRIDOR_HOSPITAL,
        23: LightingSpaceOptions.CORRIDOR_MANUFACTURING_FACILITY,
        24: LightingSpaceOptions.CORRIDOR_ALL_OTHERS,
        25: LightingSpaceOptions.COURT_ROOM,
        26: LightingSpaceOptions.COMPUTER_ROOM,
        27: LightingSpaceOptions.DINING_AREA_PENITENTIARY,
        28: LightingSpaceOptions.DINING_AREA_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
        29: LightingSpaceOptions.DINING_AREA_BAR_LOUNGE_OR_LEISURE_DINING,
        30: LightingSpaceOptions.DINING_AREA_CAFETERIA_OR_FAST_FOOD_DINING,
        31: LightingSpaceOptions.DINING_AREA_FAMILY_DINING,
        32: LightingSpaceOptions.DINING_AREA_ALL_OTHERS,
        33: LightingSpaceOptions.ELECTRICAL_MECHANICAL_ROOM,
        34: LightingSpaceOptions.EMERGENCY_VEHICLE_GARAGE,
        35: LightingSpaceOptions.FOOD_PREPARATION_AREA,
        36: LightingSpaceOptions.GUEST_ROOM,
        37: LightingSpaceOptions.JUDGES_CHAMBERS,
        38: LightingSpaceOptions.DWELLING_UNIT,
        39: LightingSpaceOptions.LABORATORY_EXCEPT_IN_OR_AS_A_CLASSROOM,
        40: LightingSpaceOptions.LAUNDRY_WASHING_AREA,
        41: LightingSpaceOptions.LOADING_DOCK_INTERIOR,
        42: LightingSpaceOptions.LOBBY_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
        43: LightingSpaceOptions.LOBBY_ELEVATOR,
        44: LightingSpaceOptions.LOBBY_HOTEL,
        45: LightingSpaceOptions.LOBBY_MOTION_PICTURE_THEATER,
        46: LightingSpaceOptions.LOBBY_PERFORMING_ARTS_THEATER,
        47: LightingSpaceOptions.LOBBY_ALL_OTHERS,
        48: LightingSpaceOptions.LOCKER_ROOM,
        49: LightingSpaceOptions.LOUNGE_BREAKROOM_HEALTH_CARE_FACILITY,
        50: LightingSpaceOptions.LOUNGE_BREAKROOM_ALL_OTHERS,
        51: LightingSpaceOptions.OFFICE_ENCLOSED,
        52: LightingSpaceOptions.OFFICE_OPEN_PLAN,
        53: LightingSpaceOptions.PARKING_AREA_INTERIOR,
        54: LightingSpaceOptions.PHARMACY_AREA,
        55: LightingSpaceOptions.RESTROOM_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
        56: LightingSpaceOptions.RESTROOM_ALL_OTHERS,
        57: LightingSpaceOptions.SALES_AREA,
        58: LightingSpaceOptions.SEATING_AREA_GENERAL,
        59: LightingSpaceOptions.STAIRWELL,
        60: LightingSpaceOptions.STORAGE_ROOM_HOSPITAL,
        61: LightingSpaceOptions.STORAGE_ROOM_SMALL,
        62: LightingSpaceOptions.STORAGE_ROOM_LARGE,
        63: LightingSpaceOptions.VEHICULAR_MAINTENANCE_AREA,
        64: LightingSpaceOptions.WORKSHOP,
        65: LightingSpaceOptions.ASSISTED_LIVING_FACILITY_CHAPEL,
        66: LightingSpaceOptions.ASSISTED_LIVING_FACILITY_RECREATION_ROOM_COMMON_LIVING_ROOM,
        67: LightingSpaceOptions.CONVENTION_CENTER_EXHIBIT_SPACE,
        68: LightingSpaceOptions.DORMITORY_LIVING_QUARTERS,
        69: LightingSpaceOptions.FIRE_STATION_SLEEPING_QUARTERS,
        70: LightingSpaceOptions.GYMNASIUM_FITNESS_CENTER_EXERCISE_AREA,
        71: LightingSpaceOptions.GYMNASIUM_FITNESS_CENTER_PLAYING_AREA,
        72: LightingSpaceOptions.HEALTHCARE_FACILITY_EMERGENCY_ROOM,
        73: LightingSpaceOptions.HEALTHCARE_FACILITY_EXAM_TREATMENT_ROOM,
        74: LightingSpaceOptions.HEALTHCARE_FACILITY_MEDICAL_SUPPLY_ROOM,
        75: LightingSpaceOptions.HEALTHCARE_FACILITY_NURSERY,
        76: LightingSpaceOptions.HEALTHCARE_FACILITY_NURSES_STATION,
        77: LightingSpaceOptions.HEALTHCARE_FACILITY_OPERATING_ROOM,
        78: LightingSpaceOptions.HEALTHCARE_FACILITY_PATIENT_ROOM,
        79: LightingSpaceOptions.HEALTHCARE_FACILITY_PHYSICAL_THERAPY_ROOM,
        80: LightingSpaceOptions.HEALTHCARE_FACILITY_RECOVERY_ROOM,
        81: LightingSpaceOptions.LIBRARY_READING_AREA,
        82: LightingSpaceOptions.LIBRARY_STACKS,
        83: LightingSpaceOptions.MANUFACTURING_FACILITY_DETAILED_MANUFACTURING_AREA,
        84: LightingSpaceOptions.MANUFACTURING_FACILITY_EQUIPMENTROOM,
        85: LightingSpaceOptions.MANUFACTURING_FACILITY_EXTRA_HIGH_BAY_AREA,
        86: LightingSpaceOptions.MANUFACTURING_FACILITY_HIGH_BAY_AREA,
        87: LightingSpaceOptions.MANUFACTURING_FACILITY_LOW_BAY_AREA,
        88: LightingSpaceOptions.MUSEUM_GENERAL_EXHIBITION_AREA,
        89: LightingSpaceOptions.MUSEUM_RESTORATION_ROOM,
        90: LightingSpaceOptions.POST_OFFICE_SORTING_AREA,
        91: LightingSpaceOptions.RELIGIOUS_FACILITY_FELLOWSHIP_HALL,
        92: LightingSpaceOptions.RELIGIOUS_FACILITY_WORSHIP_PULPIT_CHOIR_AREA,
        93: LightingSpaceOptions.RETAIL_FACILITIES_DRESSING_FITTING_ROOM,
        94: LightingSpaceOptions.RETAIL_FACILITIES_MALL_CONCOURSE,
        95: LightingSpaceOptions.SPORTS_ARENA_PLAYING_AREA_CLASS_I_FACILITY,
        96: LightingSpaceOptions.SPORTS_ARENA_PLAYING_AREA_CLASS_II_FACILITY,
        97: LightingSpaceOptions.SPORTS_ARENA_PLAYING_AREA_CLASS_III_FACILITY,
        98: LightingSpaceOptions.SPORTS_ARENA_PLAYING_AREA_CLASS_IV_FACILITY,
        99: LightingSpaceOptions.TRANSPORTATION_FACILITY_BAGGAGE_CAROUSEL_AREA,
        100: LightingSpaceOptions.TRANSPORTATION_FACILITY_AIRPORT_CONCOURSE,
        101: LightingSpaceOptions.TRANSPORTATION_FACILITY_TICKET_COUNTER,
        102: LightingSpaceOptions.WAREHOUSE_STORAGE_AREA_MEDIUM_TO_BULKY_PALLETIZED_ITEMS,
        103: LightingSpaceOptions.WAREHOUSE_STORAGE_AREA_SMALLER_HAND_CARRIED_ITEMS,
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        ParentNode.__init__(self, u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.space_data_structure = {}

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

        # Store object instances for easy access
        self.zone = self.rmd.space_map.get(self.u_name)

    def __repr__(self):
        return f"Space(u_name='{self.u_name}', parent={self.parent})"

    def populate_data_elements(self):
        """Populate data elements that originate from eQUEST's SPACE command"""

        occupancy_type_list = self.get_inp(BDL_SpaceKeywords.C_901_OCC_TYPE)
        if isinstance(occupancy_type_list, list):
            # Remove undefined occupancy types from the end of the list
            while occupancy_type_list and self.try_int(occupancy_type_list[-1]) == 0:
                occupancy_type_list.pop()

            # Get the unique occupancy types from the SPACE command
            unique_occupancy_types = set(occupancy_type_list)
            if len(unique_occupancy_types) > 1:
                # Iterate through the list of occupancy types after the first
                for i in range(1, len(occupancy_type_list)):
                    self.create_subspace_clones(i)

            # If no subspaces are created, use the SPACE command's floor area for the main space
            else:
                self.floor_area = self.try_float(self.get_inp(BDL_SpaceKeywords.AREA))

        else:
            self.floor_area = self.try_float(self.get_inp(BDL_SpaceKeywords.AREA))

        # Populate space data elements
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

        # Populate infiltration data elements
        self.populate_infiltration()

        # Populate interior lighting data elements in the main space until TODO - lighting can be assigned to subspaces
        self.populate_interior_lighting_data_elements()

        # Populate miscellaneous equipment data elements in the main space until TODO - equipment can be assigned to subspaces
        self.populate_miscellaneous_equipment_data_elements()

        # Populate the set of unique building area types for the project
        building_area_type = self.try_int(
            self.get_inp(BDL_SpaceKeywords.C_901_BLDG_TYPE)
        )
        # if the building area type is new, create a new BuildingSegment object
        if building_area_type not in self.rmd.building_area_types:
            building_segment = BuildingSegment(
                f"{BuildingSegment.lighting_building_area_map.get(building_area_type, 'Default Building Segment')}",
                self.rmd,
                building_area_type,
            )
            building_segment.populate_data_elements()
            self.rmd.building_area_types.add(building_area_type)
            if self.rmd.default_building_segment is None:
                self.rmd.default_building_segment = building_segment
        self.zone.parent_building_segment = self.get_obj(
            BuildingSegment.lighting_building_area_map.get(
                building_area_type, "Default Building Segment"
            )
        )
        self.zone.parent.parent_building_segment = self.zone.parent_building_segment

        # Use the first occupancy type for the main Space object, and subspace Space objects for each additional occupancy type
        first_occ = None
        if isinstance(occupancy_type_list, list) and occupancy_type_list:
            first_occ = self.try_int(occupancy_type_list[0]) or None

        # Only set if we can resolve an occupancy type; otherwise keep existing value
        if first_occ is not None:
            self.lighting_space_type = self.lighting_space_map.get(
                first_occ, self.lighting_space_type
            )

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

    def populate_infiltration(self):
        """Populate infiltration data elements for the zone object."""
        infiltration = Infiltration(self)
        infiltration.populate_data_elements()
        infiltration.populate_data_group()
        infiltration.insert_to_rpd()

    def create_subspace_clones(self, i):
        """Create subspace clones for each subspace defined in the SPACE command."""
        # Do not call populate_data_elements() on subspace clones, only populate lighting_space_type and floor_area
        # TODO - lighting and equipment can be assigned to subspaces in the future
        subspace = Space(f"{self.u_name} Subspace {i + 1}", self.parent, self.rmd)
        subspace.lighting_space_type = self.lighting_space_map.get(
            self.try_access_index(self.get_inp(BDL_SpaceKeywords.C_901_OCC_TYPE), i)
        )
        subspace.floor_area = self.try_access_index(
            self.get_inp(BDL_SpaceKeywords.C_SUB_AREA), i
        )


class InteriorLighting:

    daylighting_control_type_map = {
        BDL_DaylightingControlOptions.CONTINUOUS: DaylightingControlOptions.CONTINUOUS_DIMMING,
        BDL_DaylightingControlOptions.CONTINUOUS_OFF: DaylightingControlOptions.CONTINUOUS_DIMMING,
        BDL_DaylightingControlOptions.STEPPED: DaylightingControlOptions.STEPPED,
        BDL_DaylightingControlOptions.DISCRETE: DaylightingControlOptions.STEPPED,
    }

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

        has_daylighting = self.parent_space.boolean_map.get(
            self.parent_space.get_inp(BDL_SpaceKeywords.DAYLIGHTING)
        )
        if has_daylighting:
            # Check if there are 2 daylighting control systems defined for the space
            if self.parent_space.get_inp(BDL_SpaceKeywords.ZONE_FRACTION2):
                # If so, they must both map to the same 229 control type to populate the data element, otherwise populate a Note explaining
                if self.daylighting_control_type_map.get(
                    self.parent_space.get_inp(BDL_SpaceKeywords.LIGHT_CTRL_TYPE1)
                ) == self.daylighting_control_type_map.get(
                    self.parent_space.get_inp(BDL_SpaceKeywords.LIGHT_CTRL_TYPE2)
                ):
                    self.daylighting_control_type = (
                        self.daylighting_control_type_map.get(
                            self.parent_space.get_inp(
                                BDL_SpaceKeywords.LIGHT_CTRL_TYPE1
                            )
                        )
                    )
                else:
                    self.notes = "Interior lighting has two daylighting control systems defined, but they do not map to the same 229 control type. "
            else:
                # Only one daylighting control system is defined
                self.daylighting_control_type = self.daylighting_control_type_map.get(
                    self.parent_space.get_inp(BDL_SpaceKeywords.LIGHT_CTRL_TYPE1)
                )

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


class Infiltration:

    infiltration_algorithm_map = {
        BDL_InfiltrationAlgorithmOptions.NONE: "None",
        BDL_InfiltrationAlgorithmOptions.AIR_CHANGE: "Air Change Method",
        BDL_InfiltrationAlgorithmOptions.RESIDENTIAL: "Residential Infiltration Coefficient",
        BDL_InfiltrationAlgorithmOptions.S_G: "Sherman-Grimsrud Infiltration Method",
        BDL_InfiltrationAlgorithmOptions.CRACK: "Crack Method",
        BDL_InfiltrationAlgorithmOptions.ASHRAE_ENHANCED: "2005 ASHRAE Handbook Fundamentals - Enhanced Infiltration Method",
    }

    def __init__(self, parent_space):
        self.data_structure = {}
        self.parent_space = parent_space
        self.zone = parent_space.zone

        # infiltration data elements
        self.name = self.zone.u_name + " Infil"
        self.reporting_name = None
        self.notes = None
        self.modeling_method = None
        self.algorithm_name = None
        self.measured_air_leakage_rate = None
        self.flow_rate = None
        self.multiplier_schedule = None

    def populate_data_elements(self):
        self.multiplier_schedule = self.parent_space.get_inp(
            BDL_SpaceKeywords.INF_SCHEDULE
        )
        infiltration_method = self.parent_space.get_inp(BDL_SpaceKeywords.INF_METHOD)
        self.algorithm_name = self.infiltration_algorithm_map.get(infiltration_method)
        if infiltration_method == BDL_InfiltrationAlgorithmOptions.AIR_CHANGE:
            flow_per_area = self.parent_space.try_float(
                self.parent_space.get_inp(BDL_SpaceKeywords.INF_FLOW_AREA)
            )
            air_changes_per_hour = self.parent_space.try_float(
                self.parent_space.get_inp(BDL_SpaceKeywords.AIR_CHANGES_HR)
            )
            if (
                flow_per_area
                and air_changes_per_hour
                and self.zone.volume
                and self.parent_space.floor_area
            ):
                self.flow_rate = (
                    flow_per_area * self.parent_space.floor_area
                    + air_changes_per_hour * self.zone.volume / 60
                )
                self.modeling_method = InfiltrationMethodOptions.WEATHER_DRIVEN
            elif flow_per_area and self.parent_space.floor_area:
                self.flow_rate = flow_per_area * self.parent_space.floor_area
                if self.multiplier_schedule:
                    self.modeling_method = InfiltrationMethodOptions.CONSTANT_SCHEDULED
                else:
                    self.modeling_method = InfiltrationMethodOptions.CONSTANT
            elif air_changes_per_hour and self.zone.volume:
                self.flow_rate = air_changes_per_hour * self.zone.volume / 60
                self.modeling_method = InfiltrationMethodOptions.WEATHER_DRIVEN
            elif flow_per_area == 0 and air_changes_per_hour == 0:
                self.flow_rate = 0
                self.modeling_method = InfiltrationMethodOptions.WEATHER_DRIVEN

        else:
            # infil_flow_rate will not populate if the infiltration method is not AIR-CHANGE
            self.modeling_method = InfiltrationMethodOptions.WEATHER_DRIVEN

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        infiltration_data_elements = [
            "reporting_name",
            "notes",
            "modeling_method",
            "algorithm_name",
            "measured_air_leakage_rate",
            "flow_rate",
            "multiplier_schedule",
        ]

        for attr in infiltration_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert infiltration object into the rpd data structure."""
        # find the zone that has the "SPACE" attribute value equal to the space object's u_name
        self.zone.infiltration = self.data_structure
