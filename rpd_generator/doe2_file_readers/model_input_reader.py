import inspect
import pkgutil
import importlib
import re
from rpd_generator.bdl_structure import *


class ModelInputReader:
    """Model input reader class."""

    def __init__(self):
        self.bdl_command_dict = self._get_bdl_commands_for_rpd()
        self.current_parent_floor = None
        self.current_parent_space = None
        self.current_parent = None

    def read_input_bdl_file(self, bdl_file_path):
        """
        Read BDL input file and return a dictionary of object instances.

        Args:
            bdl_file_path (str): Path to the BDL file.

        Returns:
            dict: A dictionary with BDL commands as keys and lists of their respective instances as values.
        """
        with open(bdl_file_path, "r") as bdl_file:
            command_instances = {}

            active_obj_instance = None
            record_data_for = False

            for line in bdl_file:
                if record_data_for and line[0] != "-":
                    record_data_for = False

                if '" = ' in line:
                    unique_name, command = self._parse_command_line(line)
                    if command in self.bdl_command_dict:
                        obj_instance = self._create_obj_instance(unique_name, command)
                        command_instances[obj_instance.u_name] = obj_instance
                        active_obj_instance = obj_instance

                elif 'DATA FOR' in line:
                    record_data_for = True
                    obj_u_name = line.split("DATA FOR ")[1].strip()
                    if active_obj_instance is None or obj_u_name != active_obj_instance.u_name:
                        active_obj_instance = command_instances.get(obj_u_name)
                    continue

                elif record_data_for and " = " in line and active_obj_instance is not None:
                    keyword, value, units = self._parse_definition_line(line)
                    # TODO add pint units to the keyword-value pairs
                    active_obj_instance.keyword_value_pairs[keyword] = value

            return command_instances

    def _set_current_parent(self, obj):
        if isinstance(obj, self.bdl_command_dict["FLOOR"]):
            self.current_parent_floor = obj
        elif isinstance(obj, self.bdl_command_dict["SPACE"]):
            self.current_parent_space = obj
        else:
            self.current_parent = obj

    def _create_obj_instance(self, unique_name, command):
        """
        Create an object instance based on the command type.

        Args:
            unique_name (str): Unique name for the instance.
            command (str): BDL command.

        Returns:
            Object: Created object instance.
        """
        command_class = self.bdl_command_dict[command]
        is_parent, is_child, is_int_ext_wall, is_space = self._determine_instance_type(command_class)

        if is_int_ext_wall:
            obj_instance = command_class(unique_name, self.current_parent_space)
            self._set_current_parent(obj_instance)
        elif is_space:
            obj_instance = command_class(unique_name, self.current_parent_floor)
            self._set_current_parent(obj_instance)
        elif is_child:
            obj_instance = command_class(unique_name, self.current_parent)
        elif is_parent:
            obj_instance = command_class(unique_name)
            self._set_current_parent(obj_instance)
        else:
            obj_instance = command_class(unique_name)

        return obj_instance

    @staticmethod
    def _parse_command_line(line):
        """
        Parse the line to extract unique name and command.

        Args:
            line (str): Line to be parsed.

        Returns:
            tuple: Unique name and command extracted from the line.
        """
        parts = line.split('" = ')
        unique_name = parts[0].strip().split('"')[1]
        command = parts[1].strip()
        return unique_name, command

    @staticmethod
    def _parse_definition_line(line):
        """
        Parse the line to extract keyword and value.

        Args:
            line (str): Line to be parsed.

        Returns:
            tuple: Keyword and value extracted from the line.
        """
        parts, units = line[:104].split(" = "), line[104:].strip()
        keyword = re.split(r' {2,}', parts[0])[1].strip()
        value = parts[1].strip()
        print(keyword, value, units)
        return keyword, value, units

    @staticmethod
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

    @staticmethod
    def _determine_instance_type(command_class):
        """
        Determine the type of BDL command class.

        Args:
            command_class (class): Command class to be determined.

        Returns:
            tuple: Indicates if the class is parent, child, int_ext_wall, or space.
        """
        is_parent = issubclass(command_class, ParentNode) or issubclass(command_class, ParentDefinition)
        is_child = issubclass(command_class, ChildNode)
        is_int_ext_wall = command_class.__name__ == "ExteriorWall" or command_class.__name__ == "InteriorWall"
        is_space = command_class.__name__ == "Space"

        return is_parent, is_child, is_int_ext_wall, is_space


reader = ModelInputReader()
model_object_structure = reader.read_input_bdl_file(r"../../test/example/INP.BDL")
print(model_object_structure["G - Lockers"].keyword_value_pairs)
