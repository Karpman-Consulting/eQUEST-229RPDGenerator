from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_ScheduleKeywords = BDLEnums.bdl_enums["ScheduleKeywords"]
BDL_ScheduleTypes = BDLEnums.bdl_enums["ScheduleTypes"]


class Schedule(BaseNode):
    """Schedule object in the tree."""

    bdl_command = BDL_Commands.SCHEDULE_PD

    year = None
    day_of_week_for_january_1 = None
    holiday_type = None
    holiday_months = None
    holiday_days = None
    annual_calendar = {}
    LAST_DAY = 364
    supported_hourly_schedules = [BDL_ScheduleTypes.ON_OFF, BDL_ScheduleTypes.FRACTION, BDL_ScheduleTypes.MULTIPLIER, BDL_ScheduleTypes.TEMPERATURE]

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

        # Get the type of schedule
        ann_sch_type = self.keyword_value_pairs.get(BDL_ScheduleKeywords.TYPE)

        # There are no hourly values for temperature and ratio reset schedules so ignore those types
        if ann_sch_type in self.supported_hourly_schedules:
            proj_calendar = self.annual_calendar

            # Get the month value where a new week-schedule begins
            ann_months = (
                self.keyword_value_pairs.get(BDL_ScheduleKeywords.MONTH)
                if isinstance(self.keyword_value_pairs.get(BDL_ScheduleKeywords.MONTH), list)
                else [self.keyword_value_pairs.get(BDL_ScheduleKeywords.MONTH)]
            )
            ann_months = [int(float(val)) for val in ann_months]

            # Get the day value where a new week-schedule begins
            ann_days = (
                self.keyword_value_pairs.get(BDL_ScheduleKeywords.DAY)
                if isinstance(self.keyword_value_pairs.get(BDL_ScheduleKeywords.DAY), list)
                else [self.keyword_value_pairs.get(BDL_ScheduleKeywords.DAY)]
            )
            ann_days = [int(float(val)) for val in ann_days]

            week_schedules = [self.keyword_value_pairs.get(BDL_ScheduleKeywords.WEEK_SCHEDULES)]

            # Create a list to hold the index where there is a change in week schedule based on mo/day in ann sch
            schedule_change_indices = [
                list(proj_calendar.keys()).index(f"{ann_months[i]}/{ann_days[i]}") + 1
                for i in range(len(ann_months))
            ]

            # Loop through each day of the year in the calendar. Extend the hourly schedule values based on the day type
            # result is an 8760 list with the hourly schedule value for the whole year.
            wk_sch_index = 0
            hourly_values = []
            for day_index, day_type in enumerate(proj_calendar.values()):
                # Check if the index is a change point. If so, continue to the next weekly schedule index
                if day_index in schedule_change_indices and day_index != self.LAST_DAY:
                    wk_sch_index += 1

                wk_schedule_pd = self.rmd.bdl_obj_instances[
                    week_schedules[wk_sch_index]
                ]
                hourly_values.extend(
                    wk_schedule_pd.day_type_hourly_values[day_type - 1]
                )
            self.hourly_values = hourly_values

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
