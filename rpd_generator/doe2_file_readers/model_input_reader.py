import inspect
import pkgutil
import importlib
from rpd_generator.models import *


def read_input_bdl_file(bdl_file_path: str) -> dict:
    """
    Read BDL input file and return dictionary of objects.
    """
    bdl_command_dict = get_bdl_commands_for_rpd()
    with open(bdl_file_path, "r") as bdl_file:
        instance_dict = {cmd: [] for cmd in bdl_command_dict}
        previous_line = ""
        parent = None
        for line in bdl_file:
            # TODO: Implement a definitive way to know if the line is a bdl command. Parameter catch may not be enough.
            if '" = ' in line and "PARAMETER" not in previous_line:
                unique_name, command = (part.strip() for part in line.split('" = '))
                unique_name = unique_name.split('"')[1]
                if command in bdl_command_dict:
                    bdl_command = bdl_command_dict[command]
                    if issubclass(bdl_command, ChildNode):
                        obj = bdl_command(unique_name, parent)
                        instance_dict[command].append(obj)
                    elif issubclass(bdl_command, ParentNode) or issubclass(
                            bdl_command, ParentDefinition
                    ):
                        obj = bdl_command(unique_name)
                        instance_dict[command].append(obj)
                        # store most recent parent instance in memory to assign to next child instance(s)
                        parent = obj
                    else:
                        obj = bdl_command(unique_name)
                        instance_dict[command].append(obj)
            previous_line = line
    return instance_dict


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


print(read_input_bdl_file(r"../../test/example/INP.BDL"))
