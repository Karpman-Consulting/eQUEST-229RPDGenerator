from pydash import flat_map
from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.jsonpath_utils import find_all, find_one
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.schema.schema_utils import get_q

CoolingSystemOptions = SchemaEnums.schema_enums["CoolingSystemOptions"]
CoolingSourceOptions = SchemaEnums.schema_enums["CoolingSourceOptions"]


def is_zone_mechanically_cooled(
    rmd: dict,
    zone: dict,
    hvac_systems_map: dict[str, dict] | None = None,
    zone_map: dict[str, dict] | None = None,
) -> bool:
    """
    Function determines whether a zone is cooled. Checks for transfer air
    """
    if hvac_systems_map is not None:
        hvac_ids_serving_zone = {
            t["served_by_heating_ventilating_air_conditioning_system"]
            for t in zone.get("terminals", [])
            if t.get("served_by_heating_ventilating_air_conditioning_system")
        }
        list_hvac_systems = [
            hvac_systems_map[hid]
            for hid in hvac_ids_serving_zone
            if hid in hvac_systems_map
        ]
    else:
        list_hvac_systems = get_list_hvac_systems_associated_with_zone(rmd, zone)

    if zone_map is None:
        zone_map = {
            zn["id"]: zn
            for b in rmd.get("buildings", [])
            for seg in b.get("building_segments", [])
            for zn in seg.get("zones", [])
        }

    def does_hvac_has_cooling_sys(hvac: dict) -> bool:
        cooling_type = hvac.get("cooling_system", {}).get("type")
        return cooling_type not in [None, CoolingSourceOptions.NONE]

    def does_zone_terminals_have_cooling_type(zn: dict) -> bool:
        terminal_list = zn.get("terminals", [])
        return any(
            [
                t.get("cooling_source") not in [None, CoolingSourceOptions.NONE]
                for t in terminal_list
            ]
        )

    has_cooling_system = any(
        [does_hvac_has_cooling_sys(hvac) for hvac in list_hvac_systems]
    ) or does_zone_terminals_have_cooling_type(zone)

    if not has_cooling_system:
        transfer_flow = get_q(zone, "transfer_airflow_rate", ZERO.FLOW)
        if transfer_flow > ZERO.FLOW:
            transfer_source_zone_id = zone.get("transfer_airflow_source_zone")
            source_zone = zone_map.get(transfer_source_zone_id)
            if source_zone:
                # Recursion (shallow)
                return is_zone_mechanically_cooled(
                    rmd,
                    source_zone,
                    hvac_systems_map=hvac_systems_map,
                    zone_map=zone_map,
                )

    return has_cooling_system
