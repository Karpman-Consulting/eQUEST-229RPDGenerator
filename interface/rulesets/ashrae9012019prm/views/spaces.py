import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords

SPACE_TYPE_LPD = {
    "Atrium < 20 ft": 0.39,
    "Atrium >= 20 ft and <= 40 ft": 0.48,
    "Atrium > 40 ft": 0.60,
    "Auditorium": 0.61,
    "Gymnasium": 0.23,
    "Motion picture theater": 0.27,
    "Penitentiary audience seating": 0.67,
    "Performing arts theater": 1.16,
    "Religious facility": 0.72,
    "Sports arena": 0.33,
    "All other audience seating areas": 0.23,
    "Banking activity area": 0.61,
    "Penitentiary classroom": 0.89,
    "All other classrooms/lecture halls/training rooms": 0.71,
    "Conference/Meeting/Multipurpose Room": 0.97,
    "Confinement Cells": 0.70,
    "Copy/Print Room": 0.31,
    "Facility for the visually impaired corridor": 0.71,
    "Hospital corridor": 0.71,
    "All other corridors": 0.41,
    "Courtroom": 1.20,
    "Computer Room": 0.94,
    "Penitentiary dining room": 0.42,
    "Facility for the visually impaired dining room": 1.27,
    "Bar/lounge or leisure dining": 0.86,
    "Cafeteria or fast food dining": 0.40,
    "Family dining": 0.60,
    "All other dining areas": 0.43,
    "Electrical/Mechanical Room": 0.43,
    "Emergency Vehicle Garage": 0.52,
    "Food Preparation Area": 1.09,
    "Guest Room": 0.41,
    "Laboratory in or as a classroom": 1.11,
    "All other laboratories": 1.33,
    "Laundry/Washing Area": 0.53,
    "Loading Dock, Interior": 0.88,
    "Facility for the visually impaired lobby": 1.69,
    "Elevator lobby": 0.65,
    "Hotel lobby": 0.51,
    "Motion picture theater lobby": 0.23,
    "Performing arts theater lobby": 1.25,
    "All other lobbies": 0.84,
    "Locker Room": 0.52,
    "Healthcare facility lounge/breakroom": 0.42,
    "All other lounges/breakrooms": 0.59,
    "Office Enclosed and <= 250 ft2": 0.74,
    "Office Enclosed and > 250 ft2": 0.66,
    "Office Open plan": 0.61,
    "Parking Area, Interior": 0.15,
    "Pharmacy Area": 1.66,
    "Facility for the visually impaired restroom": 1.26,
    "All other restrooms": 0.63,
    "Sales Area": 1.05,
    "Seating Area, General": 0.23,
    "Stairwell": 0.49,
    "Storage Room < 50 ft2": 0.51,
    "Storage Room >= 50 ft2": 0.38,
    "Vehicular Maintenance Area": 0.60,
    "Workshop": 1.26,
    "Facility for the visually impaired chapel": 0.70,
    "Facility for the visually impaired recreation room/common living room": 1.77,
    "Convention Center--Exhibit Space": 0.61,
    "Dormitory--Living Quarters": 0.50,
    "Fire Station--Sleeping Quarters": 0.23,
    "Gymnasium/Fitness Center Exercise area": 0.90,
    "Gymnasium/Fitness Center Playing area": 0.85,
    "Healthcare Facility Exam/treatment room": 1.40,
    "Healthcare Facility Imaging room": 0.94,
    "Healthcare Facility Medical supply room": 0.62,
    "Healthcare Facility Nursery": 0.92,
    "Healthcare Facility Nurse's station": 1.17,
    "Healthcare Facility Operating room": 2.26,
    "Healthcare Facility Patient room": 0.68,
    "Healthcare Facility Physical therapy room": 0.91,
    "Healthcare Facility Recovery room": 1.25,
    "Library Reading area": 0.96,
    "Library Stacks": 1.18,
    "Manufacturing Facility Detailed manufacturing area": 0.80,
    "Manufacturing Facility Equipment room": 0.76,
    "Manufacturing Facility Extra high bay area (>50 ft floor-to-ceiling height)": 1.42,
    "Manufacturing Facility High bay area (25 to 50 ft floor-to-ceiling height)": 1.24,
    "Manufacturing Facility Low bay area (<25 ft floor-to-ceiling height)": 0.86,
    "Museum General exhibition area": 0.31,
    "Museum Restoration room": 1.10,
    "Performing Arts Theater--Dressing Room": 0.41,
    "Post Office--Sorting Area": 0.76,
    "Religious Facility Fellowship hall": 0.54,
    "Religious Facility Worship/pulpit/choir area": 0.85,
    "Retail Facilities Dressing/fitting room": 0.51,
    "Retail Facilities Mall concourse": 0.82,
    "Sports Arena--Playing Area Class I facility": 2.94,
    "Sports Arena--Playing Area Class II facility": 2.01,
    "Sports Arena--Playing Area Class III facility": 1.30,
    "Sports Arena--Playing Area Class IV facility": 0.86,
    "Transportation Facility Baggage/carousel area": 0.39,
    "Transportation Facility Airport concourse": 0.25,
    "Transportation Facility Ticket counter": 0.51,
    "Warehouse--Storage Area Medium to bulky, palletized items": 0.33,
    "Warehouse--Storage Area Smaller, hand-carried items": 0.69,
}

