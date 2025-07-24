from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_MaterialKeywords = BDLEnums.bdl_enums["MaterialKeywords"]
BDL_LayerKeywords = BDLEnums.bdl_enums["LayerKeywords"]
BDL_MaterialTypes = BDLEnums.bdl_enums["MaterialTypes"]


class Material(BaseNode):
    """Material object in the tree."""

    bdl_command = BDL_Commands.MATERIAL

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.material_data_structure = {}
        self.material_type = None

        # data elements with no children
        self.thickness = None
        self.thermal_conductivity = None
        self.density = None
        self.specific_heat = None
        self.r_value = None

    def __repr__(self):
        return f"Material(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for material object."""
        self.material_type = self.get_inp(BDL_MaterialKeywords.TYPE)

        if self.material_type == BDL_MaterialTypes.PROPERTIES:
            self.thickness = self.try_float(
                self.get_inp(BDL_MaterialKeywords.THICKNESS)
            )

            self.thermal_conductivity = self.try_float(
                self.get_inp(BDL_MaterialKeywords.CONDUCTIVITY)
            )

            self.density = self.try_float(self.get_inp(BDL_MaterialKeywords.DENSITY))

            self.specific_heat = self.try_float(
                self.get_inp(BDL_MaterialKeywords.SPECIFIC_HEAT)
            )

        elif self.material_type == BDL_MaterialTypes.RESISTANCE:
            self.r_value = self.try_float(self.get_inp(BDL_MaterialKeywords.RESISTANCE))

    def populate_data_group(self):
        """Populate schema structure for material object."""
        self.material_data_structure["id"] = self.u_name

        no_children_attributes = [
            "reporting_name",
            "notes",
            "thickness",
            "thermal_conductivity",
            "density",
            "specific_heat",
            "r_value",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.material_data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert material object into the rpd data structure."""
        self.rmd.materials.append(self.material_data_structure)

    def clone_with_thickness(self, new_thickness: float):
        """Clone this material with a new thickness and register it in the RMD."""
        new_id = f"{self.u_name}_{str(new_thickness)}"
        if (self.u_name, new_thickness) in self.rmd.material_variants:
            return self.rmd.get_obj(
                self.rmd.material_variants[(self.u_name, new_thickness)]
            )

        new_material = Material(new_id, self.rmd)
        new_material.material_type = self.material_type
        new_material.thermal_conductivity = self.thermal_conductivity
        new_material.density = self.density
        new_material.specific_heat = self.specific_heat
        new_material.r_value = self.r_value
        new_material.thickness = new_thickness

        # Register variant
        self.rmd.material_variants[(self.u_name, new_thickness)] = new_id
        return new_material


class Layer(BaseDefinition):
    """Layer object in the tree."""

    bdl_command = BDL_Commands.LAYERS

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.material_references = None

    def __repr__(self):
        return f"Layer(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for layers object."""
        material_ids = self.get_inp(BDL_LayerKeywords.MATERIAL, [])
        material_ids = (
            material_ids if isinstance(material_ids, list) else [material_ids]
        )

        material_layers = self.get_inp("MATERIAL-LAYERS", [])
        self.material_references = []

        for idx, mat_id in enumerate(material_ids):
            layer_props = material_layers[idx] if idx < len(material_layers) else {}
            true_thickness = layer_props.get("thickness")

            original_material = self.get_obj(mat_id)
            if true_thickness is not None:
                true_thickness = original_material.try_float(true_thickness)

            # If we’ve already seen this material ID with this exact thickness, reuse
            key = (mat_id, true_thickness)
            if key in self.rmd.material_variants:
                resolved_id = self.rmd.material_variants[key]
            else:
                if (
                    original_material.thickness is not None
                    and true_thickness != original_material.thickness
                ):
                    # Need to clone
                    new_material = original_material.clone_with_thickness(
                        true_thickness
                    )
                    resolved_id = new_material.u_name
                else:
                    resolved_id = mat_id
                    self.rmd.material_variants[key] = mat_id  # Register baseline usage

            self.material_references.append(resolved_id)
