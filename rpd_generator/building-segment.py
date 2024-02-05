class BuildingSegment:
    """
    This class is used to describe a building segment
    """

    def __init__(self, obj_id):
        self.obj_id = obj_id

        self.building_segment_data_structure = {}

        # data elements with children
        self.zones = []
        self.hvac_systems = []

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.number_of_floors_above_grade = None
        self.number_of_floors_below_grade = None
        self.is_all_new = None
        self.area_type_vertical_fenestration = None
        self.lighting_building_area_type = None
        self.area_type_heating_ventilating_air_conditioning_system = None

    def populate_data_group(self):
        """Populate the building segment data structure."""
        self.building_segment_data_structure[self.obj_id] = {
            "zones": self.zones,
            "heating_ventilating_air_conditioning_systems": self.hvac_systems,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "number_of_floors_above_grade",
            "number_of_floors_below_grade",
            "is_all_new",
            "area_type_vertical_fenestration",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.building_segment_data_structure[self.obj_id][attr] = value

    def insert_to_rpd(self, building):
        """Insert building segment object into the rpd data structure."""
        building.building_segments.append(self.building_segment_data_structure)
