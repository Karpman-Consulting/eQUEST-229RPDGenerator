from rpd_generator.schema.schema_enums import SchemaEnums

LightingBuildingAreaOptions = SchemaEnums.schema_enums[
    "LightingBuildingAreaOptions2019ASHRAE901T951TG38"
]
HVACBuildingAreaOptions = SchemaEnums.schema_enums[
    "HeatingVentilatingAirConditioningBuildingAreaOptions2019ASHRAE901"
]
VerticalFenestrationBuildingAreaOptions = SchemaEnums.schema_enums[
    "VerticalFenestrationBuildingAreaOptions2019ASHRAE901"
]
ServiceWaterHeatingBuildingAreaOptions = SchemaEnums.schema_enums[
    "ServiceWaterHeatingAreaOptions2019ASHRAE901"
]


class BuildingSegment:
    """
    This class is used to represent the BuildingSegment object in the 229 schema.
    """

    lighting_building_area_map = {
        1: LightingBuildingAreaOptions.AUTOMOTIVE_FACILITY,
        2: LightingBuildingAreaOptions.CONVENTION_CENTER,
        3: LightingBuildingAreaOptions.COURTHOUSE,
        4: LightingBuildingAreaOptions.DINING_BAR_LOUNGE_LEISURE,
        5: LightingBuildingAreaOptions.DINING_CAFETERIA_FAST_FOOD,
        6: LightingBuildingAreaOptions.DINING_FAMILY,
        7: LightingBuildingAreaOptions.DINING_BAR_LOUNGE_LEISURE,
        8: LightingBuildingAreaOptions.DINING_CAFETERIA_FAST_FOOD,
        9: LightingBuildingAreaOptions.DINING_FAMILY,
        10: LightingBuildingAreaOptions.EXERCISE_CENTER,
        11: LightingBuildingAreaOptions.FIRE_STATION,
        12: LightingBuildingAreaOptions.RELIGIOUS_FACILITY,
        13: LightingBuildingAreaOptions.GYMNASIUM,
        14: LightingBuildingAreaOptions.HEALTH_CARE_CLINIC,
        15: LightingBuildingAreaOptions.HOSPITAL,
        16: LightingBuildingAreaOptions.LIBRARY,
        17: LightingBuildingAreaOptions.MANUFACTURING_FACILITY,
        18: LightingBuildingAreaOptions.MOTION_PICTURE_THEATER,
        19: LightingBuildingAreaOptions.MUSEUM,
        20: LightingBuildingAreaOptions.OFFICE,
        21: LightingBuildingAreaOptions.PARKING_GARAGE,
        22: LightingBuildingAreaOptions.PENITENTIARY,
        23: LightingBuildingAreaOptions.PERFORMING_ARTS_THEATER,
        24: LightingBuildingAreaOptions.POLICE_STATION,
        25: LightingBuildingAreaOptions.POST_OFFICE,
        26: LightingBuildingAreaOptions.RELIGIOUS_FACILITY,
        27: LightingBuildingAreaOptions.RETAIL,
        28: LightingBuildingAreaOptions.RETAIL,
        29: LightingBuildingAreaOptions.SCHOOL_UNIVERSITY,
        30: LightingBuildingAreaOptions.SCHOOL_UNIVERSITY,
        31: LightingBuildingAreaOptions.SPORTS_ARENA,
        32: LightingBuildingAreaOptions.TOWN_HALL,
        33: LightingBuildingAreaOptions.TRANSPORTATION,
        34: LightingBuildingAreaOptions.WAREHOUSE,
        35: LightingBuildingAreaOptions.WAREHOUSE,
        36: LightingBuildingAreaOptions.WORKSHOP,
        37: LightingBuildingAreaOptions.DORMITORY,
        38: LightingBuildingAreaOptions.HOTEL_MOTEL,
        39: LightingBuildingAreaOptions.HOTEL_MOTEL,
        40: LightingBuildingAreaOptions.MULTIFAMILY,
    }

    hvac_building_area_map = {
        1: HVACBuildingAreaOptions.RETAIL,
        2: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        3: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        4: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        5: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        6: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        7: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        8: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        9: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        10: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        11: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        12: HVACBuildingAreaOptions.RETAIL,
        13: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        14: HVACBuildingAreaOptions.HOSPITAL,
        15: HVACBuildingAreaOptions.HOSPITAL,
        16: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        17: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        18: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        19: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        20: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        21: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        22: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        23: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        24: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        25: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        26: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        27: HVACBuildingAreaOptions.RETAIL,
        28: HVACBuildingAreaOptions.RETAIL,
        29: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        30: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        31: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        32: HVACBuildingAreaOptions.PUBLIC_ASSEMBLY,
        33: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        34: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        35: HVACBuildingAreaOptions.HEATED_ONLY_STORAGE,
        36: HVACBuildingAreaOptions.OTHER_NON_RESIDENTIAL,
        37: HVACBuildingAreaOptions.RESIDENTIAL,
        38: HVACBuildingAreaOptions.RESIDENTIAL,
        39: HVACBuildingAreaOptions.RESIDENTIAL,
        40: HVACBuildingAreaOptions.RESIDENTIAL,
    }

    vertical_fenestration_building_area_map = {
        1: VerticalFenestrationBuildingAreaOptions.OTHER,
        2: VerticalFenestrationBuildingAreaOptions.OTHER,
        3: VerticalFenestrationBuildingAreaOptions.OTHER,
        4: VerticalFenestrationBuildingAreaOptions.RESTAURANT_QUICK_SERVICE,
        5: VerticalFenestrationBuildingAreaOptions.RESTAURANT_QUICK_SERVICE,
        6: VerticalFenestrationBuildingAreaOptions.RESTAURANT_QUICK_SERVICE,
        7: VerticalFenestrationBuildingAreaOptions.RESTAURANT_FULL_SERVICE,
        8: VerticalFenestrationBuildingAreaOptions.RESTAURANT_FULL_SERVICE,
        9: VerticalFenestrationBuildingAreaOptions.RESTAURANT_FULL_SERVICE,
        10: VerticalFenestrationBuildingAreaOptions.OTHER,
        11: VerticalFenestrationBuildingAreaOptions.OTHER,
        12: VerticalFenestrationBuildingAreaOptions.GROCERY_STORE,
        13: VerticalFenestrationBuildingAreaOptions.OTHER,
        14: VerticalFenestrationBuildingAreaOptions.HEALTHCARE_OUTPATIENT,
        15: VerticalFenestrationBuildingAreaOptions.HOSPITAL,
        16: VerticalFenestrationBuildingAreaOptions.OTHER,
        17: VerticalFenestrationBuildingAreaOptions.OTHER,
        18: VerticalFenestrationBuildingAreaOptions.OTHER,
        19: VerticalFenestrationBuildingAreaOptions.OTHER,
        20: VerticalFenestrationBuildingAreaOptions.OFFICE_MEDIUM,  # May be small, medium, or large depending on area
        21: VerticalFenestrationBuildingAreaOptions.OTHER,
        22: VerticalFenestrationBuildingAreaOptions.OTHER,
        23: VerticalFenestrationBuildingAreaOptions.OTHER,
        24: VerticalFenestrationBuildingAreaOptions.OTHER,
        25: VerticalFenestrationBuildingAreaOptions.OTHER,
        26: VerticalFenestrationBuildingAreaOptions.OTHER,
        27: VerticalFenestrationBuildingAreaOptions.RETAIL_STAND_ALONE,
        28: VerticalFenestrationBuildingAreaOptions.RETAIL_STRIP_MALL,
        29: VerticalFenestrationBuildingAreaOptions.SCHOOL_PRIMARY,
        30: VerticalFenestrationBuildingAreaOptions.SCHOOL_SECONDARY_AND_UNIVERSITY,
        31: VerticalFenestrationBuildingAreaOptions.OTHER,
        32: VerticalFenestrationBuildingAreaOptions.OTHER,
        33: VerticalFenestrationBuildingAreaOptions.OTHER,
        34: VerticalFenestrationBuildingAreaOptions.OTHER,
        35: VerticalFenestrationBuildingAreaOptions.WAREHOUSE_NONREFRIGERATED,
        36: VerticalFenestrationBuildingAreaOptions.OTHER,
        37: VerticalFenestrationBuildingAreaOptions.OTHER,
        38: VerticalFenestrationBuildingAreaOptions.HOTEL_MOTEL_SMALL,
        39: VerticalFenestrationBuildingAreaOptions.HOTEL_MOTEL_LARGE,
        40: VerticalFenestrationBuildingAreaOptions.OTHER,
    }

    service_water_heating_building_area_map = {
        1: ServiceWaterHeatingBuildingAreaOptions.AUTOMOTIVE_FACILITY,
        2: ServiceWaterHeatingBuildingAreaOptions.CONVENTION_CENTER,
        3: ServiceWaterHeatingBuildingAreaOptions.COURTHOUSE,
        4: ServiceWaterHeatingBuildingAreaOptions.DINING_BAR_LOUNGE_LEISURE,
        5: ServiceWaterHeatingBuildingAreaOptions.DINING_CAFETERIA_FAST_FOOD,
        6: ServiceWaterHeatingBuildingAreaOptions.DINING_FAMILY,
        7: ServiceWaterHeatingBuildingAreaOptions.DINING_BAR_LOUNGE_LEISURE,
        8: ServiceWaterHeatingBuildingAreaOptions.DINING_CAFETERIA_FAST_FOOD,
        9: ServiceWaterHeatingBuildingAreaOptions.DINING_FAMILY,
        10: ServiceWaterHeatingBuildingAreaOptions.EXERCISE_CENTER,
        11: ServiceWaterHeatingBuildingAreaOptions.FIRE_STATION,
        12: ServiceWaterHeatingBuildingAreaOptions.GROCERY_STORE,
        13: ServiceWaterHeatingBuildingAreaOptions.GYMNASIUM,
        14: ServiceWaterHeatingBuildingAreaOptions.HEALTH_CARE_CLINIC,
        15: ServiceWaterHeatingBuildingAreaOptions.HOSPITAL_AND_OUTPATIENT_SURGERY,
        16: ServiceWaterHeatingBuildingAreaOptions.LIBRARY,
        17: ServiceWaterHeatingBuildingAreaOptions.MANUFACTURING_FACILITY,
        18: ServiceWaterHeatingBuildingAreaOptions.MOTION_PICTURE_THEATER,
        19: ServiceWaterHeatingBuildingAreaOptions.MUSEUM,  # May be small, medium, or large depending on area
        20: ServiceWaterHeatingBuildingAreaOptions.OFFICE,
        21: ServiceWaterHeatingBuildingAreaOptions.PARKING_GARAGE,
        22: ServiceWaterHeatingBuildingAreaOptions.PENITENTIARY,
        23: ServiceWaterHeatingBuildingAreaOptions.PERFORMING_ARTS_THEATER,
        24: ServiceWaterHeatingBuildingAreaOptions.POLICE_STATION,
        25: ServiceWaterHeatingBuildingAreaOptions.POST_OFFICE,
        26: ServiceWaterHeatingBuildingAreaOptions.RELIGIOUS_FACILITY,
        27: ServiceWaterHeatingBuildingAreaOptions.RETAIL,
        28: ServiceWaterHeatingBuildingAreaOptions.RETAIL,
        29: ServiceWaterHeatingBuildingAreaOptions.SCHOOL_UNIVERSITY,
        30: ServiceWaterHeatingBuildingAreaOptions.SCHOOL_UNIVERSITY,
        31: ServiceWaterHeatingBuildingAreaOptions.SPORTS_ARENA,
        32: ServiceWaterHeatingBuildingAreaOptions.TOWN_HALL,
        33: ServiceWaterHeatingBuildingAreaOptions.TRANSPORTATION,
        34: ServiceWaterHeatingBuildingAreaOptions.WAREHOUSE,
        35: ServiceWaterHeatingBuildingAreaOptions.WAREHOUSE,
        36: ServiceWaterHeatingBuildingAreaOptions.WORKSHOP,
        37: ServiceWaterHeatingBuildingAreaOptions.DORMITORY,
        38: ServiceWaterHeatingBuildingAreaOptions.HOTEL,
        39: ServiceWaterHeatingBuildingAreaOptions.HOTEL,
        40: ServiceWaterHeatingBuildingAreaOptions.MULTIFAMILY,
    }

    bpf_area_map = {
        1: "RETAIL",
        2: "ALL_OTHERS",
        3: "ALL_OTHERS",
        4: "RESTAURANT",
        5: "RESTAURANT",
        6: "RESTAURANT",
        7: "RESTAURANT",
        8: "RESTAURANT",
        9: "RESTAURANT",
        10: "ALL_OTHERS",
        11: "ALL_OTHERS",
        12: "RETAIL",
        13: "ALL_OTHERS",
        14: "HEALTHCARE_HOSPITAL",
        15: "HEALTHCARE_HOSPITAL",
        16: "ALL_OTHERS",
        17: "ALL_OTHERS",
        18: "ALL_OTHERS",
        19: "ALL_OTHERS",
        20: "OFFICE",
        21: "ALL_OTHERS",
        22: "ALL_OTHERS",
        23: "ALL_OTHERS",
        24: "ALL_OTHERS",
        25: "ALL_OTHERS",
        26: "ALL_OTHERS",
        27: "RETAIL",
        28: "RETAIL",
        29: "SCHOOL",
        30: "SCHOOL",
        31: "ALL_OTHERS",
        32: "ALL_OTHERS",
        33: "ALL_OTHERS",
        34: "WAREHOUSE",
        35: "WAREHOUSE",
        36: "ALL_OTHERS",
        37: "ALL_OTHERS",
        38: "HOTEL_MOTEL",
        39: "HOTEL_MOTEL",
        40: "MULTIFAMILY",
    }

    def __init__(self, obj_id, rmd, building_type=None):
        self.rmd = rmd
        self.obj_id = obj_id
        self.building_type = building_type
        self.rmd.bdl_obj_instances[obj_id] = self
        self.building_segment_data_structure = {}

        # data elements with children
        self.zones = []
        self.hvac_systems = []
        self.service_water_heating_uses = []

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.number_of_floors_above_grade = None
        self.number_of_floors_below_grade = None
        self.is_all_new = None
        self.area_type_vertical_fenestration = None
        self.lighting_building_area_type = None
        self.area_type_heating_ventilating_air_conditioning_system = None
        self.service_water_heating_area_type = None

    def populate_data_elements(self):
        # BuildingSegment instances will be created for each unique building area type set within a SPACE BDL command
        # So there will only be 1 lighting building area type per BuildingSegment
        self.lighting_building_area_type = self.lighting_building_area_map.get(
            self.building_type
        )
        self.area_type_vertical_fenestration = (
            self.vertical_fenestration_building_area_map.get(self.building_type)
        )
        self.area_type_heating_ventilating_air_conditioning_system = (
            self.hvac_building_area_map.get(self.building_type)
        )
        self.service_water_heating_area_type = (
            self.service_water_heating_building_area_map.get(self.building_type)
        )

    def populate_data_group(self):
        """Populate the building segment data structure."""
        self.building_segment_data_structure = {
            "id": self.obj_id,
            "zones": self.zones,
            "heating_ventilating_air_conditioning_systems": self.hvac_systems,
            "service_water_heating_uses": self.service_water_heating_uses,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "number_of_floors_above_grade",
            "number_of_floors_below_grade",
            "is_all_new",
            "area_type_vertical_fenestration",
            "lighting_building_area_type",
            "area_type_heating_ventilating_air_conditioning_system",
            "service_water_heating_area_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.building_segment_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert building segment object into the rpd data structure."""
        self.rmd.bdl_obj_instances["Default Building"].building_segments.append(
            self.building_segment_data_structure
        )
