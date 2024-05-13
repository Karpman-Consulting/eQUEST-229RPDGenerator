from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.utilities import schedule_funcs


class Schedule(BaseNode):
    """Schedule object in the tree."""

    bdl_command = "SCHEDULE-PD"
    year = None
    day_of_week_for_january_1 = None
    holiday_type = None
    holiday_months = None
    holiday_days = None
    calender = {}

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

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

    def populate_data_elements(self):

        # POPULATE HOURLY_VALUES
        # Get the type of schedule
        ann_sch_type = self.keyword_value_pairs.get("TYPE")

        # There are no hourly values for temperature and ratio reset schedules so ignore those types
        if ann_sch_type != "RESET-TEMP" and ann_sch_type != "RESET-RATIO":
            proj_calendar = Schedule.calender
            # Get the month/day pair change points where a different week schedule begins
            ann_months = (
                self.keyword_value_pairs.get("MONTH")
                if isinstance(self.keyword_value_pairs.get("MONTH"), list)
                else [self.keyword_value_pairs.get("MONTH")]
            )
            ann_days = (
                self.keyword_value_pairs.get("DAY")
                if isinstance(self.keyword_value_pairs.get("DAY"), list)
                else [self.keyword_value_pairs.get("DAY")]
            )
            ann_months = [int(float(val)) for val in ann_months]
            ann_days = [int(float(val2)) for val2 in ann_days]
            # Get the week schedule associated with each month/day pair
            ann_wk_sch = [self.keyword_value_pairs.get("WEEK-SCHEDULES")]
            # Create a list of "Mo/Day" from the calendar
            list_of_dates = list(proj_calendar.keys())
            # Create a list to hold the index where there is a change in week schedule based on mo/day in ann sch
            change_index_list = []
            # Loop through each mo/day combo from the eQuest annual schedule to determine change indices.
            for i in range(0, len(ann_months)):
                date = str(ann_months[i]) + "/" + str(ann_days[i])
                # Add 1 because the change does not occur until the subsequent day in the eQuest ann schedule
                index_numbers_where_change_list = list_of_dates.index(date) + 1
                change_index_list.append(index_numbers_where_change_list)

            # Loop through each day of the year in the calendar. Depending on the day type extend the hourly schedule list object
            # for each day so that the result is a list with the hourly schedule value for the whole year.
            # Y is used to count the change point indices
            y = 0
            hourly_wk_sch_list = []
            list_of_day_types = list(proj_calendar.values())
            for x in range(0, len(list_of_day_types)):
                # Check if the indices is a change point. If so then the y counter will pull the next weekly schedule.
                if x in change_index_list and x != 365:
                    y = y + 1
                day_type = list_of_day_types[x]
                hourly_wk_sch_list.extend(
                    self.rmd.bdl_obj_instances[ann_wk_sch[y]].day_hourly_values[
                        day_type - 1
                    ]
                )

            self.hourly_values = hourly_wk_sch_list

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
                self.schedule_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.schedules.append(self.schedule_data_structure)
