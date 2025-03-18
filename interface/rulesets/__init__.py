import importlib
import pkgutil
import re


def import_views(ruleset):
    """Dynamically import all views from the selected ruleset's views package by searching modules for classes with "View" in the name."""
    ruleset = ruleset.replace("None", "generic")
    ruleset = re.sub(r"[-. ]", "", ruleset).lower()
    base_module = f"interface.rulesets.{ruleset}.views"

    # Discover all modules in the views package
    views_package = importlib.import_module(base_module)
    module_names = [
        module_name
        for _, module_name, is_pkg in pkgutil.iter_modules(views_package.__path__)
        if not is_pkg  # Only include modules, not sub-packages
    ]

    imported_views = {}

    for view_name in module_names:
        module = importlib.import_module(f"{base_module}.{view_name}")

        for attr_name in dir(module):
            if "View" in attr_name:  # Filter classes containing 'View'
                view_class = getattr(module, attr_name)
                if (
                    isinstance(view_class, type)
                    and view_class.__module__ == module.__name__
                ):
                    imported_views[attr_name] = view_class

    return imported_views


def static_files_path(ruleset):
    """Dynamically return the path to the ruleset's static files."""
    ruleset = ruleset.replace("None", "generic")
    ruleset = re.sub(r"[-. ]", "", ruleset).lower()
    return f"interface/rulesets/{ruleset}/static"
