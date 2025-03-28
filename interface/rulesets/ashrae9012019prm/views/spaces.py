import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords, Space

SPACE_TYPE_LPD = {
    "Audience Seating Area - Auditorium": 0.90,
    "Audience Seating Area - Convention center": 0.70,
    "Audience Seating Area - Exercise center": 0.30,
    "Audience Seating Area - Gymnasium": 0.40,
    "Audience Seating Area - Motion picture theater": 1.20,
    "Audience Seating Area - Penitentiary": 0.70,
    "Audience Seating Area - Performing arts theater": 2.60,
    "Audience Seating Area - Religious facility": 1.70,
    "Audience Seating Area - Sports arena": 0.40,
    "Audience Seating Area - Transportation facility": 0.50,
    "Audience Seating Area - All other": 0.90,
    "Atrium - Low/Medium": 0.0375,  # per foot in total height. Revisit TODO
    "Atrium - High": 0.50,  # + 0.025 per foot in total height. Revisit TODO
    "Banking activity area": 1.50,
    "Classroom/Lecture Hall/Training Room - Penitentiary": 1.30,
    "Classroom/Lecture Hall/Training Room - School": 1.40,
    "Classroom/Lecture Hall/Training Room - All other": 1.40,
    "Conference/Meeting/Multipurpose Room": 1.30,
    "Confinement Cells": 0.90,
    "Copy/Print Room": 0.90,
    "Corridor - Facility for the visually impaired corridor (and not used primarily by the staff)": 1.15,
    "Corridor - Hospital": 1.00,
    "Corridor - Manufacturing facility": 0.50,
    "Corridor - All others": 0.50,
    "Court room": 1.90,
    "Computer Room": 2.14,
    "Dining Area - Penitentiary": 1.30,
    "Dining Area - Facility for the visually impaired dining room (and not used primarily by staff)": 3.32,
    "Dining Area - Bar/lounge or leisure dining": 1.40,
    "Dining Area - Cafeteria or fast food dining": 0.90,
    "Dining Area - Family dining": 2.10,
    "Dining Area - All others": 0.90,
    "Electrical/Mechanical Room": 1.50,
    "Emergency Vehicle Garage": 0.80,
    "Food Preparation Area": 1.20,
    "Guest Room": 1.14,
    "Judges Chambers": 1.30,
    "Dwelling Unit": 1.07,
    "Laboratory in or as a classroom": 1.40,
    "All other laboratories": 1.40,
    "Laundry/Washing Area": 0.60,
    "Loading Dock, Interior": 0.59,
    "Lobby - Facility for the visually impaired (and not used primarily by staff)": 2.26,
    "Lobby - Elevator": 0.80,
    "Lobby - Hotel": 1.10,
    "Lobby - Motion picture theater": 1.10,
    "Lobby - Performing arts theater": 3.30,
    "Lobby - All others": 1.30,
    "Locker Room": 0.60,
    "Lounge/Breakroom - Healthcare facility": 0.80,
    "Lounge/Breakroom - All others": 1.20,
    "Office - Enclosed": 1.10,
    "Office - Open plan": 1.10,
    "Parking Area, Interior": 0.20,
    "Pharmacy Area": 1.20,
    "Restroom - Facility for the visually impaired restroom (and not used primarily by staff)": 1.52,
    "Restroom - All others": 0.90,
    "Sales Area": 1.70,
    "Seating Area, General": 0.68,
    "Stairwell": 0.60,
    "Storage Room - Hospital": 0.90,
    "Storage Room - Small": 0.80,
    "Storage Room - Large": 0.80,
    "Vehicular Maintenance Area": 0.70,
    "Workshop": 1.90,
    "Assisted Living Facility - Chapel (used primarily by residents)": 2.77,
    "Assisted Living Facility - Recreation room/common living room (and not used primarily by staff)": 3.02,
    "Convention Center - Exhibit Space": 1.30,
    "Dormitory - Living Quarters": 1.11,
    "Fire Station - Sleeping Quarters": 0.30,
    "Gymnasium/Fitness Center - Exercise area": 0.90,
    "Gymnasium/Fitness Center - Playing area": 1.40,
    "Healthcare Facility - Emergency room": 2.70,
    "Healthcare Facility - Exam/treatment room": 1.50,
    "Healthcare Facility - Medical supply room": 1.40,
    "Healthcare Facility - Nursery": 0.60,
    "Healthcare Facility - Nurse's station": 1.00,
    "Healthcare Facility - Operating room": 2.20,
    "Healthcare Facility - Patient room": 0.70,
    "Healthcare Facility - Physical therapy room": 0.90,
    "Healthcare Facility - Recovery room": 0.80,
    "Library - Reading area": 1.20,
    "Library - Stacks": 1.70,
    "Manufacturing Facility - Detailed manufacturing area": 2.10,
    "Manufacturing Facility - Equipment room": 1.20,
    "Manufacturing Facility - Extra high bay area": 1.32,
    "Manufacturing Facility - High bay area": 1.70,
    "Manufacturing Facility - Low bay area": 1.20,
    "Museum - General exhibition area": 1.00,
    "Museum - Restoration room": 1.70,
    "Post Office - Sorting Area": 1.20,
    "Religious Facility - Fellowship hall": 0.90,
    "Religious Facility - Worship/pulpit/choir area": 2.40,
    "Retail Facilities - Dressing/fitting room": 0.89,
    "Retail Facilities - Mall concourse": 1.70,
    "Sports Arena - Playing Area Class I facility": 4.61,
    "Sports Arena - Playing Area Class II facility": 3.01,
    "Sports Arena - Playing Area Class III facility": 2.26,
    "Sports Arena - Playing Area Class IV facility": 1.50,
    "Transportation Facility - Baggage/carousel area": 1.00,
    "Transportation Facility - Airport concourse": 0.60,
    "Transportation Facility - Ticket counter": 1.50,
    "Warehouse - Storage Area - Medium to bulky, palletized items": 0.90,
    "Warehouse - Storage Area - Smaller, hand-carried items": 1.40,
}

