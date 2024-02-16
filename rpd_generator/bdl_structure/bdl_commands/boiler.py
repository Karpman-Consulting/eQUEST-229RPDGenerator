from rpd_generator.bdl_structure.base_node import BaseNode


class Boiler(BaseNode):
    """Boiler object in the tree."""

    bdl_command = "BOILER"

    draft_type_map = {
        "HW-BOILER": "NATURAL",
        "HW-BOILER-W/DRAFT": "FORCED",
        "ELEC-HW-BOILER": "NATURAL",
        "STM-BOILER": "NATURAL",
        "STM-BOILER-W/DRAFT": "FORCED",
        "ELEC-STM-BOILER": "NATURAL",
        "HW-CONDENSING": "FORCED",
    }
    energy_source_map = {
        "HW-BOILER": None,
        "HW-BOILER-W/DRAFT": None,
        "ELEC-HW-BOILER": "ELECTRICITY",
        "STM-BOILER": None,
        "STM-BOILER-W/DRAFT": None,
        "ELEC-STM-BOILER": "ELECTRICITY",
        "HW-CONDENSING": None,
    }

    draft_type_map = {
        "HW-BOILER": "NATURAL",
        "HW-BOILER-W/DRAFT": "FORCED",
        "ELEC-HW-BOILER": "NATURAL",
        "STM-BOILER": "NATURAL",
        "STM-BOILER-W/DRAFT": "FORCED",
        "ELEC-STM-BOILER": "NATURAL",
        "HW-CONDENSING": "FORCED",
    }
    # NEED TO GET BOILER ENERGY SOURCE FROM THE ASSIGNED FUEL METER
    energy_source_map = {
        "HW-BOILER": None,
        "HW-BOILER-W/DRAFT": None,
        "ELEC-HW-BOILER": "ELECTRICITY",
        "STM-BOILER": None,
        "STM-BOILER-W/DRAFT": None,
        "ELEC-STM-BOILER": "ELECTRICITY",
        "HW-CONDENSING": None,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

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
        return f"Boiler(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for boiler object."""
        self.draft_type = self.draft_type_map.get(self.keyword_value_pairs.get("TYPE"))

    def populate_data_elements(self):
        """Populate data elements for boiler object."""
        self.draft_type = self.draft_type_map.get(self.keyword_value_pairs.get("TYPE"))
        requests = self.get_output_requests()
        self.get_output_data(r"C:\Program Files (x86)\eQUEST 3-65-7175\D2Result.dll", b"C:\\Users\\JacksonJarboe\\Documents\\eQUEST 3-65-7175 Data\\DOE23", b"C:\\Users\\JacksonJarboe\\Documents\\Local Models\\CT Children's Hospital\\Final Model\\Proposed\\CT Childrens Hospital - Final - Baseline Design", requests)

    def get_output_requests(self):
        """Get the output requests for the boiler object."""
        requests = {
            # Primary Equipment (Boilers) - Capacity (Btu/hr)
            "Primary Equipment (Boilers) - Capacity (Btu/hr)": (2401061, self.u_name.encode("utf-8"), b""),
            # Primary Equipment (Boilers) - Flow (gal/min)
            "Primary Equipment (Boilers) - Flow (gal/min)": (2401062, self.u_name.encode("utf-8"), b""),
            # Primary Equipment (Boilers) - Rated EIR (frac)
            "Primary Equipment (Boilers) - Rated EIR (frac)": (2401063, self.u_name.encode("utf-8"), b""),
            # Primary Equipment (Boilers) - Rated HIR (frac)
            "Primary Equipment (Boilers) - Rated HIR (frac)": (2401064, self.u_name.encode("utf-8"), b""),
            # Primary Equipment (Boilers) - Auxiliary (kW)
            "Primary Equipment (Boilers) - Auxiliary (kW)": (2401065, self.u_name.encode("utf-8"), b""),
            # Boilers - Sizing Info/Boiler - Capacity
            "Boilers - Sizing Info/Boiler - Capacity": (2315911, self.u_name.encode("utf-8"), b""),
        }
        return requests

    def populate_data_group(self):
        """Populate schema structure for boiler object."""
        self.boiler_data_structure = {
            "id": self.u_name,
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
                self.boiler_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        rmd.boilers.append(self.boiler_data_structure)
