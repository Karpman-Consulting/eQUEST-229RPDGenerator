import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords, Space

# TODO: Update some of these names to match naming convention in enums from dropdowns
SPACE_TYPE_LPD = {
    "Auditorium": 0.90,
    "Convention center": 0.70,
    "Exercise center": 0.30,
    "Gymnasium": 0.40,
    "Motion picture theater": 1.20,
    "Penitentiary audience seating": 0.70,
    "Performing arts theater": 2.60,
    "Religious facility": 1.70,
    "Sports arena": 0.40,
    "Transportation facility": 0.50,
    "All other audience seating areas": 0.90,
    "Atrium <= 40 ft": 0.0375,  # per foot in total height. Revisit TODO
    "Atrium > 40 ft": 0.50,  # + 0.025 per foot in total height. Revisit TODO
    "Banking activity area": 1.50,
    "Penitentiary classroom": 1.30,
    "Preschool through 12th grade, laboratory, and shop classrooms": 1.40,
    "All other classroom/lecture halls/training room": 1.40,
    "Conference/Meeting/Multipurpose Room": 1.30,
    "Confinement Cells": 0.90,
    "Copy/Print Room": 0.90,
    "Facility for the visually impaired corridor": 1.15,
    "Hospital corridor": 1.00,
    "Manufacturing facility corridor": 0.50,
    "All other corridors": 0.50,
    "Courtroom": 1.90,
    "Computer Room": 2.14,
    "Penitentiary dining area": 1.30,
    "Facility for the visually impaired dining room": 3.32,
    "Bar/lounge or leisure dining": 1.40,
    "Cafeteria or fast food dining": 0.90,
    "Family dining": 2.10,
    "All other dining areas": 0.90,
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
    "Facility for the visually impaired lobby": 2.26,
    "Elevator lobby": 0.80,
    "Hotel lobby": 1.10,
    "Motion picture theater lobby": 1.10,
    "Performing arts theater lobby": 3.30,
    "All other lobbies": 1.30,
    "Locker Room": 0.60,
    "Healthcare facility lounge/breakroom": 0.80,
    "All other lounges/breakrooms": 1.20,
    "Enclosed office": 1.10,
    "Open plan office": 1.10,
    "Parking Area, Interior": 0.20,
    "Pharmacy Area": 1.20,
    "Facility for the visually impaired restroom": 1.52,
    "All other restrooms": 0.90,
    "Sales Area": 1.70,
    "Seating Area, General": 0.68,
    "Stairwell": 0.60,
    "Storage Room Hospital": 0.90,
    "Storage Room >= 50 ft2": 0.80,
    "Storage Room < 50 ft2": 0.80,
    "Vehicular Maintenance Area": 0.70,
    "Workshop": 1.90,
    "Assisted Living Facility Chapel": 2.77,
    "Assisted Living Facility Recreation room": 3.02,
    "Convention Center--Exhibit Space": 1.30,
    "Dormitory--Living Quarters": 1.11,
    "Fire Station--Sleeping Quarters": 0.30,
    "Gymnasium/Fitness Center Exercise area": 0.90,
    "Gymnasium/Fitness Center Playing area": 1.40,
    "Healthcare Facility Emergency room": 2.70,
    "Healthcare Facility Exam/treatment room": 1.50,
    "Healthcare Facility Medical supply room": 1.40,
    "Healthcare Facility Nursery": 0.60,
    "Healthcare Facility Nurse's station": 1.00,
    "Healthcare Facility Operating room": 2.20,
    "Healthcare Facility Patient room": 0.70,
    "Healthcare Facility Physical therapy room": 0.90,
    "Healthcare Facility Recovery room": 0.80,
    "Library Reading area": 1.20,
    "Library Stacks": 1.70,
    "Manufacturing Facility Detailed manufacturing area": 2.10,
    "Manufacturing Facility Equipment room": 1.20,
    "Manufacturing Facility Extra high bay area (>50 ft floor-to-ceiling height)": 1.32,
    "Manufacturing Facility High bay area (25 to 50 ft floor-to-ceiling height)": 1.70,
    "Manufacturing Facility Low bay area (<25 ft floor-to-ceiling height)": 1.20,
    "Museum General exhibition area": 1.00,
    "Museum Restoration room": 1.70,
    "Post Office--Sorting Area": 1.20,
    "Religious Facility Fellowship hall": 0.90,
    "Religious Facility Worship/pulpit/choir area": 2.40,
    "Retail Facilities Dressing/fitting room": 0.89,
    "Retail Facilities Mall concourse": 1.70,
    "Sports Arena--Playing Area Class I facility": 4.61,
    "Sports Arena--Playing Area Class II facility": 3.01,
    "Sports Arena--Playing Area Class III facility": 2.26,
    "Sports Arena--Playing Area Class IV facility": 1.50,
    "Transportation Facility Baggage/carousel area": 1.00,
    "Transportation Facility Airport concourse": 0.60,
    "Transportation Facility Ticket counter": 1.50,
    "Warehouse--Storage Area Medium to bulky, palletized items": 0.90,
    "Warehouse--Storage Area Smaller, hand-carried items": 1.40,
}

