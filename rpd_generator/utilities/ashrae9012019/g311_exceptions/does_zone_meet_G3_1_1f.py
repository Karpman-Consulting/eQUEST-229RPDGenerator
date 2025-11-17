from typing import TypedDict

from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.is_zone_mechanically_cooled import (
    is_zone_mechanically_cooled,
)


class G311FDiagnostics(TypedDict):
    meets: bool
    is_zone_mechanically_cooled: bool


def get_g3_1_1f_diagnostics(rmd: dict, zone: dict) -> G311FDiagnostics:
    cooled = is_zone_mechanically_cooled(rmd, zone)
    return G311FDiagnostics(
        meets=cooled,
        is_zone_mechanically_cooled=cooled,
    )


def does_zone_meet_g_3_1_1f(rmd, zone):
    """
    Original API, now using diagnostics.
    """
    diag = get_g3_1_1f_diagnostics(rmd, zone)
    return diag["meets"]
