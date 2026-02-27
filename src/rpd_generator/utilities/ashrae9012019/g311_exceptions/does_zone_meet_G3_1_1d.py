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
from rpd_generator.utilities.pint_utils import ZERO

from rpd_generator.config import Config
from rpd_generator.schema.schema_utils import get_q

ureg = Config.ureg

BUILDING_TOTAL_LAB_EXHAUST_CFM_THRESHOLD = 15_000 * ureg("cfm")


class G311DDiagnostics(TypedDict):
    meets: bool
    building_total_lab_exhaust: Quantity
    is_lab_zone: bool


def get_g3_1_1d_diagnostics(
    rmd: dict,
    zone_id: str,
    laboratory_zones_list: list[dict] | None = None,
    building_total_lab_exhaust: Quantity | None = None,
    dict_of_zones_and_terminals_served_by_hvac_sys: dict | None = None,
    hvac_systems_map: dict[str, dict] | None = None,
) -> G311DDiagnostics:
    """
    Full diagnostics for G3.1.1d.
    """

    def sum_total_primary_airflow_from_terminals_func(terminal_list: list) -> Quantity:
        return sum(
            [
                get_q(terminal, "primary_airflow", ZERO.FLOW)
                for terminal in terminal_list
            ],
            ZERO.FLOW,
        )

    def sum_zone_primary_airflow_from_terminals_func(
        terminal_list: list, zone: dict
    ) -> Quantity:
        zone_terminal_ids = {t["id"] for t in zone.get("terminals", [])}
        return sum(
            [
                get_q(terminal, "primary_airflow", ZERO.FLOW)
                for terminal in terminal_list
                if terminal["id"] in zone_terminal_ids
            ],
            ZERO.FLOW,
        )

    def sum_hvac_total_exhaust_air_func(hvac_sys: dict) -> Quantity:
        return sum(
            (
                get_q(fan, "design_airflow", ZERO.FLOW)
                for fan in hvac_sys.get("fan_system", {}).get("exhaust_fans", [])
            ),
            ZERO.FLOW,
        )

    if laboratory_zones_list is None:
        laboratory_zones_list = get_building_lab_zones_list(rmd)
    if building_total_lab_exhaust is None:
        building_total_lab_exhaust = (
            get_building_total_lab_exhaust_from_zone_exhaust_fans(rmd)
        )

    if dict_of_zones_and_terminals_served_by_hvac_sys is None:
        dict_of_zones_and_terminals_served_by_hvac_sys = (
            get_dict_of_zones_and_terminals_served_by_hvac_sys(rmd)
        )

    lab_zone_ids = {z["id"] for z in laboratory_zones_list}

    if building_total_lab_exhaust <= BUILDING_TOTAL_LAB_EXHAUST_CFM_THRESHOLD:
        for lab_zone in laboratory_zones_list:
            if hvac_systems_map is not None:
                hvac_sys_id_list = {
                    t["served_by_heating_ventilating_air_conditioning_system"]
                    for t in lab_zone.get("terminals", [])
                    if t.get("served_by_heating_ventilating_air_conditioning_system")
                }
                hvac_sys_list_serving_zone = [
                    hvac_systems_map[hid]
                    for hid in hvac_sys_id_list
                    if hid in hvac_systems_map
                ]
            else:
                hvac_sys_list_serving_zone = get_list_hvac_systems_associated_with_zone(
                    rmd, lab_zone
                )

            zone_total_exhaust = ZERO.FLOW
            for hvac in hvac_sys_list_serving_zone:
                served_data = dict_of_zones_and_terminals_served_by_hvac_sys.get(
                    hvac["id"]
                )
                if not served_data:
                    continue
                terminal_list_hvac_sys = served_data["terminals_list"]

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

    is_lab_zone = zone_id in lab_zone_ids
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