SPACE_TYPES_MAP = {
    "001": "Audience Seating Area - Auditorium",
    "002": "Audience Seating Area - Convention center",
    "003": "Audience Seating Area - Exercise center",
    "004": "Audience Seating Area - Gymnasium",
    "005": "Audience Seating Area - Motion picture theater",
    "006": "Audience Seating Area - Penitentiary",
    "007": "Audience Seating Area - Performing arts theater",
    "008": "Audience Seating Area - Religious facility",
    "009": "Audience Seating Area - Sports arena",
    "010": "Audience Seating Area - Transportation facility",
    "011": "Audience Seating Area - All other",
    "012": "Atrium - Low/Medium",
    "013": "Atrium - High",
    "014": "Banking activity area",
    "015": "Classroom/Lecture Hall/Training Room - Penitentiary",
    "016": "Classroom/Lecture Hall/Training Room - School",
    "017": "Classroom/Lecture Hall/Training Room - All other",
    "018": "Conference/Meeting/Multipurpose Room",
    "019": "Confinement Cells",
    "020": "Copy/Print Room",
    "021": "Corridor - Facility for the visually impaired (and not used primarily by the staff)",
    "022": "Corridor - Hospital",
    "023": "Corridor - Manufacturing facility",
    "024": "Corridor - All others",
    "025": "Court room",
    "026": "Computer Room",
    "027": "Dining Area - Penitentiary",
    "028": "Dining Area - Facility for the visually impaired dining room (and not used primarily by staff)",
    "029": "Dining Area - Bar/lounge or leisure dining",
    "030": "Dining Area - Cafeteria or fast food dining",
    "031": "Dining Area - Family dining",
    "032": "Dining Area - All others",
    "033": "Electrical/Mechanical Room",
    "034": "Emergency Vehicle Garage",
    "035": "Food Preparation Area",
    "036": "Guest Room",
    "037": "Judges Chambers",
    "038": "Dwelling Unit",
    "039": "Laboratory in or as a classroom",
    "040": "All other laboratories",
    "041": "Laundry/Washing Area",
    "042": "Loading Dock, Interior",
    "043": "Lobby - Facility for the visually impaired lobby (and not used primarily by staff)",
    "044": "Lobby - Elevator",
    "045": "Lobby - Hotel",
    "046": "Lobby - Motion picture theater",
    "047": "Lobby - Performing arts theater",
    "048": "Lobby - All others",
    "049": "Locker Room",
    "050": "Lounge/Breakroom - Healthcare facility",
    "051": "Lounge/Breakroom - All others",
    "052": "Office - Enclosed",
    "053": "Office - Open plan",
    "054": "Parking Area, Interior",
    "055": "Pharmacy Area",
    "056": "Restroom - Facility for the visually impaired (and not used primarily by staff)",
    "057": "Restroom - All others",
    "058": "Sales Area",
    "059": "Seating Area, General",
    "060": "Stairwell",
    "061": "Storage Room - Hospital",
    "062": "Storage Room - Small",
    "063": "Storage Room - Large",
    "064": "Vehicular Maintenance Area",
    "065": "Workshop",
    "066": "Assisted Living Facility - Chapel (used primarily by residents)",
    "067": "Assisted Living Facility - Recreation room/common living room (and not used primarily by staff)",
    "068": "Convention Center - Exhibit Space",
    "069": "Dormitory - Living Quarters",
    "070": "Fire Station - Sleeping Quarters",
    "071": "Gymnasium/Fitness Center - Exercise area",
    "072": "Gymnasium/Fitness Center - Playing area",
    "073": "Healthcare Facility - Emergency room",
    "074": "Healthcare Facility - Exam/treatment room",
    "075": "Healthcare Facility - Medical supply room",
    "076": "Healthcare Facility - Nursery",
    "077": "Healthcare Facility - Nurse's station",
    "078": "Healthcare Facility - Operating room",
    "079": "Healthcare Facility - Patient room",
    "080": "Healthcare Facility - Physical therapy room",
    "081": "Healthcare Facility - Recovery room",
    "082": "Library - Reading area",
    "083": "Library - Stacks",
    "084": "Manufacturing Facility - Detailed manufacturing area",
    "085": "Manufacturing Facility - Equipment room",
    "086": "Manufacturing Facility - Extra high bay area",
    "087": "Manufacturing Facility - High bay area",
    "088": "Manufacturing Facility - Low bay area",
    "089": "Museum - General exhibition area",
    "090": "Museum - Restoration room",
    "091": "Post Office - Sorting Area",
    "092": "Religious Facility - Fellowship hall",
    "093": "Religious Facility - Worship/pulpit/choir area",
    "094": "Retail Facilities - Dressing/fitting room",
    "095": "Retail Facilities - Mall concourse",
    "096": "Sports Arena - Playing Area Class I facility",
    "097": "Sports Arena - Playing Area Class II facility",
    "098": "Sports Arena - Playing Area Class III facility",
    "099": "Sports Arena - Playing Area Class IV facility",
    "100": "Transportation Facility - Baggage/carousel area",
    "101": "Transportation Facility - Airport concourse",
    "102": "Transportation Facility - Ticket counter",
    "103": "Warehouse - Storage Area - Medium to bulky, palletized items",
    "104": "Warehouse - Storage Area - Smaller, hand-carried items",
}


