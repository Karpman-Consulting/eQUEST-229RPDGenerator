import pytest

from rpd_generator.utilities.jsonpath_utils import (
    create_enum_dict,
    ensure_root,
    find_all,
    find_all_by_jsonpaths,
    find_all_with_field_value,
    find_all_with_filters,
    find_one,
    split_jsonpath,
    split_path,
)


SAMPLE_OBJECT = {
    "ruleset_model_descriptions": [
        {
            "id": "RMD-1",
            "buildings": [
                {
                    "id": "B-1",
                    "building_segments": [
                        {
                            "id": "SEG-1",
                            "zones": [
                                {
                                    "id": "Z-1",
                                    "type": "OFFICE",
                                    "floor": "1",
                                    "spaces": [
                                        {"id": "S-1", "lighting_type": "LED"},
                                        {"id": "S-2", "lighting_type": "FLUORESCENT"},
                                    ],
                                },
                                {
                                    "id": "Z-2",
                                    "type": "LAB",
                                    "floor": "1",
                                    "spaces": [
                                        {"id": "S-3", "lighting_type": "LED"},
                                    ],
                                },
                                {
                                    "id": "Z-3",
                                    "type": "OFFICE",
                                    "floor": "2",
                                    "spaces": [
                                        {"id": "S-4", "lighting_type": "LED"},
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    ]
}


def test_create_enum_dict_keeps_available_enum_metadata():
    schema = {
        "definitions": {
            "SurfaceType": {
                "enum": ["WALL", "ROOF"],
                "descriptions": ["Wall", "Roof"],
            },
            "PlainObject": {"type": "object"},
        }
    }

    assert create_enum_dict(schema) == {
        "SurfaceType": {
            "enum": ["WALL", "ROOF"],
            "descriptions": ["Wall", "Roof"],
        },
        "PlainObject": {},
    }


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("ruleset_model_descriptions[*].id", "$.ruleset_model_descriptions[*].id"),
        ("$.ruleset_model_descriptions[*].id", "$.ruleset_model_descriptions[*].id"),
        ("$", "$"),
    ],
)
def test_ensure_root(path, expected):
    assert ensure_root(path) == expected


def test_split_path_preserves_filter_expressions_with_dots():
    path = "$.zones[*][?(@.id == 'Zone.A')].spaces[*].id"

    assert split_path(path) == [
        "zones[*][?(@.id == 'Zone.A')]",
        "spaces[*]",
        "id",
    ]


def test_split_jsonpath_preserves_bracketed_filters():
    assert split_jsonpath("$.a[*][?(@.b == 'c.d')].e") == [
        "a[*][?(@.b == 'c.d')]",
        "e",
    ]


def test_find_all_supports_wildcards_indices_and_filters():
    matches = find_all(
        "$.ruleset_model_descriptions[*].buildings[0].building_segments[*]"
        ".zones[*][?(@.type == 'OFFICE')].spaces[0].id",
        SAMPLE_OBJECT,
    )

    assert matches == ["S-1", "S-4"]


def test_find_all_supports_multiple_filter_conditions():
    matches = find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*]"
        ".zones[*][?(@.type == 'OFFICE' and @.floor == '1')].id",
        SAMPLE_OBJECT,
    )

    assert matches == ["Z-1"]


@pytest.mark.parametrize(
    "path",
    [
        "$.ruleset_model_descriptions[99].id",
        "$.ruleset_model_descriptions[*].missing",
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*]"
        ".zones[*][?(@.type == 'UNKNOWN')].id",
    ],
)
def test_find_all_returns_empty_list_for_missing_matches(path):
    assert find_all(path, SAMPLE_OBJECT) == []


def test_find_all_by_jsonpaths_flattens_matches_in_order():
    matches = find_all_by_jsonpaths(
        [
            "$.ruleset_model_descriptions[*].id",
            "$.ruleset_model_descriptions[*].buildings[*].id",
        ],
        SAMPLE_OBJECT,
    )

    assert matches == ["RMD-1", "B-1"]


def test_find_all_with_field_value_uses_jsonpath_filtering():
    obj = {"items": [{"id": "A", "kind": "TARGET"}, {"id": "B", "kind": "OTHER"}]}

    assert find_all_with_field_value("$.items[*]", "kind", "TARGET", obj) == [
        {"id": "A", "kind": "TARGET"}
    ]


def test_find_all_with_filters_requires_all_filter_values():
    obj = {
        "items": [
            {"id": "A", "kind": "TARGET", "level": "2"},
            {"id": "B", "kind": "TARGET", "level": "1"},
            {"id": "C", "kind": "OTHER", "level": "2"},
        ]
    }

    assert find_all_with_filters(
        "$.items[*]",
        {"kind": "TARGET", "level": "2"},
        obj,
    ) == [{"id": "A", "kind": "TARGET", "level": "2"}]


def test_find_one_returns_first_match_or_default():
    assert (
        find_one("$.ruleset_model_descriptions[*].buildings[*].id", SAMPLE_OBJECT)
        == "B-1"
    )
    assert find_one("$.missing", SAMPLE_OBJECT, default="fallback") == "fallback"
