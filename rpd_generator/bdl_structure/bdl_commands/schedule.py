from rpd_generator.bdl_structure.base_node import BaseNode


class Schedule(BaseNode):
    """Schedule object in the tree."""

    bdl_command = "SCHEDULE-PD"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.schedule_data_structure = {}

        # data elements with no children
        self.purpose = None
        self.sequence_type = None
        self.hourly_values = None
        self.hourly_heating_design_day = None
        self.hourly_cooling_design_day = None
        self.event_times = None
        self.event_values = None
        self.event_times_heating_design_day = None
        self.event_values_heating_design_day = None
        self.event_times_cooling_design_day = None
        self.event_values_cooling_design_day = None
        self.type = None
        self.prescribed_type = None
        self.is_modified_for_workaround = None

    def __repr__(self):
        return f"Schedule(u_name='{self.u_name}')"

    def populate_data_group(self):
        """Populate schema structure for schedule object."""
        self.schedule_data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "purpose",
            "sequence_type",
            "hourly_values",
            "hourly_heating_design_day",
            "hourly_cooling_design_day",
            "event_times",
            "event_values",
            "event_times_heating_design_day",
            "event_values_heating_design_day",
            "event_times_cooling_design_day",
            "event_values_cooling_design_day",
            "type",
            "prescribed_type",
            "is_modified_for_workaround",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.schedule_data_structure[self.u_name][attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.schedules.append(self.schedule_data_structure)