class SpacesView(BaseView):
    button_name = "Spaces"
    icon = "spaces.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        self.view_frame = ctk.CTkFrame(self)
        self.current_subview = None
        self.current_subview_name = None

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            font=LABEL_FONT,
        )
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text="Assign the various space data parameters for each space.",
            font=LABEL_FONT,
        )
        self.subviews = {
            "Baseline SpacesSubview": SpacesSubview(self.view_frame),
            "Proposed SpacesSubview": SpacesSubview(self.view_frame),
        }

    def __repr__(self):
        return "SpacesView"

    def open_view(self):
        self.toggle_active_button("Spaces")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(True)

        # 2 rows in the main surface view structure.
        # View frame (row 2, index 1) has a weight to make it fill up the empty space in the window
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Directions
        self.directions_frame.grid(row=0, column=0, sticky=FILL, padx=50, pady=20)
        self.directions_label.grid(row=0, column=0)
        self.directions_widget.grid(row=0, column=1)

        # Subview frame
        self.view_frame.grid(row=1, column=0, sticky=FILL, padx=20, pady=PAD20END)
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        current_state = self.app_data.baseline_or_proposed.get()
        self.current_subview_name = current_state + " SpacesSubview"
        self.show_subview(current_state + " SpacesSubview")

    def show_subview(self, subview_name):
        # Clear previous subview
        if self.current_subview is not None:
            self.current_subview.grid_forget()

        subview = self.subviews.get(subview_name)
        if subview:
            self.current_subview_name = subview_name
            self.current_subview = subview
        else:
            current_state = self.app_data.baseline_or_proposed.get()
            filtered_subviews = [
                value for key, value in self.subviews.items() if current_state in key
            ]

            # Set current_subview to the first matching subview, if found
            if filtered_subviews:
                self.current_subview = filtered_subviews[0]
                self.current_subview_name = (
                    self.app_data.baseline_or_proposed.get()
                    + " "
                    + self.current_subview.__repr__()
                )

        self.current_subview.grid(row=0, column=0, sticky=FILL)
        self.current_subview.focus_set()
        self.current_subview.open_subview()


class SpacesSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        self.is_view_populated = False
        self.new_spaces = {}

    def __repr__(self):
        return "SpacesSubview"

    def open_subview(self):
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get spaces from relevant rmd. Throw error if none found
        space_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            space_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).space_map.keys()
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            space_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).space_map.keys()

        for i, space_name in enumerate(space_names):
            # Add data vars for each space
            self.app_data.lighting_space_type_vars[space_name] = ctk.StringVar()
            # Add widget row for each space
            self.add_row(i, space_name)

        self.is_view_populated = True
        self.predict_space_type()

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
            status_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        lighting_space_type_label = ctk.CTkLabel(
            self, text="Lighting Space Type", font=LABEL_FONT
        )
        lighting_space_type_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        envelope_space_type_label = ctk.CTkLabel(
            self, text="Envelope Space Type", font=LABEL_FONT
        )
        envelope_space_type_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        ventilation_space_type_label = ctk.CTkLabel(
            self, text="Ventilation Space Type", font=LABEL_FONT
        )
        ventilation_space_type_label.grid(row=0, column=4, padx=PAD20END, pady=5)
        swh_space_type_label = ctk.CTkLabel(
            self, text="SWH Space Type", font=LABEL_FONT
        )
        swh_space_type_label.grid(row=0, column=5, padx=PAD20END, pady=5)
        lighting_occ_controls_label = ctk.CTkLabel(
            self, text="Lighting Occ. Controls", font=LABEL_FONT
        )
        lighting_occ_controls_label.grid(row=0, column=6, padx=PAD20END, pady=5)
        daylighting_controls_label = ctk.CTkLabel(
            self, text="Daylighting Controls", font=LABEL_FONT
        )
        daylighting_controls_label.grid(row=0, column=7, padx=PAD20END, pady=5)
        occ_controls_modeled_via_schedule_label = ctk.CTkLabel(
            self, text="Occ. Controls Modeled via Schedule?", font=LABEL_FONT
        )
        occ_controls_modeled_via_schedule_label.grid(
            row=0, column=8, padx=PAD20END, pady=5
        )
        daylighting_modeled_via_schedule_label = ctk.CTkLabel(
            self, text="Daylighting Modeled via Schedule?", font=LABEL_FONT
        )
        daylighting_modeled_via_schedule_label.grid(
            row=0, column=9, padx=PAD20END, pady=5
        )

    def add_row(self, i, space_name):
        name_label = ctk.CTkLabel(self, text=f"{space_name}")
        name_label.grid(row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W)
        if not self.app_data.is_all_new_construction.get():
            status_combo = ctk.CTkComboBox(
                self,
                values=self.app_data.StatusDescriptions,
                state=READONLY,
            )
            status_combo._entry.configure(justify=LEFT)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        lighting_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingSpaceDescriptions2019ASHRAE901TG37,
            variable=self.app_data.lighting_space_type_vars[space_name],
            command=lambda _: self.app_data.insert_to_rpd(
                self.app_data.LightingSpaceMapping2019ASHRAE901TG37, space_name
            ),
            state=READONLY,
        )
        lighting_space_type_combo._entry.configure(justify=LEFT)
        lighting_space_type_combo.grid(
            row=(i + 1), column=2, padx=PAD20END, pady=PAD20END
        )
        envelope_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.EnvelopeSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        envelope_space_type_combo._entry.configure(justify=LEFT)
        envelope_space_type_combo.grid(
            row=(i + 1), column=3, padx=PAD20END, pady=PAD20END
        )
        ventilation_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.VentilationSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        ventilation_space_type_combo._entry.configure(justify=LEFT)
        ventilation_space_type_combo.grid(
            row=(i + 1), column=4, padx=PAD20END, pady=PAD20END
        )
        swh_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.ServiceWaterHeatingSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        swh_space_type_combo._entry.configure(justify=LEFT)
        swh_space_type_combo.grid(row=(i + 1), column=5, padx=PAD20END, pady=PAD20END)
        lighting_occ_controls_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingOccupancyControlDescriptions,
            state=READONLY,
        )
        lighting_occ_controls_combo._entry.configure(justify=LEFT)
        lighting_occ_controls_combo.grid(
            row=(i + 1), column=6, padx=PAD20END, pady=PAD20END
        )
        daylighting_controls_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingDaylightingControlDescriptions,
            state=READONLY,
        )
        daylighting_controls_combo._entry.configure(justify=LEFT)
        daylighting_controls_combo.grid(
            row=(i + 1), column=7, padx=PAD20END, pady=PAD20END
        )
        occ_controls_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        occ_controls_modeled_checkbox.grid(
            row=(i + 1), column=8, padx=PAD20END, pady=PAD20END
        )
        daylighting_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        daylighting_modeled_checkbox.grid(
            row=(i + 1), column=9, padx=PAD20END, pady=PAD20END
        )

    def predict_space_type(self):
        """Predict the space type based on the specified space C-ACTIVITY-DESC"""
        baseline_rmd = self.app_data.get_rmd(ASHRAE9012019ModelOptions.BASELINE_0)
        for space_name in baseline_rmd.space_map.keys():
            space = baseline_rmd.get_obj(space_name)
            space_type_codes = []
            if space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC):
                space_type_codes = self.get_valid_space_codes(space)
            else:
                # Assign default activity type to each space
                print("No C-ACTIVITY-DESC found for space:", space_name)
                continue

            num_space_types = len(space_type_codes)
            #  If exactly 2 valid activity type codes are found
            if num_space_types == 2:
                # Get area, both LPDs, and lighting power for the space
                space_area = space.try_float(space.get_inp(BDL_SpaceKeywords.AREA))
                space_1_lpd = SPACE_TYPE_LPD.get(
                    SPACE_TYPES_MAP.get(space_type_codes[0]), None
                )
                space_2_lpd = SPACE_TYPE_LPD.get(
                    SPACE_TYPES_MAP.get(space_type_codes[1]), None
                )
                space_lighting_power = space_area * space.try_float(
                    space.int_ltg_power_per_area[0]
                )
                # Calculate and save the areas of the spaces
                space_1_area, space_2_area = self.calculate_space_areas(
                    space_area, space_1_lpd, space_2_lpd, space_lighting_power
                )
                # Calculate misc equipment power density
                space_1_misc_eq_power, space_2_misc_eq_power = (
                    self.calculate_value_proportionate_to_lpd(
                        space_1_area,
                        space_2_area,
                        space_1_lpd,
                        space_2_lpd,
                        space.try_float(space.misc_eq_power[0]),
                    )
                )
                # Calculate number of occupants for each space
                space_1_occupants, space_2_occupants = (
                    self.calculate_value_proportionate_to_lpd(
                        space_1_area,
                        space_2_area,
                        space_1_lpd,
                        space_2_lpd,
                        space.try_float(space.number_of_occupants),
                    )
                )
                # Get space types for each space
                space_1_type = SPACE_TYPES_MAP[space_type_codes[0]]
                space_2_type = SPACE_TYPES_MAP[space_type_codes[1]]
                # Update all original space data (space 1)
                self.update_original_space_data(
                    space_name,
                    space_1_area,
                    space_1_lpd,
                    space_1_misc_eq_power,
                    space_1_occupants,
                    space_1_type,
                )
                # Save new space data to temporary dictionary (space 2)
                self.new_spaces[space_name] = {
                    "floor_area": space_2_area,
                    "int_ltg_power_per_area": space_2_lpd,
                    "misc_eq_power": space_2_misc_eq_power,
                    "number_of_occupants": space_2_occupants,
                    "space_type": space_2_type,
                }

                # TODO: Debugging prints to see the calculated values. Remove when done
                print("Space type codes:", space_type_codes)
                print("Space area:", space_area)
                print("Space 1 LPD:", space_1_lpd)
                print("Space 2 LPD:", space_2_lpd)
                print("Lighting power:", space_lighting_power)
                print("Space 1 area:", space_1_area)
                print("Space 2 area:", space_2_area)
                print("Misc eq power:", space.misc_eq_power[0])
                print("Space 1 misc eq power:", space_1_misc_eq_power)
                print("Space 2 misc eq power:", space_2_misc_eq_power)
                print("Occupants:", space.number_of_occupants)
                print("Space 1 occupants:", space_1_occupants)
                print("Space 2 occupants:", space_2_occupants)
                print("--------------")
            # If more than 2 valid activity codes are found
            elif num_space_types > 2:
                # Create (n-1) new, default spaces in all RMDs
                self.add_new_spaces((num_space_types - 1), space_name)
            # If only 1 valid activity type code is found, populate original space types
            elif num_space_types == 1:
                space.lighting_space_type = SPACE_TYPES_MAP[space_type_codes[0]]
                space.envelope_space_type = SPACE_TYPES_MAP[space_type_codes[0]]
                space.ventilation_space_type = SPACE_TYPES_MAP[space_type_codes[0]]
                space.service_water_heating_space_type = SPACE_TYPES_MAP[
                    space_type_codes[0]
                ]
            # If no valid activity type codes are found
            else:
                # Predict space type based on C-ACTIVITY-DESC as a substring of available space types
                predicted_space_type = self.predict_space_type_from_substring(space)
                # If space type not predicted, try to predict based on space LPD
                if not predicted_space_type:
                    predicted_space_type = self.predict_space_type_from_lpd(space)
                # If space type is still not predicted, set default
                if not predicted_space_type:
                    predicted_space_type = "Office - Enclosed"
                # Set space type to predicted space type
                space.lighting_space_type = predicted_space_type
                space.envelope_space_type = predicted_space_type
                space.ventilation_space_type = predicted_space_type
                space.service_water_heating_space_type = predicted_space_type

        # Create and insert stored new spaces into all RMDs
        self.assign_new_space_data()

        # TODO: This is only here for testing to see changed RMD values. Remove when done
        print("\n\nSpace data in each RMD after prediction:")
        for rmd in self.app_data.rmds:
            for name, data in rmd.bdl_obj_instances.items():
                if type(data) == Space:
                    print(f"Space name: {name}")
                    print(f"Floor area: {data.floor_area}")
                    print(f"Lighting power per area: {data.int_ltg_power_per_area}")
                    print(f"Misc eq power: {data.misc_eq_power[0]}")
                    print(f"Occupants: {data.number_of_occupants}")
                    print(f"Lighting space type: {data.lighting_space_type}")
                    print(f"Envelope space type: {data.envelope_space_type}")
                    print(f"Ventilation space type: {data.ventilation_space_type}")
                    print(f"SWH space type: {data.service_water_heating_space_type}")
                    print("--------------")

    @staticmethod
    def get_valid_space_codes(space):
        """If every code in the C-ACTIVITY-DESC is valid, return the list of codes. Otherwise return an empty list."""
        space_type_codes = space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC).split("-")
        for code in space_type_codes:
            if code not in SPACE_TYPES_MAP.keys():
                return []
        return space_type_codes

    @staticmethod
    def calculate_space_areas(space_area, lpd_1, lpd_2, lighting_power):
        # X + Y = Space Area
        # X * LPD_1 + Y * LPD_2 = Lighting Power
        y_1 = lpd_1 * space_area
        y_2 = lpd_2 - lpd_1
        space_area_2 = (lighting_power - y_1) / y_2
        space_area_1 = space_area - space_area_2
        return space_area_1, space_area_2

    @staticmethod
    def calculate_value_proportionate_to_lpd(
        space_1_area, space_2_area, lpd_1, lpd_2, baseline_value
    ):
        """Calculate the value proportionate to the lighting power density\
        for any system of equations that follows this pattern:"""
        # b1*X + b2*Y = Baseline Space Misc. Eq. Power
        # a1/a2 = b1/b2
        i1 = lpd_2 * baseline_value / space_1_area
        i2 = lpd_2 * space_2_area / space_1_area
        b2 = i1 / (lpd_1 + i2)
        b1 = (b2 * lpd_1) / lpd_2
        return (b1 * space_1_area), (b2 * space_2_area)

    @staticmethod
    def predict_space_type_from_substring(space):
        """If the C-ACTIVITY-DESC for a space is a substring of any space type, return the space type with the
        lowest code as the predicted space type. Else return None."""
        activity_desc = space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC)
        if not activity_desc:
            return None
        predicted_space_types = {}
        for code, space_type in SPACE_TYPES_MAP.items():
            if activity_desc.lower() in space_type.lower():
                predicted_space_types[space_type] = code
        # If any predicted space types are found, keep the one with the lowest code
        if predicted_space_types:
            lowest_code = min(predicted_space_types.values())
            return SPACE_TYPES_MAP[lowest_code]
        return None

    @staticmethod
    def predict_space_type_from_lpd(space):
        """If the LPD for a space matches any of the LPDs in the SPACE_TYPE_LPD dictionary, return the space type
        with the lowest code as the predicted space type. Else return None."""
        space_lpd = space.try_float(space.int_ltg_power_per_area[0])
        if not space_lpd:
            return None
        predicted_space_types = {}
        for space_type, lpd in SPACE_TYPE_LPD.items():
            if space_lpd == lpd:
                code = list(SPACE_TYPES_MAP.keys())[
                    list(SPACE_TYPES_MAP.values()).index(space_type)
                ]
                predicted_space_types[code] = lpd
        # If any predicted space types are found, keep the one with the lowest code
        if predicted_space_types:
            lowest_code = min(predicted_space_types.keys())
            return SPACE_TYPES_MAP[lowest_code]

    def add_new_spaces(self, num_spaces, space_name):
        """Store new spaces so we can later add them to the RMDs"""
        for i in range(num_spaces):
            new_space_name = f"{space_name}_{i+2}"
            self.new_spaces[new_space_name] = space_name

    def update_original_space_data(
        self, space_name, area, lpd, misc_eq_power, occupants, space_type
    ):
        """Update the original space data for all RMDs"""
        for rmd in self.app_data.rmds:
            space = rmd.get_obj(space_name)
            space.floor_area = area
            space.int_ltg_power_per_area = lpd
            space.misc_eq_power[0] = misc_eq_power
            space.number_of_occupants = occupants
            space.lighting_space_type = space_type
            space.envelope_space_type = space_type
            space.ventilation_space_type = space_type
            space.service_water_heating_space_type = space_type

    def assign_new_space_data(self):
        """For every new space we created during the prediction, either add a default new
        space or a new space with the calculated data values. Do this for every RMD.
        Explanation: When we have a situation with more than 2 type codes, there are (n-1)
        new spaces created that already have their '_#' suffixes. What is stored in their
        'data' field in the new_spaces dictionary is the original space name that we need
        to copy over the original space data. If we have a situation with only 2 type codes,
        we create a new space with the original space name and the 'data' is actually
        a dict of the data we calculated. The new space name w/ suffix is created here
        """
        # TODO: copy over original space data we need to populate where necessary
        for rmd in self.app_data.rmds:
            for name, data in self.new_spaces.items():
                if type(data) == str:
                    original_space = rmd.get_obj(data)
                    new_space = Space(name, original_space.parent, rmd)
                    rmd.bdl_obj_instances[name] = new_space
                    rmd.space_map[name] = rmd.space_map.get(data)
                elif type(data) == dict:
                    original_space = rmd.get_obj(name)
                    new_space_name = f"{name}_2"
                    new_space = Space(new_space_name, original_space.parent, rmd)
                    new_space.floor_area = data["floor_area"]
                    new_space.int_ltg_power_per_area = data["int_ltg_power_per_area"]
                    new_space.misc_eq_power[0] = data["misc_eq_power"]
                    new_space.number_of_occupants = data["number_of_occupants"]
                    new_space.lighting_space_type = data["space_type"]
                    new_space.envelope_space_type = data["space_type"]
                    new_space.ventilation_space_type = data["space_type"]
                    new_space.service_water_heating_space_type = data["space_type"]
                    rmd.bdl_obj_instances[new_space_name] = new_space
                    rmd.space_map[new_space_name] = rmd.space_map.get(name)
