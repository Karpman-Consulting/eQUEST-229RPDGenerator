from typing import TypedDict
from pint import Quantity

from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_building_lab_zones_list import (
    get_building_lab_zones_list,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_building_total_lab_exhaust_from_zone_exhaust_fans import (
    get_building_total_lab_exhaust_from_zone_exhaust_fans,
)
from rpd_generator.utilities.get_dict_of_zones_and_terminals_served_by_hvac_sys import (
    get_dict_of_zones_and_terminals_served_by_hvac_sys,
)
from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)
from rpd_generator.utilities.jsonpath_utils import find_all
from rpd_generator.utilities.pint_utils import ZERO

from rpd_generator.config import Config

ureg = Config.ureg

BUILDING_TOTAL_LAB_EXHAUST_CFM_THRESHOLD = 15_000 * ureg("cfm")


class G311DDiagnostics(TypedDict):
    meets: bool
    building_total_lab_exhaust: Quantity
    is_lab_zone: bool


def get_g3_1_1d_diagnostics(rmd: dict, zone_id: str) -> G311DDiagnostics:
    """
    Full diagnostics for G3.1.1d.
    """

    def sum_total_primary_airflow_from_terminals_func(terminal_list: list) -> float:
        return sum(
            [terminal.get("primary_airflow", ZERO.FLOW) for terminal in terminal_list],
            ZERO.FLOW,
        )

    def sum_zone_primary_airflow_from_terminals_func(
        terminal_list: list, zone: dict
    ) -> float:
        return sum(
            [
                terminal.get("primary_airflow", ZERO.FLOW)
                for terminal in terminal_list
                if terminal["id"] in find_all("$.terminals[*].id", zone)
            ],
            ZERO.FLOW,
        )

    def sum_hvac_total_exhaust_air_func(hvac_sys: dict) -> float:
        return sum(
            find_all(
                "$.fan_system.exhaust_fans[*].design_airflow",
                hvac_sys,
            ),
            ZERO.FLOW,
        )

    laboratory_zones_list = get_building_lab_zones_list(rmd)
    building_total_lab_exhaust = get_building_total_lab_exhaust_from_zone_exhaust_fans(
        rmd
    )

    dict_of_zones_and_terminal_units_served_by_hvac_sys = (
        get_dict_of_zones_and_terminals_served_by_hvac_sys(rmd)
    )

    if building_total_lab_exhaust <= BUILDING_TOTAL_LAB_EXHAUST_CFM_THRESHOLD:
        for lab_zone in laboratory_zones_list:
            hvac_sys_list_serving_zone = get_list_hvac_systems_associated_with_zone(
                rmd, lab_zone
            )

            zone_total_exhaust = ZERO.FLOW
            for hvac in hvac_sys_list_serving_zone:
                terminal_list_hvac_sys = (
                    dict_of_zones_and_terminal_units_served_by_hvac_sys[hvac["id"]][
                        "terminals_list"
                    ]
                )
                hvac_system_total_exhaust_airflow = sum_hvac_total_exhaust_air_func(
                    hvac
                )
                total_terminal_air_flow = sum_total_primary_airflow_from_terminals_func(
                    terminal_list_hvac_sys
                )
                zone_primary_air_flow = sum_zone_primary_airflow_from_terminals_func(
                    terminal_list_hvac_sys, lab_zone
                )

                if zone_primary_air_flow > ZERO.FLOW:
                    zone_total_exhaust += (
                        hvac_system_total_exhaust_airflow
                        * zone_primary_air_flow
                        / total_terminal_air_flow
                    )
                else:
                    zone_total_exhaust += hvac_system_total_exhaust_airflow

            building_total_lab_exhaust += zone_total_exhaust

    is_lab_zone = zone_id in laboratory_zones_list
    meets = (
        is_lab_zone
        and building_total_lab_exhaust > BUILDING_TOTAL_LAB_EXHAUST_CFM_THRESHOLD
    )

    return G311DDiagnostics(
        meets=meets,
        building_total_lab_exhaust=building_total_lab_exhaust,
        is_lab_zone=is_lab_zone,
    )


def does_zone_meet_g3_1_1d(rmd: dict, zone_id: str) -> bool:
    """
    Wrapper that preserves the original API.
    """
    diag = get_g3_1_1d_diagnostics(rmd, zone_id)
    return diag["meets"]