SPACE_TYPE_CODES = {
    "001": "Atrium < 20 ft",
    "002": "Atrium >= 20 ft and <= 40 ft",
    "003": "Atrium > 40 ft",
    "004": "Auditorium",
    "005": "Gymnasium",
    "006": "Motion picture theater",
    "007": "Penitentiary audience seating",
    "008": "Performing arts theater",
    "009": "Religious facility",
    "010": "Sports arena",
    "011": "All other audience seating areas",
    "012": "Banking activity area",
    "013": "Penitentiary classroom",
    "014": "All other classrooms/lecture halls/training rooms",
    "015": "Conference/Meeting/Multipurpose Room",
    "016": "Confinement Cells",
    "017": "Copy/Print Room",
    "018": "Facility for the visually impaired corridor",
    "019": "Hospital corridor",
    "020": "All other corridors",
    "021": "Courtroom",
    "022": "Computer Room",
    "023": "Penitentiary dining room",
    "024": "Facility for the visually impaired dining room",
    "025": "Bar/lounge or leisure dining",
    "026": "Cafeteria or fast food dining",
    "027": "Family dining",
    "028": "All other dining areas",
    "029": "Electrical/Mechanical Room",
    "030": "Emergency Vehicle Garage",
    "031": "Food Preparation Area",
    "032": "Guest Room",
    "033": "Laboratory in or as a classroom",
    "034": "All other laboratories",
    "035": "Laundry/Washing Area",
    "036": "Loading Dock, Interior",
    "037": "Facility for the visually impaired lobby",
    "038": "Elevator lobby",
    "039": "Hotel lobby",
    "040": "Motion picture theater lobby",
    "041": "Performing arts theater lobby",
    "042": "All other lobbies",
    "043": "Locker Room",
    "044": "Healthcare facility lounge/breakroom",
    "045": "All other lounges/breakrooms",
    "046": "Office Enclosed and <= 250 ft2",
    "047": "Office Enclosed and > 250 ft2",
    "048": "Office Open plan",
    "049": "Parking Area, Interior",
    "050": "Pharmacy Area",
    "051": "Facility for the visually impaired restroom",
    "052": "All other restrooms",
    "053": "Sales Area",
    "054": "Seating Area, General",
    "055": "Stairwell",
    "056": "Storage Room < 50 ft2",
    "057": "Storage Room >= 50 ft2",
    "058": "Vehicular Maintenance Area",
    "059": "Workshop",
    "060": "Facility for the visually impaired chapel",
    "061": "Facility for the visually impaired recreation room/common living room",
    "062": "Convention Center--Exhibit Space",
    "063": "Dormitory--Living Quarters",
    "064": "Fire Station--Sleeping Quarters",
    "065": "Gymnasium/Fitness Center Exercise area",
    "066": "Gymnasium/Fitness Center Playing area",
    "067": "Healthcare Facility Exam/treatment room",
    "068": "Healthcare Facility Imaging room",
    "069": "Healthcare Facility Medical supply room",
    "070": "Healthcare Facility Nursery",
    "071": "Healthcare Facility Nurse's station",
    "072": "Healthcare Facility Operating room",
    "073": "Healthcare Facility Patient room",
    "074": "Healthcare Facility Physical therapy room",
    "075": "Healthcare Facility Recovery room",
    "076": "Library Reading area",
    "077": "Library Stacks",
    "078": "Manufacturing Facility Detailed manufacturing area",
    "079": "Manufacturing Facility Equipment room",
    "080": "Manufacturing Facility Extra high bay area (>50 ft floor-to-ceiling height)",
    "081": "Manufacturing Facility High bay area (25 to 50 ft floor-to-ceiling height)",
    "082": "Manufacturing Facility Low bay area (<25 ft floor-to-ceiling height)",
    "083": "Museum General exhibition area",
    "084": "Museum Restoration room",
    "085": "Performing Arts Theater--Dressing Room",
    "086": "Post Office--Sorting Area",
    "087": "Religious Facility Fellowship hall",
    "088": "Religious Facility Worship/pulpit/choir area",
    "089": "Retail Facilities Dressing/fitting room",
    "090": "Retail Facilities Mall concourse",
    "091": "Sports Arena--Playing Area Class I facility",
    "092": "Sports Arena--Playing Area Class II facility",
    "093": "Sports Arena--Playing Area Class III facility",
    "094": "Sports Arena--Playing Area Class IV facility",
    "095": "Transportation Facility Baggage/carousel area",
    "096": "Transportation Facility Airport concourse",
    "097": "Transportation Facility Ticket counter",
    "098": "Warehouse--Storage Area Medium to bulky, palletized items",
    "099": "Warehouse--Storage Area Smaller, hand-carried items",
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
                space_type_codes = space.get_inp(
                    BDL_SpaceKeywords.C_ACTIVITY_DESC
                ).split("-")
            if len(space_type_codes) > 1:
                # Create (n-1) new spaces in all RMDs
                # TODO: How should we name the new space(s)?
                pass
            if len(space_type_codes) == 2:
                # Get area, both LPDs, and lighting power for the space
                space_area = space.get_float(BDL_SpaceKeywords.AREA)
                space_1_lpd = SPACE_TYPE_LPD.get(
                    SPACE_TYPE_CODES.get(space_type_codes[0]), None
                )
                space_2_lpd = SPACE_TYPE_LPD.get(
                    SPACE_TYPE_CODES.get(space_type_codes[1]), None
                )
                space_lighting_power = space_area * space.get_float(
                    BDL_SpaceKeywords.LIGHTING_W_AREA
                )

                # Calculate and save the areas of the spaces
                space_1_area, space_2_area = self.calculate_space_areas(
                    space_area, space_1_lpd, space_2_lpd, space_lighting_power
                )
                self.assign_space_areas(
                    space_name, space_1_area, space_name, space_2_area
                )

                # Assign lighting power per area for each space

                # Calculate misc equipment power density

    def calculate_space_areas(self, space_area, lpd_1, lpd_2, lighting_power):
        # X + Y = Space Area
        # X * LPD_1 + Y * LPD_2 = Lighting Power
        # TODO: solve
        return 0, 0

    def calculate_misc_equipment_power(self):
        # b1*X + b2*Y = Baseline Space Misc. Eq. Power
        # a1/a2 = b1/b2
        pass

    def assign_space_areas(
        self, space_name_1, space_area_1, space_name_2, space_area_2
    ):
        """Assign the space areas to the respective spaces"""
        for rmd in self.app_data.rmds:
            rmd.get_obj(space_name_1).set_inp(BDL_SpaceKeywords.AREA, space_area_1)
            rmd.get_obj(space_name_2).set_inp(BDL_SpaceKeywords.AREA, space_area_2)
