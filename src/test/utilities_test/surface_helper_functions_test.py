import pytest

from rpd_generator.config import Config
from rpd_generator.utilities.get_dict_of_surfaces_with_construction_assigned import (
    get_dict_of_surfaces_with_construction_assigned,
)
from rpd_generator.utilities.get_opaque_surface_type import (
    OpaqueSurfaceType,
    get_opaque_surface_type,
)


ureg = Config.ureg


@pytest.mark.parametrize(
    ("surface", "has_radiant_heat", "expected"),
    [
        ({"tilt": 0, "adjacent_to": "EXTERIOR"}, False, OpaqueSurfaceType.ROOF),
        ({"tilt": 59.9, "adjacent_to": "EXTERIOR"}, False, OpaqueSurfaceType.ROOF),
        (
            {"tilt": 90, "adjacent_to": "EXTERIOR"},
            False,
            OpaqueSurfaceType.ABOVE_GRADE_WALL,
        ),
        (
            {"tilt": 90, "adjacent_to": "GROUND"},
            False,
            OpaqueSurfaceType.BELOW_GRADE_WALL,
        ),
        ({"tilt": 120, "adjacent_to": "EXTERIOR"}, False, OpaqueSurfaceType.FLOOR),
        ({"tilt": 180, "adjacent_to": "GROUND"}, False, OpaqueSurfaceType.UNHEATED_SOG),
        ({"tilt": 180, "adjacent_to": "GROUND"}, True, OpaqueSurfaceType.HEATED_SOG),
        (
            {"tilt": 45 * ureg("degree"), "adjacent_to": "EXTERIOR"},
            False,
            OpaqueSurfaceType.ROOF,
        ),
    ],
)
def test_get_opaque_surface_type_classifies_by_tilt_and_adjacency(
    surface, has_radiant_heat, expected
):
    assert get_opaque_surface_type(surface, has_radiant_heat) == expected


def test_get_dict_of_surfaces_with_construction_assigned_counts_surface_categories():
    rpd = {
        "ruleset_model_descriptions": [
            {
                "constructions": [
                    {
                        "id": "C-1",
                        "primary_layers": ["L-1", "L-2"],
                        "framing_layers": ["F-1"],
                        "u_factor": 0.1,
                    },
                    {"id": "C-2", "c_factor": 0.2, "f_factor": 0.3},
                ],
                "buildings": [
                    {
                        "building_segments": [
                            {
                                "zones": [
                                    {
                                        "surfaces": [
                                            {
                                                "id": "Wall",
                                                "construction": "C-1",
                                                "adjacent_to": "EXTERIOR",
                                                "classification": "WALL",
                                            },
                                            {
                                                "id": "Roof",
                                                "construction": "C-1",
                                                "adjacent_to": "EXTERIOR",
                                                "classification": "CEILING",
                                            },
                                            {
                                                "id": "InferredRoof",
                                                "construction": "C-1",
                                                "adjacent_to": "EXTERIOR",
                                                "tilt": 10,
                                            },
                                            {
                                                "id": "InferredWall",
                                                "construction": "C-2",
                                                "adjacent_to": "EXTERIOR",
                                                "tilt": 90,
                                            },
                                            {
                                                "id": "Ground",
                                                "construction": "C-2",
                                                "adjacent_to": "GROUND",
                                            },
                                            {
                                                "id": "Interior",
                                                "construction": "C-2",
                                                "adjacent_to": "INTERIOR",
                                            },
                                            {
                                                "id": "NoConstruction",
                                                "adjacent_to": "EXTERIOR",
                                                "classification": "WALL",
                                            },
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ]
    }

    result = get_dict_of_surfaces_with_construction_assigned(rpd)

    assert result["C-1"] == {
        "exterior_walls": 1,
        "rooves": 2,
        "below_grade_surfaces": 0,
        "interior_surfaces": 0,
        "primary_layers_length": 2,
        "framing_layers_length": 1,
        "u_factor": 0.1,
        "c_factor": None,
        "f_factor": None,
    }
    assert result["C-2"] == {
        "exterior_walls": 1,
        "rooves": 0,
        "below_grade_surfaces": 1,
        "interior_surfaces": 1,
        "primary_layers_length": 0,
        "framing_layers_length": 0,
        "u_factor": None,
        "c_factor": 0.2,
        "f_factor": 0.3,
    }
