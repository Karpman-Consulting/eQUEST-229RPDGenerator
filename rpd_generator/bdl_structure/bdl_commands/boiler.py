from rpd_generator.bdl_structure.base_node import BaseNode


class Boiler(BaseNode):
    """Boiler object in the tree."""

    bdl_command = "BOILER"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.boiler_data_structure = {}

        # data elements with children
        self.output_validation_points = []

        # data elements with no children
        self.loop = None
        self.design_capacity = None
        self.rated_capacity = None
        self.minimum_load_ratio = None
        self.draft_type = None
        self.energy_source_type = None
        self.auxiliary_power = None
        self.operation_lower_limit = None
        self.operation_upper_limit = None

    def __repr__(self):
        return f"Boiler('{self.u_name}')"

    def populate_data_group(self):
        """Populate schema structure for boiler object."""
        self.boiler_data_structure[self.u_name] = {
            "output_validation_points": self.output_validation_points,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "design_capacity",
            "rated_capacity",
            "minimum_load_ratio",
            "draft_type",
            "energy_source_type",
            "auxiliary_power",
            "operation_lower_limit",
            "operation_upper_limit",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.boiler_data_structure[self.u_name][attr] = value

    def insert_to_rpd(self, rmd):
        rmd.boilers.append(self.boiler_data_structure)