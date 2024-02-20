import inspect
import pkgutil
import importlib
import re
import os
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
        :return: A dictionary with BDL commands as keys and lists of .
        """

        with open(bdl_file_path, "r") as bdl_file:
            file_commands = {}

            active_command_dict = None
            record_data_for = False

            for line in bdl_file:
                if record_data_for and line[0] != "-":
                    record_data_for = False

                if '" = ' in line:
                    unique_name, command = self._parse_command_line(line)
                    if command in self.bdl_command_dict:
                        # start a command_dict with unique_name
                        command_dict = {"unique_name": unique_name}
                        self._track_current_parents(command, command_dict)
                        # add parent to the command_dict if applicable
                        command_dict = self._set_parent(command, command_dict)
                        if command not in file_commands:
                            file_commands[command] = [command_dict]
                        else:
                            file_commands[command].append(command_dict)
                        active_command_dict = command_dict
                    continue

                elif "DATA FOR" in line:
                    record_data_for = True
                    obj_u_name = line.split("DATA FOR ")[1].strip()
                    if (
                        active_command_dict is None
                        or obj_u_name != active_command_dict["unique_name"]
                    ):
                        active_command_dict = next(
                            (
                                cmd_dict
                                for cmd_list in file_commands.values()
                                for cmd_dict in cmd_list
                                if cmd_dict["unique_name"] == obj_u_name
                            ),
                            None,
                        )
                    continue

                elif (
                    record_data_for
                    and " = " in line
                    and active_command_dict is not None
                ):
                    # TODO add pint units to the values
                    keyword, value, units = self._parse_definition_line(line)
                    if keyword in active_command_dict and isinstance(
                        active_command_dict[keyword], list
                    ):
                        active_command_dict[keyword] = active_command_dict[
                            keyword
                        ].append(value)

                    elif keyword in active_command_dict:
                        active_command_dict[keyword] = [
                            active_command_dict[keyword],
                            value,
                        ]

                    else:
                        active_command_dict[keyword] = value

            return file_commands

    @staticmethod
    def copy_inp_with_diagnostic_comments(model_path):
        model_dir = os.path.dirname(model_path)
        model_name = os.path.basename(model_path)
        base_name, extension = os.path.splitext(model_name)
        temp_file_path = os.path.join(model_dir, base_name + "_temp" + extension)

        with open(model_path, "r") as inp_file, open(temp_file_path, "w") as out_file:
            lines_after_target = 0

            for line in inp_file:

                # Check if the current line contains the target text
                if "$              Abort, Diagnostics" in line:
                    lines_after_target = 3  # Set counter to insert after 3 lines

                # If counter is 1, it means 3 lines have passed since the target, so insert the new line
                elif lines_after_target == 1:
                    out_file.write("DIAGNOSTIC COMMENTS ..")
                    lines_after_target = 0  # Reset counter
                elif lines_after_target > 0:
                    lines_after_target -= (
                        1  # Decrement counter if we're in the 3-line window
                    )

                out_file.write(line)

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

    def _track_current_parents(self, command, command_dict):
        """
        Keep track of the most recent floor, space, or other parent objects. Floor and space parents are stored
        separately to ensure that the correct parent is set for child objects in multi-tiered nodes.
        :param command:
        :param command_dict:
        :return: None
        """
        plain_parent_commands = ["SYSTEM", "EXTERIOR-WALL", "INTERIOR-WALL"]
        if command == "FLOOR":
            self.current_parent_floor = command_dict["unique_name"]
        elif command == "SPACE":
            self.current_parent_space = command_dict["unique_name"]
        elif command in plain_parent_commands:
            self.current_parent = command_dict["unique_name"]
        return

    def _set_parent(self, command, command_dict):
        """
        Set the parent of the object based on the command type.
        :param command:
        :param command_dict:
        :return: command_dict
        """
        if command in ["EXTERIOR-WALL", "INTERIOR-WALL", "UNDERGROUND-WALL"]:
            command_dict["parent"] = self.current_parent_space
        elif command == "SPACE":
            command_dict["parent"] = self.current_parent_floor
        elif command in ["ZONE", "WINDOW", "DOOR"]:
            command_dict["parent"] = self.current_parent
        return command_dict
