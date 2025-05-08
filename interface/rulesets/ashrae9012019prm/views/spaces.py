import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords, Space
from interface.space_type_prediction_maps import *

# TODO: Remove DEBUG flag and associated print statements when we're done with development here
DEBUG = True


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

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class SpacesSubview(CTkXYFrame):
    # Set right after subviews are created in the SpacesView
    json_representation = None

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        self.is_view_populated = False

    def __repr__(self):
        return "SpacesSubview"

    def open_subview(self):
        self.spaces_view.main_window.next_button.configure(command=self.view_next)
        self.spaces_view.main_window.back_button.configure(command=self.view_back)
        self.spaces_view.main_window.show_back_next_buttons_toggle()
        self.populate_subview() if not self.is_view_populated else None

    def view_next(self):
        if "SurfacesView" in self.spaces_view.main_window.views:
            self.spaces_view.main_window.show_view("SurfacesView")
        else:
            self.spaces_view.main_window.show_view("SystemsView")

    def view_back(self):
        self.spaces_view.main_window.show_view("ZonesView")

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

        # Populate with any loaded data if it exists
        self.set_subview_data()

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
        status_combo = None
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

        self.widget_rows.append(
            [
                name_label,
                status_combo,
                lighting_space_type_combo,
                envelope_space_type_combo,
                ventilation_space_type_combo,
                swh_space_type_combo,
                lighting_occ_controls_combo,
                daylighting_controls_combo,
                occ_controls_modeled_checkbox,
                daylighting_modeled_checkbox,
            ]
        )

    def get_subview_data(self):
        subview_data = []
        for row in self.widget_rows:
            (
                name_label,
                status_combo,
                lighting_space_type_combo,
                envelope_space_type_combo,
                ventilation_space_type_combo,
                swh_space_type_combo,
                lighting_occ_controls_combo,
                daylighting_controls_combo,
                occ_controls_modeled_checkbox,
                daylighting_modeled_checkbox,
            ) = row
            space_data = {
                "Name": name_label.cget("text"),
                "Status": status_combo.get() if status_combo else "",
                "Lighting Space Type": lighting_space_type_combo.get(),
                "Envelope Space Type": envelope_space_type_combo.get(),
                "Ventilation Space Type": ventilation_space_type_combo.get(),
                "SWH Space Type": swh_space_type_combo.get(),
                "Lighting Occ. Controls": lighting_occ_controls_combo.get(),
                "Daylighting Controls": daylighting_controls_combo.get(),
                "Occ. Controls Modeled": occ_controls_modeled_checkbox.get(),
                "Daylighting Modeled": daylighting_modeled_checkbox.get(),
            }
            subview_data.append(space_data)
        return subview_data

    # TODO: Right now missing data in a space row will default to empty strings for the fields.
    #           Defaults will change once guessing is complete and the view structure changes.
    def set_subview_data(self):
        for row in self.widget_rows:
            (
                name_label,
                status_combo,
                lighting_space_type_combo,
                envelope_space_type_combo,
                ventilation_space_type_combo,
                swh_space_type_combo,
                lighting_occ_controls_combo,
                daylighting_controls_combo,
                occ_controls_modeled_checkbox,
                daylighting_modeled_checkbox,
            ) = row
            space_row_data = self.get_space_data(name_label.cget("text"))
            if not space_row_data:
                # If no data found, skip this row
                continue
            status_combo.set(space_row_data.get("Status", "")) if status_combo else None
            lighting_space_type_combo.set(space_row_data.get("Lighting Space Type", ""))
            envelope_space_type_combo.set(space_row_data.get("Envelope Space Type", ""))
            ventilation_space_type_combo.set(
                space_row_data.get("Ventilation Space Type", "")
            )
            swh_space_type_combo.set(space_row_data.get("SWH Space Type", ""))
            lighting_occ_controls_combo.set(
                space_row_data.get("Lighting Occ. Controls", "")
            )
            daylighting_controls_combo.set(
                space_row_data.get("Daylighting Controls", "")
            )
            # Handle the checkboxes for modeled via schedule
            occ_controls_modeled = space_row_data.get("Occ. Controls Modeled", False)
            (
                occ_controls_modeled_checkbox.select()
                if occ_controls_modeled
                else occ_controls_modeled_checkbox.deselect()
            )
            daylighting_modeled = space_row_data.get("Daylighting Modeled", False)
            (
                daylighting_modeled_checkbox.select()
                if daylighting_modeled
                else daylighting_modeled_checkbox.deselect()
            )

    def get_space_data(self, space_name):
        """Helper method to get space data from the app_data for a specific space."""
        spaces_data = self.app_data.all_project_data.get(self.json_representation, [])
        for space in spaces_data:
            if space.get("Name") == space_name:
                return space
        return None

    def predict_space_type(self):
        """Predict the space type based on the specified space C-ACTIVITY-DESC"""
        baseline_rmd = self.app_data.get_rmd(ASHRAE9012019ModelOptions.BASELINE_0)

        for space_name in baseline_rmd.space_map.keys():
            no_valid_codes = False
            space = baseline_rmd.get_obj(space_name)
            space_type_codes = []
            if space.get_inp(BDL_SpaceKeywords.C_ACTIVITY_DESC):
                space_type_codes = self.get_valid_space_codes(space)

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
                # If space LPD values match, we cannot predict the area
                if space_1_lpd == space_2_lpd:
                    no_valid_codes = True
                else:
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

                    if DEBUG:
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
                no_valid_codes = True

            # Fall back to substring and LPD-based prediction or defaults if no valid codes (or invalid codes) found
            if no_valid_codes:
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

        if DEBUG:
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
                        print(
                            f"SWH space type: {data.service_water_heating_space_type}"
                        )
                        print("--------------")
                        print(
                            f"Misc eq ids: {data.misc_eq_id if hasattr(data, 'misc_eq_id') else 'N/A'}"
                        )
                        print(
                            f"Int lighting IDs: {data.int_ltg_id if hasattr(data, 'int_ltg_id') else 'N/A'}"
                        )
                        print(
                            f"Occupant multiplier schedule: {data.occupant_multiplier_schedule if hasattr(data, 'occupant_multiplier_schedule') else 'N/A'}"
                        )
                        print(
                            f"Occupant sensible heat gain: {data.occupant_sensible_heat_gain if hasattr(data, 'occupant_sensible_heat_gain') else 'N/A'}"
                        )
                        print(
                            f"Occupant latent heat gain: {data.occupant_latent_heat_gain if hasattr(data, 'occupant_latent_heat_gain') else 'N/A'}"
                        )
                        print(
                            f"Status type: {data.status_type if hasattr(data, 'status_type') else 'N/A'}"
                        )
                        print(
                            f"Interior lighting multiplier schedule: {data.int_ltg_lighting_multiplier_schedule if hasattr(data, 'int_ltg_lighting_multiplier_schedule') else 'N/A'}"
                        )
                        print(
                            f"Misc. equipment multiplier schedule: {data.misc_eq_multiplier_schedule if hasattr(data, 'misc_eq_multiplier_schedule') else 'N/A'}"
                        )
                        print(
                            f"Misc. equipment sensible fraction: {data.misc_eq_sensible_fraction if hasattr(data, 'misc_eq_sensible_fraction') else 'N/A'}"
                        )
                        print(
                            f"Misc. equipment latent fraction: {data.misc_eq_latent_fraction if hasattr(data, 'misc_eq_latent_fraction') else 'N/A'}"
                        )

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
        for rmd in self.app_data.rmds:
            for name, data in self.new_spaces.items():
                original_space = None
                new_space = None
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
                    # Add new space to bdl_obj_instances
                    rmd.bdl_obj_instances[new_space_name] = new_space
                    rmd.space_map[new_space_name] = rmd.space_map.get(name)

                # Copy over info from original space
                new_space.misc_eq_id = original_space.misc_eq_id
                new_space.int_ltg_id = original_space.int_ltg_id
                new_space.occupant_multiplier_schedule = (
                    original_space.occupant_multiplier_schedule
                )
                new_space.occupant_sensible_heat_gain = (
                    original_space.occupant_sensible_heat_gain
                )
                new_space.occupant_latent_heat_gain = (
                    original_space.occupant_latent_heat_gain
                )
                new_space.status_type = original_space.status_type
                new_space.int_ltg_lighting_multiplier_schedule = (
                    original_space.int_ltg_lighting_multiplier_schedule
                )
                new_space.misc_eq_multiplier_schedule = (
                    original_space.misc_eq_multiplier_schedule
                )
                new_space.misc_eq_sensible_fraction = (
                    original_space.misc_eq_sensible_fraction
                )
                new_space.misc_eq_latent_fraction = (
                    original_space.misc_eq_latent_fraction
                )
