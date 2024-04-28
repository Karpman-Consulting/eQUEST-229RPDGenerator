from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class Space(ChildNode, ParentNode):
    """Space object in the tree."""

    bdl_command = "SPACE"

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        ParentNode.__init__(self, u_name, rmd)

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

        # InteriorLighting data elements
        self.int_ltg_id = [None]
        self.int_ltg_reporting_name = [None]
        self.int_ltg_notes = [None]
        self.int_ltg_purpose_type = [None]
        self.int_ltg_power_per_area = [None]
        self.int_ltg_lighting_multiplier_schedule = [None]
        self.int_ltg_occupancy_control_type = [None]
        self.int_ltg_daylighting_control_type = [None]
        self.int_ltg_are_schedules_used_for_modeling_occupancy_control = [None]
        self.int_ltg_are_schedules_used_for_modeling_daylighting_control = [None]

        # MiscellaneousEquipment data elements
        self.misc_eq_id = [None]
        self.misc_eq_reporting_name = [None]
        self.misc_eq_notes = [None]
        self.misc_eq_energy_type = [None]
        self.misc_eq_power = [None]
        self.misc_eq_multiplier_schedule = [None]
        self.misc_eq_sensible_fraction = [None]
        self.misc_eq_latent_fraction = [None]
        self.misc_eq_remaining_fraction_to_loop = [None]
        self.misc_eq_energy_from_loop = [None]
        self.misc_eq_type = [None]
        self.misc_eq_has_automatic_control = [None]

    def __repr__(self):
        return f"Space(u_name='{self.u_name}', parent={self.parent})"

    def populate_data_elements(self):
        """Populate data elements that originate from eQUEST's SPACE command"""
        # Populate interior lighting data elements
        space_ltg_scheds = self.keyword_value_pairs.get("LIGHTING-SCHEDUL")
        if not isinstance(space_ltg_scheds, list):
            space_ltg_scheds = [space_ltg_scheds]
        for i, sched in enumerate(space_ltg_scheds):
            self.populate_interior_lighting(i, sched)

        # Populate miscellaneous equipment data elements
        space_misc_eq_scheds = self.keyword_value_pairs.get("EQUIP-SCHEDULE")
        if not isinstance(space_misc_eq_scheds, list):
            space_misc_eq_scheds = [space_misc_eq_scheds]
        for i, sched in enumerate(space_misc_eq_scheds):
            self.populate_miscellaneous_equipment(i, sched)

        # Populate space data elements
        self.floor_area = self.try_float(self.keyword_value_pairs.get("AREA"))

        volume = self.keyword_value_pairs.get("VOLUME")
        if volume is not None:
            volume = self.try_float(volume)
            zone = self.rmd.space_map.get(self.u_name)
            zone.__setattr__("volume", volume)

        self.number_of_occupants = self.try_float(
            self.keyword_value_pairs.get("NUMBER-OF-PEOPLE")
        )

        self.occupant_multiplier_schedule = self.keyword_value_pairs.get(
            "PEOPLE-SCHEDULE"
        )

        self.occupant_sensible_heat_gain = self.keyword_value_pairs.get(
            "PEOPLE-HG-SENS"
        )

        self.occupant_sensible_heat_gain = self.try_float(
            self.occupant_sensible_heat_gain
        )

        self.occupant_latent_heat_gain = self.keyword_value_pairs.get("PEOPLE-HG-LAT")

        self.occupant_latent_heat_gain = self.try_float(self.occupant_latent_heat_gain)

    def populate_data_group(self):
        """Populate schema structure for space object."""

        attributes = [attr for attr in dir(self) if attr.startswith("int_ltg_")]
        keys = [
            attr.replace("int_ltg_", "") for attr in attributes
        ]  # Move outside the loop

        # Extract values for each attribute from the object only once
        int_ltg_value_lists = [getattr(self, attr) for attr in attributes]

        # Iterate over the values, creating dictionaries directly from zipped keys and values
        for values in zip(*int_ltg_value_lists):
            int_ltg_dict = {
                key: value for key, value in zip(keys, values) if value is not None
            }
            if int_ltg_dict:  # Only append if the dictionary is not empty
                self.interior_lighting.append(int_ltg_dict)

        attributes = [attr for attr in dir(self) if attr.startswith("misc_eq_")]
        keys = [
            attr.replace("misc_eq_", "") for attr in attributes
        ]  # Move outside the loop

        # Extract values for each attribute from the object only once
        misc_eq_value_lists = [getattr(self, attr) for attr in attributes]

        # Iterate over the values, creating dictionaries directly from zipped keys and values
        for values in zip(*misc_eq_value_lists):
            misc_eq_dict = {
                key: value for key, value in zip(keys, values) if value is not None
            }
            if misc_eq_dict:  # Only append if the dictionary is not empty
                self.miscellaneous_equipment.append(misc_eq_dict)

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

    def insert_to_rpd(self, rmd):
        """Insert space object into the rpd data structure."""
        # find the zone that has the "SPACE" attribute value equal to the space object's u_name
        zone = rmd.space_map.get(self.u_name)
        zone.spaces.append(self.space_data_structure)

    def populate_interior_lighting(self, n, schedule):
        """Populate interior lighting data elements for an instance of InteriorLighting"""
        int_ltg_id = f"{self.u_name} IntLtg{n}"
        int_ltg_power_per_area = self.try_access_index(
            self.keyword_value_pairs.get("LIGHTING-W/AREA"), n
        )
        int_ltg_lighting_multiplier_schedule = schedule

        if n == 0:
            self.int_ltg_id = [int_ltg_id]
            self.int_ltg_power_per_area = [int_ltg_power_per_area]
            self.int_ltg_lighting_multiplier_schedule = [
                int_ltg_lighting_multiplier_schedule
            ]
        else:
            self.int_ltg_id.append(int_ltg_id)
            self.int_ltg_power_per_area.append(int_ltg_power_per_area)
            self.int_ltg_lighting_multiplier_schedule.append(
                int_ltg_lighting_multiplier_schedule
            )

            # Lists must be the same length, even when elements are not populated
            self.int_ltg_reporting_name.append(None)
            self.int_ltg_notes.append(None)
            self.int_ltg_purpose_type.append(None)
            self.int_ltg_occupancy_control_type.append(None)
            self.int_ltg_daylighting_control_type.append(None)
            self.int_ltg_are_schedules_used_for_modeling_occupancy_control.append(None)
            self.int_ltg_are_schedules_used_for_modeling_daylighting_control.append(
                None
            )

    def populate_miscellaneous_equipment(self, n, schedule):
        """Populate miscellaneous equipment data elements for an instance of MiscellaneousEquipment"""
        misc_eq_id = f"{self.u_name} MiscEqp{n}"
        misc_eq_power = self.try_float(
            self.try_access_index(self.keyword_value_pairs.get("EQUIPMENT-W/AREA"), n)
        ) * self.try_float(self.keyword_value_pairs.get("AREA"))
        misc_eq_multiplier_schedule = schedule

        if n == 0:
            self.misc_eq_id = [misc_eq_id]
            self.misc_eq_power = [misc_eq_power]
            self.misc_eq_multiplier_schedule = [misc_eq_multiplier_schedule]
        else:
            self.misc_eq_id.append(misc_eq_id)
            self.misc_eq_power.append(misc_eq_power)
            self.misc_eq_multiplier_schedule.append(misc_eq_multiplier_schedule)

            # Lists must be the same length, even when elements are not populated
            self.misc_eq_reporting_name.append(None)
            self.misc_eq_notes.append(None)
            self.misc_eq_energy_type.append(None)
            self.misc_eq_sensible_fraction.append(None)
            self.misc_eq_latent_fraction.append(None)
            self.misc_eq_remaining_fraction_to_loop.append(None)
            self.misc_eq_energy_from_loop.append(None)
            self.misc_eq_type.append(None)
            self.misc_eq_has_automatic_control.append(None)
