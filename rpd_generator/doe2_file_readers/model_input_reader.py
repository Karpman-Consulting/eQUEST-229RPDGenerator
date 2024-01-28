import inspect
import pkgutil
import importlib
from rpd_generator.models import *


def read_bdl_input_file(bdl_file_path: str) -> dict:
    """Read BDL input file and return dictionary of objects."""

    bdl_commands_for_rpd = get_bdl_commands_for_rpd()
    print(bdl_commands_for_rpd)
    # with open(bdl_file_path, "r") as bdl_file:
    # for line in bdl_file:
    #     print(line)
    return {}


def get_bdl_commands_for_rpd():
    commands = []
    prefix = bdl_commands.__name__ + "."
    for finder, name, is_pkg in pkgutil.iter_modules(bdl_commands.__path__, prefix):
        module = importlib.import_module(name)
        for mod_name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and (issubclass(obj, BaseNode) or issubclass(obj, BaseDefinition))
                and obj not in [BaseNode, BaseDefinition, ParentNode, ChildNode]
            ):
                commands.append(getattr(obj, "bdl_command", None))
    return commands


read_bdl_input_file(r"../../test/example/INP.BDL")
