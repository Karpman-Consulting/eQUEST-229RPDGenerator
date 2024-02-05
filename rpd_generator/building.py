class Building:
    """
    This class is used to describe a building
    """

    def __init__(self, obj_id):
        self.obj_id = obj_id

        self.building_data_structure = {}

        # data elements with children
        self.building_segments = []
        self.elevators = []
        self.exterior_lighting = []
        self.refrigerated_cases = []

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.building_open_schedule = None
        self.has_site_shading = None
        self.number_of_floors_above_grade = None
        self.number_of_floors_below_grade = None

    def populate_data_group(self):
        """Populate the building data structure."""
        self.building_data_structure[self.obj_id] = {
            "building_segments": self.building_segments,
            "elevators": self.elevators,
            "exterior_lighting": self.exterior_lighting,
            "refrigerated_cases": self.refrigerated_cases,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "building_open_schedule",
            "has_site_shading",
            "number_of_floors_above_grade",
            "number_of_floors_below_grade",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.building_data_structure[self.obj_id][attr] = value

    def insert_to_rpd(self, rmd):
        """Insert building object into the rpd data structure."""
        rmd.buildings.append(self.building_data_structure)
