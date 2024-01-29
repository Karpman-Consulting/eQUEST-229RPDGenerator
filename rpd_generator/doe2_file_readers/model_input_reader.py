import inspect
import pkgutil
import importlib
from rpd_generator.models import *


def read_bdl_input_file(bdl_file_path: str) -> None:
    """
    Read BDL input file and return dictionary of objects.
    """
    bdl_commands_dict = get_bdl_commands_for_rpd()
    parent = None
    with open(bdl_file_path, "r") as bdl_file:
        previous_line = ""
        for line in bdl_file:
            # TODO: Implement a definitive way to know if the line is a bdl command. Parameter catch may not be enough.
            if '" = ' in line and "PARAMETER" not in previous_line:
                unique_name, command = (part.strip() for part in line.split('" = '))
                unique_name = unique_name.split('"')[1]
                if command in bdl_commands_dict:

                    bdl_command = bdl_commands_dict[command]
                    if issubclass(bdl_command, ChildNode):
                        obj = bdl_command(unique_name, parent)
                    elif issubclass(bdl_command, ParentNode) or issubclass(
                        bdl_command, ParentDefinition
                    ):
                        obj = bdl_command(unique_name)
                        parent = obj
                    else:
                        obj = bdl_command(unique_name)
            previous_line = line


def get_bdl_commands_for_rpd() -> dict:
    """
    Return a dictionary of BDL commands mapped to their respective class objects.
    """
    commands_dict = {}
    prefix = bdl_commands.__name__ + "."
    for _, name, _ in pkgutil.iter_modules(bdl_commands.__path__, prefix):
        module = importlib.import_module(name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, (BaseNode, BaseDefinition)):
                bdl_command = getattr(obj, "bdl_command", None)
                commands_dict[bdl_command] = obj
    return commands_dict


read_bdl_input_file(r"../../test/example/INP.BDL")
