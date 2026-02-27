import inspect
from jsonpath_ng.ext import parse

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_1 import (
    diagnose_baseline_system_1,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_2 import (
    diagnose_baseline_system_2,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_3 import (
    diagnose_baseline_system_3,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_4 import (
    diagnose_baseline_system_4,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_5 import (
    diagnose_baseline_system_5,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_6 import (
    diagnose_baseline_system_6,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_7 import (
    diagnose_baseline_system_7,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_8 import (
    diagnose_baseline_system_8,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_9 import (
    diagnose_baseline_system_9,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_10 import (
    diagnose_baseline_system_10,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_11_1 import (
    diagnose_baseline_system_11_1,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_11_2 import (
    diagnose_baseline_system_11_2,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_12 import (
    diagnose_baseline_system_12,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_13 import (
    diagnose_baseline_system_13,
)
from rpd_generator.utilities.get_dict_of_zones_and_terminals_served_by_hvac_sys import (
    get_dict_of_zones_and_terminals_served_by_hvac_sys,
)
from rpd_generator.schema.schema_enums import SchemaEnums

EXTERNAL_FLUID_SOURCE = SchemaEnums.schema_enums["ExternalFluidSourceOptions"]

DIAGNOSTIC_MAP = {
    HVAC_SYS.SYS_1: diagnose_baseline_system_1,
    HVAC_SYS.SYS_1A: diagnose_baseline_system_1,
    HVAC_SYS.SYS_1B: diagnose_baseline_system_1,
    HVAC_SYS.SYS_1C: diagnose_baseline_system_1,
    HVAC_SYS.SYS_2: diagnose_baseline_system_2,
    HVAC_SYS.SYS_3: diagnose_baseline_system_3,
    HVAC_SYS.SYS_3A: diagnose_baseline_system_3,
    HVAC_SYS.SYS_3B: diagnose_baseline_system_3,
    HVAC_SYS.SYS_3C: diagnose_baseline_system_3,
    HVAC_SYS.SYS_4: diagnose_baseline_system_4,
    HVAC_SYS.SYS_5: diagnose_baseline_system_5,
    HVAC_SYS.SYS_5B: diagnose_baseline_system_5,
    HVAC_SYS.SYS_6: diagnose_baseline_system_6,
    HVAC_SYS.SYS_6B: diagnose_baseline_system_6,
    HVAC_SYS.SYS_7: diagnose_baseline_system_7,
    HVAC_SYS.SYS_7A: diagnose_baseline_system_7,
    HVAC_SYS.SYS_7B: diagnose_baseline_system_7,
    HVAC_SYS.SYS_7C: diagnose_baseline_system_7,
    HVAC_SYS.SYS_8: diagnose_baseline_system_8,
    HVAC_SYS.SYS_8A: diagnose_baseline_system_8,
    HVAC_SYS.SYS_8B: diagnose_baseline_system_8,
    HVAC_SYS.SYS_8C: diagnose_baseline_system_8,
    HVAC_SYS.SYS_9: diagnose_baseline_system_9,
    HVAC_SYS.SYS_9B: diagnose_baseline_system_9,
    HVAC_SYS.SYS_10: diagnose_baseline_system_10,
    HVAC_SYS.SYS_11_1: diagnose_baseline_system_11_1,
    HVAC_SYS.SYS_11_1A: diagnose_baseline_system_11_1,
    HVAC_SYS.SYS_11_1B: diagnose_baseline_system_11_1,
    HVAC_SYS.SYS_11_1C: diagnose_baseline_system_11_1,
    HVAC_SYS.SYS_11_2: diagnose_baseline_system_11_2,
    HVAC_SYS.SYS_11_2A: diagnose_baseline_system_11_2,
    HVAC_SYS.SYS_12: diagnose_baseline_system_12,
    HVAC_SYS.SYS_12A: diagnose_baseline_system_12,
    HVAC_SYS.SYS_12B: diagnose_baseline_system_12,
    HVAC_SYS.SYS_13: diagnose_baseline_system_13,
    HVAC_SYS.SYS_13A: diagnose_baseline_system_13,
}


def diagnose_modeled_vs_expected_system(
    rmd_b: dict, hvac_id: str, expected_sys_type: str
) -> dict:
    """
    Performs comparative diagnostics for a single HVAC system against an expected baseline type.
    """
    if expected_sys_type not in DIAGNOSTIC_MAP:
        return {"error": f"No diagnostic rules for {expected_sys_type}"}

    # 1. Locate the HVAC system object
    hvac_obj = None
    for b in rmd_b.get("buildings", []):
        for seg in b.get("building_segments", []):
            for hvac in seg.get("heating_ventilating_air_conditioning_systems", []):
                if hvac["id"] == hvac_id:
                    hvac_obj = hvac
                    break
            if hvac_obj:
                break
        if hvac_obj:
            break

    if not hvac_obj:
        return {"error": f"HVAC system {hvac_id} not found in RMD"}

    # 2. Precompute required data (similar to get_baseline_system_types)
    served_dict = get_dict_of_zones_and_terminals_served_by_hvac_sys(rmd_b)
    served = served_dict.get(hvac_id, {})
    terminals_list = served.get("terminals_list", [])
    zones_list = served.get("zones_list", [])

    heating_loop_id_set = {
        m.value for m in parse('$.fluid_loops[?(@.type == "HEATING")].id').find(rmd_b)
    }
    cooling_loop_id_set = {
        m.value for m in parse('$.fluid_loops[?(@.type == "COOLING")].id').find(rmd_b)
    }

    boiler_loop_id_list = [
        m.value
        for m in parse("$.boilers[*].loop").find(rmd_b)
        if m.value in heating_loop_id_set
    ]
    chiller_loop_id_list = [
        m.value
        for m in parse("$.chillers[*].cooling_loop").find(rmd_b)
        if m.value in cooling_loop_id_set
    ]
    purchased_cooling_loop_id_list = [
        m.value
        for m in parse(
            f"$.external_fluid_sources"
            f'[?(@.type == "{EXTERNAL_FLUID_SOURCE.CHILLED_WATER}")].loop'
        ).find(rmd_b)
    ]
    purchased_heating_loop_id_list = [
        m.value
        for m in parse(
            f"$.external_fluid_sources"
            f'[?(@.type == "{EXTERNAL_FLUID_SOURCE.HOT_WATER}")].loop'
        ).find(rmd_b)
    ]

    # 3. Call the appropriate diagnostic function
    diag_fn = DIAGNOSTIC_MAP[expected_sys_type]
    params = inspect.signature(diag_fn).parameters

    available_args = {
        "rmd_b": rmd_b,
        "hvac": hvac_obj,
        "terminals_list": terminals_list,
        "zones_list": zones_list,
        "chiller_loop_id_list": chiller_loop_id_list,
        "boiler_loop_id_list": boiler_loop_id_list,
        "purchased_cooling_loop_id_list": purchased_cooling_loop_id_list,
        "purchased_heating_loop_id_list": purchased_heating_loop_id_list,
    }

    call_args = {k: available_args[k] for k in params if k in available_args}
    results = diag_fn(**call_args)

    return results