SPACE_TYPES_MAP = {
    "001": "Auditorium",
    "002": "Convention center",
    "003": "Exercise center",
    "004": "Gymnasium",
    "005": "Motion picture theater",
    "006": "Penitentiary audience seating",
    "007": "Performing arts theater",
    "008": "Religious facility",
    "009": "Sports arena",
    "010": "Transportation facility",
    "011": "All other audience seating areas",
    "012": "Atrium <= 40 ft",
    "013": "Atrium > 40 ft",
    "014": "Banking activity area",
    "015": "Penitentiary classroom",
    "016": "Preschool through 12th grade, laboratory, and shop classrooms",
    "017": "All other classroom/lecture halls/training room",
    "018": "Conference/Meeting/Multipurpose Room",
    "019": "Confinement Cells",
    "020": "Copy/Print Room",
    "021": "Facility for the visually impaired corridor",
    "022": "Hospital corridor",
    "023": "Manufacturing facility corridor",
    "024": "All other corridors",
    "025": "Courtroom",
    "026": "Computer Room",
    "027": "Penitentiary dining area",
    "028": "Facility for the visually impaired dining room",
    "029": "Bar/lounge or leisure dining",
    "030": "Cafeteria or fast food dining",
    "031": "Family dining",
    "032": "All other dining areas",
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
    "043": "Facility for the visually impaired lobby",
    "044": "Elevator lobby",
    "045": "Hotel lobby",
    "046": "Motion picture theater lobby",
    "047": "Performing arts theater lobby",
    "048": "All other lobbies",
    "049": "Locker Room",
    "050": "Healthcare facility lounge/breakroom",
    "051": "All other lounges/breakrooms",
    "052": "Enclosed office",
    "053": "Open plan office",
    "054": "Parking Area, Interior",
    "055": "Pharmacy Area",
    "056": "Facility for the visually impaired restroom",
    "057": "All other restrooms",
    "058": "Sales Area",
    "059": "Seating Area, General",
    "060": "Stairwell",
    "061": "Storage Room Hospital",
    "062": "Storage Room >= 50 ft2",
    "063": "Storage Room < 50 ft2",
    "064": "Vehicular Maintenance Area",
    "065": "Workshop",
    "066": "Assisted Living Facility Chapel",
    "067": "Assisted Living Facility Recreation room",
    "068": "Convention Center--Exhibit Space",
    "069": "Dormitory--Living Quarters",
    "070": "Fire Station--Sleeping Quarters",
    "071": "Gymnasium/Fitness Center Exercise area",
    "072": "Gymnasium/Fitness Center Playing area",
    "073": "Healthcare Facility Emergency room",
    "074": "Healthcare Facility Exam/treatment room",
    "075": "Healthcare Facility Medical supply room",
    "076": "Healthcare Facility Nursery",
    "077": "Healthcare Facility Nurse's station",
    "078": "Healthcare Facility Operating room",
    "079": "Healthcare Facility Patient room",
    "080": "Healthcare Facility Physical therapy room",
    "081": "Healthcare Facility Recovery room",
    "082": "Library Reading area",
    "083": "Library Stacks",
    "084": "Manufacturing Facility Detailed manufacturing area",
    "085": "Manufacturing Facility Equipment room",
    "086": "Manufacturing Facility Extra high bay area (>50 ft floor-to-ceiling height)",
    "087": "Manufacturing Facility High bay area (25 to 50 ft floor-to-ceiling height)",
    "088": "Manufacturing Facility Low bay area (<25 ft floor-to-ceiling height)",
    "089": "Museum General exhibition area",
    "090": "Museum Restoration room",
    "091": "Post Office--Sorting Area",
    "092": "Religious Facility Fellowship hall",
    "093": "Religious Facility Worship/pulpit/choir area",
    "094": "Retail Facilities Dressing/fitting room",
    "095": "Retail Facilities Mall concourse",
    "096": "Sports Arena--Playing Area Class I facility",
    "097": "Sports Arena--Playing Area Class II facility",
    "098": "Sports Arena--Playing Area Class III facility",
    "099": "Sports Arena--Playing Area Class IV facility",
    "100": "Transportation Facility Baggage/carousel area",
    "101": "Transportation Facility Airport concourse",
    "102": "Transportation Facility Ticket counter",
    "103": "Warehouse--Storage Area Medium to bulky, palletized items",
    "104": "Warehouse--Storage Area Smaller, hand-carried items",
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

    # TODO: Remove all the debugging prints at the very end, after review complete
    #           useful to see results without having to dig into debugger
    def predict_space_type(self):
        """Predict the space type based on the specified space C-ACTIVITY-DESC"""
        baseline_rmd = self.app_data.get_rmd(ASHRAE9012019ModelOptions.BASELINE_0)
        for space_name in baseline_rmd.space_map.keys():
            space = baseline_rmd.get_obj(space_name)
            space_type_codes = []
            if space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC):
                print(space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC))
                space_type_codes = space.get_inp(
                    BDL_SpaceKeywords.C_ACTIVITY_DESC
                ).split("-")
            else:
                # Assign default activity type to each space
                print("No C-ACTIVITY-DESC found for space:", space_name)
                continue

            num_space_types = len(space_type_codes)
            if num_space_types == 2:
                print("Space type codes:", space_type_codes)
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
                print("Space area:", space_area)
                print("Space 1 LPD:", space_1_lpd)
                print("Space 2 LPD:", space_2_lpd)
                print("Lighting power:", space_lighting_power)

                # Calculate and save the areas of the spaces
                space_1_area, space_2_area = self.calculate_space_areas(
                    space_area, space_1_lpd, space_2_lpd, space_lighting_power
                )
                print("Space 1 area:", space_1_area)
                print("Space 2 area:", space_2_area)

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
                print("Misc eq power:", space.misc_eq_power[0])
                print("Space 1 misc eq power:", space_1_misc_eq_power)
                print("Space 2 misc eq power:", space_2_misc_eq_power)

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
                print("Occupants:", space.number_of_occupants)
                print("Space 1 occupants:", space_1_occupants)
                print("Space 2 occupants:", space_2_occupants)
                print("--------------")

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
            elif num_space_types > 2:
                # Create (n-1) new, default spaces in all RMDs
                self.add_new_spaces((num_space_types - 1), space_name)

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
