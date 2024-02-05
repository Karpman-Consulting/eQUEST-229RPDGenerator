import inspect
import pkgutil
import importlib
import re
from .file_finder import find_equest_files
from rpd_generator.bdl_structure import *


def _get_bdl_commands_for_rpd() -> dict:
    """
    Return a dictionary of BDL commands mapped to their respective class objects to facilitate instantiation.
    """
    commands_dict = {}
    prefix = bdl_commands.__name__ + "."
    # iterate through the modules in the bdl_commands package
    for _, name, _ in pkgutil.iter_modules(bdl_commands.__path__, prefix):
        module = importlib.import_module(name)
        # iterate through the classes in each module
        for _, obj in inspect.getmembers(module, inspect.isclass):
            # if the class is a subclass of BaseNode or BaseDefinition
            if issubclass(obj, (BaseNode, BaseDefinition)):
                # get the bdl_command attribute
                bdl_command = getattr(obj, "bdl_command", None)
                # insert the bdl_command and class object into the dictionary to facilitate instantiation
                commands_dict[bdl_command] = obj
    return commands_dict


class ModelInputReader:
    """Model input reader class."""

    bdl_command_dict = _get_bdl_commands_for_rpd()

    def __init__(self):
        self.current_parent_floor = None
        self.current_parent_space = None
        self.current_parent = None

    def read_input_bdl_file(self, bdl_file_path):
        """
        Read BDL input file and return a dictionary of object instances.

        :param bdl_file_path: Path to the BDL file.
        :return: A dictionary with BDL unique names as keys and their respective object instances as values.
        """

        with open(bdl_file_path, "r") as bdl_file:
            file_commands = {}

            active_command = None
            record_data_for = False

            for line in bdl_file:
                if record_data_for and line[0] != "-":
                    record_data_for = False

                if '" = ' in line:
                    unique_name, command = self._parse_command_line(line)
                    if command in self.bdl_command_dict:
                        command_dict = {"unique_name": unique_name}
                        if command not in file_commands:
                            file_commands[command] = [command_dict]
                        else:
                            file_commands[command].append(command_dict)
                        active_command = command_dict
                    continue

                elif "DATA FOR" in line:
                    record_data_for = True
                    obj_u_name = line.split("DATA FOR ")[1].strip()
                    if (
                        active_command is None
                        or obj_u_name != active_command["unique_name"]
                    ):
                        active_command = next(
                            (
                                cmd_dict
                                for cmd_list in file_commands.values()
                                for cmd_dict in cmd_list
                                if cmd_dict["unique_name"] == obj_u_name
                            ),
                            None,
                        )
                    continue

                elif record_data_for and " = " in line and active_command is not None:
                    # TODO add pint units to the values
                    keyword, value, units = self._parse_definition_line(line)
                    if keyword in active_command and isinstance(
                        active_command[keyword], list
                    ):
                        active_command[keyword] = active_command[keyword].append(value)
                    elif keyword in active_command:
                        active_command[keyword] = [active_command[keyword], value]

                    else:
                        active_command[keyword] = value

            return file_commands

    @staticmethod
    def _parse_command_line(line):
        """
        Parse the line to extract unique name and command.

        :param line: Line to be parsed.
        :return: tuple: Unique name and command extracted from the line.
        """
        parts = line.split('" = ')
        unique_name = parts[0].strip().split('"')[1]
        command = parts[1].strip()
        return unique_name, command

    @staticmethod
    def _parse_definition_line(line):
        """
        Parse the line to extract keyword and value.

        :param line: Line to be parsed.
        :return: tuple: Keyword and value extracted from the line.
        """
        parts, units = line[:104].split(" = "), line[104:].strip()
        keyword = re.split(r" {2,}", parts[0])[1].strip()
        value = parts[1].strip()
        return keyword, value, units
