from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)
from rpd_generator.utilities.schedule_utils import (
    get_max_schedule_multiplier_cooling_design_hourly_value_or_default,
    get_max_schedule_multiplier_heating_design_hourly_value_or_default,
    get_max_schedule_multiplier_hourly_value_or_default,
    get_schedule_multiplier_hourly_value_or_default,
)

ZONE_OCCUPANTS_RATIO_THRESHOLD = 0.05


class LeapYear:
    LEAP_YEAR_HOURS = 8784
    REGULAR_YEAR_HOURS = 8760


def get_zone_eflh(
    rmd: dict, zone: dict, hvac_systems_map: dict[str, dict] | None = None
) -> int:
    if hvac_systems_map is not None:
        hvac_ids_serving_zone = set(
            [
                terminal["served_by_heating_ventilating_air_conditioning_system"]
                for terminal in zone.get("terminals", [])
            ]
        )
        hvac_systems_list = sorted(
            [
                hvac_system
                for hvac_id, hvac_system in hvac_systems_map.items()
                if hvac_id in hvac_ids_serving_zone
            ],
            key=lambda d: d["id"],
        )
    else:
        hvac_systems_list = get_list_hvac_systems_associated_with_zone(rmd, zone)

    schedules_map = {sch.get("id"): sch for sch in rmd.get("schedules", [])}

    num_hours = None

    # Determine number of hours from HVAC fan schedules
    for hvac in hvac_systems_list:
        sched_id = hvac.get("fan_system", {}).get("operating_schedule")
        values = schedules_map.get(sched_id, {}).get("hourly_values")
        if values:
            num_hours = len(values)
            break

    # Fallback: determine number of hours from space occupant schedules
    if num_hours is None:
        for space in zone.get("spaces", []):
            sched_id = space.get("occupant_multiplier_schedule")
            values = schedules_map.get(sched_id, {}).get("hourly_values")
            if values:
                num_hours = len(values)
                break

    if num_hours is None:
        num_hours = 8760  # final fallback

    # Fan operation schedule per HVAC system
    def get_fan_operation_schedule(hvac_sys):
        sched_id = hvac_sys.get("fan_system", {}).get("operating_schedule")
        hourly_values = schedules_map.get(sched_id, {}).get("hourly_values")
        # If fan operation is unscheduled/unspecified, do not assume continuous
        # operation. Treat as not operating for EFLH significance checks.
        return hourly_values if hourly_values else [0.0] * num_hours

    hvac_operation_schedule_list = [
        get_fan_operation_schedule(hvac) for hvac in hvac_systems_list
    ]

    assert all(
        len(schedule) == num_hours for schedule in hvac_operation_schedule_list
    ), f"Not all HVAC operation schedules have {num_hours} hours"

    # Maximum occupants per space
    num_of_occupant_per_space_list = []
    for spc in zone.get("spaces", []):
        sched_id = spc.get("occupant_multiplier_schedule")
        base_occupants = spc.get("number_of_occupants", 0.0)

        max_multiplier = max(
            get_max_schedule_multiplier_hourly_value_or_default(rmd, sched_id, 1.0),
            get_max_schedule_multiplier_heating_design_hourly_value_or_default(
                rmd, sched_id, 1.0
            ),
            get_max_schedule_multiplier_cooling_design_hourly_value_or_default(
                rmd, sched_id, 1.0
            ),
            1.0,
        )

        num_of_occupant_per_space_list.append(max_multiplier * base_occupants)

    total_zone_occupants = sum(num_of_occupant_per_space_list)

    # Hourly occupant multipliers per space
    occupant_annual_hourly_value_per_space_list = [
        get_schedule_multiplier_hourly_value_or_default(
            rmd,
            spc.get("occupant_multiplier_schedule"),
            [1.0] * num_hours,
        )
        for spc in zone.get("spaces", [])
    ]

    assert all(
        len(schedule) == num_hours
        for schedule in occupant_annual_hourly_value_per_space_list
    ), f"Not all occupant schedules have {num_hours} hours"

    flh = 0
    for hour in range(num_hours):
        occupants_this_hour = sum(
            num_occupant * hourly_values[hour]
            for num_occupant, hourly_values in zip(
                num_of_occupant_per_space_list,
                occupant_annual_hourly_value_per_space_list,
            )
        )

        hvac_systems_operational_this_hour = any(
            schedule[hour] for schedule in hvac_operation_schedule_list
        )

        if (
            total_zone_occupants > 0
            and occupants_this_hour / total_zone_occupants
            > ZONE_OCCUPANTS_RATIO_THRESHOLD
            and hvac_systems_operational_this_hour
        ):
            flh += 1

    return flh
