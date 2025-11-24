import inspect
from jsonpath_ng.ext import parse

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_1 import (
    is_baseline_system_1,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_2 import (
    is_baseline_system_2,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_3 import (
    is_baseline_system_3,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_4 import (
    is_baseline_system_4,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_5 import (
    is_baseline_system_5,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_6 import (
    is_baseline_system_6,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_7 import (
    is_baseline_system_7,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_8 import (
    is_baseline_system_8,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_9 import (
    is_baseline_system_9,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_10 import (
    is_baseline_system_10,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_11_1 import (
    is_baseline_system_11_1,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_11_2 import (
    is_baseline_system_11_2,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_12 import (
    is_baseline_system_12,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_13 import (
    is_baseline_system_13,
)
from rpd_generator.utilities.get_dict_of_zones_and_terminals_served_by_hvac_sys import (
    get_dict_of_zones_and_terminals_served_by_hvac_sys,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.jsonpath_utils import find_all, find_one

EXTERNAL_FLUID_SOURCE = SchemaEnums.schema_enums["ExternalFluidSourceOptions"]
FLUID_LOOP = SchemaEnums.schema_enums["FluidLoopOptions"]


def get_baseline_system_types(rmd_b: dict) -> dict[str, list[str]]:
    """
    Identify all the baseline system types modeled in a B-RMD.

    Parameters
    ----------
    rmd_b json The B-RMD that needs to get the list of all HVAC system types.

    Returns dictionary saves all baseline HVAC system types in B-RMD with their IDs
    i.e. {"SYS-3": ["hvac_id_1", "hvac_id_10"], "SYS-7A": ["hvac_id_3", "hvac_id_17", "hvac_id_6], "SYS-9": ["hvac_id_2"]}
    -------
    """

    baseline_system_type_checks = [
        is_baseline_system_1,
        is_baseline_system_2,
        is_baseline_system_3,
        is_baseline_system_4,
        is_baseline_system_5,
        is_baseline_system_6,
        is_baseline_system_7,
        is_baseline_system_8,
        is_baseline_system_9,
        is_baseline_system_10,
        is_baseline_system_11_1,
        is_baseline_system_11_2,
        is_baseline_system_12,
        is_baseline_system_13,
    ]

    # A list of the attribute values from the HVAC_SYS class
    hvac_sys_list = [
        i[1]
        for i in inspect.getmembers(HVAC_SYS)
        if type(i[0]) is str and i[0].startswith("SYS")
    ] + [HVAC_SYS.UNMATCHED]

    baseline_hvac_system_dict = {sys_type: [] for sys_type in hvac_sys_list}

    dict_of_zones_and_terminal_units_served_by_hvac_sys = (
        get_dict_of_zones_and_terminals_served_by_hvac_sys(rmd_b)
    )

    for hvac_b in find_all(
        "$.buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*]",
        rmd_b,
    ):
        hvac_b_id = hvac_b["id"]
        terminals_list = dict_of_zones_and_terminal_units_served_by_hvac_sys[hvac_b_id][
            "terminals_list"
        ]
        zones_list = dict_of_zones_and_terminal_units_served_by_hvac_sys[hvac_b_id][
            "zones_list"
        ]
        # Heating fluid loops (type == HEATING)
        heating_loop_id_set = {
            m.value
            for m in parse('$.fluid_loops[?(@.type == "HEATING")].id').find(rmd_b)
        }

        # Cooling fluid loops (type == COOLING)
        cooling_loop_id_set = {
            m.value
            for m in parse('$.fluid_loops[?(@.type == "COOLING")].id').find(rmd_b)
        }

        # Boiler loops that reference heating loops
        boiler_loop_id_list = list(
            {
                m.value
                for m in parse("$.boilers[*].loop").find(rmd_b)
                if m.value in heating_loop_id_set
            }
        )

        # Chiller loops that reference cooling loops
        chiller_loop_id_list = list(
            {
                m.value
                for m in parse("$.chillers[*].loop").find(rmd_b)
                if m.value in cooling_loop_id_set
            }
        )

        # Purchased cooling (external fluid source: CHILLED_WATER)
        purchased_cooling_loop_id_list = list(
            {
                m.value
                for m in parse(
                    f"$.external_fluid_sources"
                    f'[?(@.type == "{EXTERNAL_FLUID_SOURCE.CHILLED_WATER}")].loop'
                ).find(rmd_b)
            }
        )

        # Purchased heating (external fluid source: HOT_WATER)
        purchased_heating_loop_id_list = list(
            {
                m.value
                for m in parse(
                    f"$.external_fluid_sources"
                    f'[?(@.type == "{EXTERNAL_FLUID_SOURCE.HOT_WATER}")].loop'
                ).find(rmd_b)
            }
        )

        # Arguments we *can* provide to a system check
        available_args = {
            "rmd_b": rmd_b,
            "hvac": hvac_b,
            "terminals_list": terminals_list,
            "zones_list": zones_list,
            "chiller_loop_id_list": chiller_loop_id_list,
            "boiler_loop_id_list": boiler_loop_id_list,
            "purchased_cooling_loop_id_list": purchased_cooling_loop_id_list,
            "purchased_heating_loop_id_list": purchased_heating_loop_id_list,
        }

        matched = False
        for sys_check in baseline_system_type_checks:
            sig = inspect.signature(sys_check)
            # pick only the parameters this function requires
            args_to_pass = {
                name: available_args[name]
                for name in sig.parameters
                if name in available_args
            }

            hvac_sys = sys_check(**args_to_pass)

            if hvac_sys != HVAC_SYS.UNMATCHED:
                baseline_hvac_system_dict[hvac_sys].append(hvac_b_id)
                matched = True
                break

        if not matched:
            baseline_hvac_system_dict[HVAC_SYS.UNMATCHED].append(hvac_b_id)

    return baseline_hvac_system_dict
