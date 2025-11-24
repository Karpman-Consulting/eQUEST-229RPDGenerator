from typing import TypedDict

from rpd_generator.utilities.jsonpath_utils import find_all


class SurfacesWithConstructionAssigned(TypedDict):
    exterior_walls: int
    rooves: int
    below_grade_surfaces: int
    interior_surfaces: int
    primary_layers_length: int
    framing_layers_length: int
    u_factor: float | None
    c_factor: float | None
    f_factor: float | None


def get_dict_of_surfaces_with_construction_assigned(
    rpd: dict,
) -> dict[str, SurfacesWithConstructionAssigned]:
    dict_of_surfaces_details: dict[str, SurfacesWithConstructionAssigned] = {}

    for construction in find_all(
        "$.ruleset_model_descriptions[*].constructions[*]",
        rpd,
    ):
        construction_id = construction["id"]
        if construction_id not in dict_of_surfaces_details:
            dict_of_surfaces_details[construction_id] = {
                "exterior_walls": 0,
                "rooves": 0,
                "below_grade_surfaces": 0,
                "interior_surfaces": 0,
                "primary_layers_length": 0,
                "framing_layers_length": 0,
                "u_factor": None,
                "c_factor": None,
                "f_factor": None,
            }
        dict_of_surfaces_details[construction_id]["primary_layers_length"] = len(
            construction.get("primary_layers", [])
        )
        dict_of_surfaces_details[construction_id]["framing_layers_length"] = len(
            construction.get("framing_layers", [])
        )
        dict_of_surfaces_details[construction_id]["u_factor"] = construction.get(
            "u_factor"
        )
        dict_of_surfaces_details[construction_id]["c_factor"] = construction.get(
            "c_factor"
        )
        dict_of_surfaces_details[construction_id]["f_factor"] = construction.get(
            "f_factor"
        )

    for surface in find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*].surfaces[*]",
        rpd,
    ):
        surface_adjacent_to = surface.get("adjacent_to")
        classification = surface.get("classification")
        tilt = surface.get("tilt", 90)
        construction = surface.get("construction")

        if not construction:
            continue

        # Below grade surface
        if surface_adjacent_to == "GROUND":
            dict_of_surfaces_details[construction]["below_grade_surfaces"] += 1
        # Interior surface
        elif surface_adjacent_to == "INTERIOR":
            dict_of_surfaces_details[construction]["interior_surfaces"] += 1
        # Exterior wall or roof
        elif surface_adjacent_to == "EXTERIOR":
            if classification == "WALL":
                dict_of_surfaces_details[construction]["exterior_walls"] += 1
            elif classification == "CEILING":
                dict_of_surfaces_details[construction]["rooves"] += 1
            elif classification is None:
                if tilt < 60:
                    dict_of_surfaces_details[construction]["rooves"] += 1
                elif 60 <= tilt < 120:
                    dict_of_surfaces_details[construction]["exterior_walls"] += 1

    return dict_of_surfaces_details
