from itertools import chain
from jsonpath2 import match


def create_jsonpath_value_dict(jpath, obj):
    return {
        m.node.tojsonpath(): m.current_value for m in match(ensure_root(jpath), obj)
    }


def ensure_root(jpath):
    return jpath if jpath.startswith("$") else "$." + jpath


def find_all(jpath, obj):
    return [m.current_value for m in match(ensure_root(jpath), obj)]


def find_all_by_jsonpaths(jpaths: list, obj: dict) -> list:
    return list(chain.from_iterable([find_all(jpath, obj) for jpath in jpaths]))


def find_all_with_field_value(jpath, field, value, obj):
    return [
        m.current_value
        for m in match(ensure_root(f'{jpath}[?(@.{field}="{value}")]'), obj)
    ]


def find_one(jpath, obj, default=None):
    matches = find_all(jpath, obj)

    return matches[0] if len(matches) > 0 else default


def find_one_with_field_value(jpath, field, value, obj):
    matches = find_all_with_field_value(jpath, field, value, obj)

    return matches[0] if len(matches) > 0 else None


def find_exactly_one_with_field_value(jpath, field, value, obj):
    matches = find_all_with_field_value(jpath, field, value, obj)
    # do another search using upper case if no matches
    if not matches:
        matches = find_all_with_field_value(jpath, field, value.upper(), obj)

    return matches[0]


def find_exactly_one(jpath, obj):
    matches = find_all(jpath, obj)
    return matches[0]


def find_ruleset_model_type(rmd):
    return find_exactly_one("$.type", rmd)
