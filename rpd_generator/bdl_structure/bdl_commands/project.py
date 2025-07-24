from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_commands.schedule import Schedule
from rpd_generator.utilities import schedule_funcs
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


ClimateZoneOptions2019ASHRAE901 = SchemaEnums.schema_enums[
    "ClimateZoneOptions2019ASHRAE901"
]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_SiteParameterKeywords = BDLEnums.bdl_enums["SiteParameterKeywords"]
BDL_RunPeriodKeywords = BDLEnums.bdl_enums["RunPeriodKeywords"]
BDL_HolidayKeywords = BDLEnums.bdl_enums["HolidayKeywords"]
BDL_HolidayTypes = BDLEnums.bdl_enums["HolidayTypes"]
BDL_ScheduleTypes = BDLEnums.bdl_enums["ScheduleTypes"]


class SiteParameters(BaseDefinition):
    bdl_command = BDL_Commands.SITE_PARAMETERS

    cz_letter_map = {
        1: "A",
        2: "B",
        3: "C",
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.site_parameter_name = u_name
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"SitePameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for site parameters object."""
        monthly_ground_temps = self.get_inp(BDL_SiteParameterKeywords.GROUND_T)
        if monthly_ground_temps:
            self.rmd.weather.setdefault(
                "ground_temperature_schedule", "Ground Temperature Schedule"
            )
            self.create_ground_temp_schedule(monthly_ground_temps)

        self.rmd.weather.setdefault("file_name", self.get_single_string_output(1101006))

        cz_number = self.get_inp(BDL_SiteParameterKeywords.C_901_CZ_NUMBER)
        cz_letter = self.get_inp(BDL_SiteParameterKeywords.C_901_CZ_LETTER)
        if cz_number is not None and cz_letter is not None:
            climate_zone = (
                "CZ"
                + str(self.try_int(cz_number.strip()))
                + str(self.cz_letter_map.get(self.try_int(cz_letter)))
            )

            if climate_zone in ClimateZoneOptions2019ASHRAE901.get_list():
                self.rmd.weather.setdefault("climate_zone", climate_zone)

    def create_ground_temp_schedule(self, monthly_ground_temps):
        """Create ground temperature schedule."""
        assert (
            len(monthly_ground_temps) == 12
        ), "Ground temperature schedule must have 12 values."
        hours_in_month = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
        hourly_values = []
        for i, temp in enumerate(monthly_ground_temps):
            hourly_values.extend([self.try_float(temp)] * hours_in_month[i])
        ground_t_schedule = Schedule("Ground Temperature Schedule", self.rmd)
        ground_t_schedule.type = BDL_ScheduleTypes.TEMPERATURE
        ground_t_schedule.hourly_values = hourly_values


class BuildingParameters(BaseDefinition):
    bdl_command = "BUILD-PARAMETERS"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"BuildingPameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for building parameters object."""
        self.rmd.building_azimuth = self.try_float(self.get_inp("AZIMUTH"))


class RunPeriod(BaseDefinition):
    bdl_command = BDL_Commands.RUN_PERIOD_PD

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"RunPeriod(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for run period object."""
        year = int(float(self.get_inp(BDL_RunPeriodKeywords.END_YEAR)))
        jan_1_day = schedule_funcs.get_day_of_week_jan_1(year)

        Schedule.year = year
        Schedule.day_of_week_for_january_1 = jan_1_day

        calendar = Calendar(self.rmd)
        calendar.day_of_week_for_january_1 = jan_1_day
        calendar.populate_data_group()
        calendar.insert_to_rpd()


class FixedShade(BaseDefinition):
    bdl_command = BDL_Commands.FIXED_SHADE

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.has_site_shading = True
        self.rmd.bdl_obj_instances[u_name] = self


class Holidays(BaseDefinition):
    bdl_command = BDL_Commands.HOLIDAYS

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

    def populate_data_elements(self):
        Schedule.holiday_type = self.get_inp(BDL_HolidayKeywords.TYPE)
        calendar = schedule_funcs.generate_year_calendar(
            Schedule.year, Schedule.day_of_week_for_january_1
        )

        if Schedule.holiday_type == BDL_HolidayTypes.OFFICIAL_US:
            calendar = schedule_funcs.get_official_us_holidays(calendar)
        elif Schedule.holiday_type == BDL_HolidayTypes.ALTERNATE:
            Schedule.holiday_months = self.get_inp(BDL_HolidayKeywords.MONTHS)
            Schedule.holiday_days = self.get_inp(BDL_HolidayKeywords.DAYS)
            calendar = schedule_funcs.get_alternate_holidays(
                calendar, Schedule.holiday_months, Schedule.holiday_days
            )

        Schedule.annual_calendar = calendar


class DesignDay(BaseDefinition):
    """DesignDay class"""

    bdl_command = BDL_Commands.DESIGN_DAY

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"DesignDay(u_name='{self.u_name}')"


class Calendar:

    def __init__(self, rmd):
        self.rmd = rmd

        self.data_structure = {}

        self.notes = None
        self.day_of_week_for_january_1 = None

    def __repr__(self):
        return "Calendar()"

    def populate_data_group(self):
        no_children_attributes = [
            "notes",
            "day_of_week_for_january_1",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert calendar object into the rpd data structure."""
        self.rmd.calendar = self.data_structure
