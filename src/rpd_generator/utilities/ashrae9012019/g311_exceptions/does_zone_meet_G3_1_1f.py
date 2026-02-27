from typing import TypedDict

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.is_zone_mechanically_cooled import (
    is_zone_mechanically_cooled,
)


class G311FDiagnostics(TypedDict):
    meets: bool
    is_zone_mechanically_cooled: bool
    is_system_type_9_or_10: bool


def get_g3_1_1f_diagnostics(
    rmd: dict,
    zone: dict,
    expected_sys_type: str,
    hvac_systems_map: dict[str, dict] | None = None,
    zone_map: dict[str, dict] | None = None,
) -> G311FDiagnostics:
    cooled = is_zone_mechanically_cooled(
        rmd, zone, hvac_systems_map=hvac_systems_map, zone_map=zone_map
    )
    is_sys_9_or_10 = expected_sys_type in [HVAC_SYS.SYS_9, HVAC_SYS.SYS_10]
    return G311FDiagnostics(
        meets=is_sys_9_or_10 and cooled,
        is_system_type_9_or_10=is_sys_9_or_10,
        is_zone_mechanically_cooled=cooled,
    )


def does_zone_meet_g_3_1_1f(rmd, zone, expected_sys_type):
    """
    Original API, now using diagnostics.
    """
    diag = get_g3_1_1f_diagnostics(rmd, zone, expected_sys_type)
    return diag["meets"]
