from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.schema.schema_enums import SchemaEnums

EnergySourceOptions = SchemaEnums.schema_enums["EnergySourceOptions"]
ElectricalPhaseOptions = SchemaEnums.schema_enums["ElectricalPhaseOptions"]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_FuelMeterKeywords = BDLEnums.bdl_enums["FuelMeterKeywords"]
BDL_ElecMeterKeywords = BDLEnums.bdl_enums["ElecMeterKeywords"]
BDL_FuelTypes = BDLEnums.bdl_enums["FuelTypes"]
BDL_SteamAndCHWaterMeterKeywords = BDLEnums.bdl_enums[
    "SteamAndChilledWaterMeterKeywords"
]
CHILLED_WATER = "CHILLED_WATER"
HOT_WATER = "HOT_WATER"
OTHER = "OTHER"

UNITS_TABLE = {
    0: (1.0, 1.0),
    1: (1.0, 1.0),
    2: (0.293, 3.412969),  # BTU to WH
    3: (0.293, 3.412969),  # BTU/HR to WATT
    4: (4183.830078, 0.000239),  # BTU/LB-F to J/KG-K
    5: (5.678260, 0.176110),  # BTU/HR-SQFT-F to W/M2-K
    6: (1.0, 1.0),  # DEGREES to DEGREES
    7: (0.092903, 10.763915),  # SQFT to M2
    8: (0.028317, 35.314724),  # CUFT to M3
    9: (0.453592, 2.204624),  # LB/HR to KG/HR
    10: (16.018459, 0.062428),  # LB/CUFT to KG/M3
    11: (0.447040, 2.236936),  # MPH to M/S
    12: (0.527178, 1.896893),  # BTU/HR-F to W/K
    13: (0.304800, 3.280840),  # FT to M
    14: (1.730735, 0.577789),  # BTU/HR-FT-F to W/M-K
    15: (3.152480, 0.317211),  # BTU/HR- SQFT to WATT /M2
    16: (2.540000, 0.393701),  # IN to CM
    17: (0.393700, 2.540005),  # UNITS/IN to UNITS/CM
    18: (1.0, 1.0),  # UNITS to UNITS
    19: (0.453592, 2.204624),  # LB to KG
    20: (1.0, 1.0),  # FRAC.OR MULT
    21: (1.0, 1.0),  # HOURS to HRS
    22: (1.0, 1.0),  # PERCENT-RH to PERCENT-RH
    23: (1.699010, 0.588578),  # CFM to M3/H
    24: (25.400000, 0.039370),  # IN-WATER to MM-WATER
    25: (4.882400, 0.204817),  # LB/SQFT to KG/M2
    26: (1.0, 1.0),  # KW to KW
    27: (10.763920, 0.092903),  # W/SQFT to W/M2
    28: (25.000000, 0.040000),  # THERMS to THERMIES
    29: (0.514440, 1.943861),  # KNOTS to M/SEC
    30: (0.176228, 5.674467),  # HR-SQFT-F /BTU to M2-K /W
    31: (1.0, 1.0),  # $DOLLARS to $DOLLARS
    32: (0.293, 3.412969),  # MBTU/HR to MWATT
    33: (1.0, 1.0),  # YEARS to YEARS
    34: (1.0, 1.0),  # $/HR to $/HR
    35: (1.0, 1.0),  # HRS/YEARS to HRS/YEARS
    36: (1.0, 1.0),  # PERCENT to PERCENT
    37: (1.0, 1.0),  # $/MONTH to $/MONTH
    38: (1.078000, 0.927644),  # GALLONS/MIN/TON
    39: (0.645683, 1.548748),  # BTU/LB to WH/KG
    40: (68.947571, 0.014504),  # LBS/SQFT-GAGE to MBAR-GAGE
    41: (1.0, 1.0),  # $/UNIT to $/UNIT
    42: (0.293, 3.412969),  # BTU/HR/PERSON to W/PERSON
    43: (1.0, 1.0),  # LBS/LB to KGS/KG
    44: (1.0, 1.0),  # BTU/BTU to KWH/KWH
    45: (0.453590, 2.204634),  # LBS/KW to KG/KW
    46: (1.0, 1.0),  # REV/MIN to REV/MIN
    47: (0.284410, 3.516051),  # KW/TON to KW/KW
    48: (0.293, 3.412969),  # MBTU to MWH
    49: (3.785410, 0.264172),  # GAL to LITER
    50: (0.063100, 15.847859),  # GPM to L/S
    51: (1897.800049, 0.000527),  # BTU/F to J/K
    52: (1.0, 1.0),  # KWH to KWH
    53: (1.0, 1.0),  # $/UNIT-HR to $/UNIT-HR
    54: (0.588500, 1.699235),  # KW/CFM to KW/M3/HR
    55: (20428.400391, 0.000049),  # BTU/SQFT-F to J/M2-K
    56: (1.0, 1.0),  # HR/HR to HR/HR
    57: (6226.479980, 0.000161),  # BTU/FT-F to J/M-K
    58: (0.555556, 1.799999),  # R to K
    59: (33.863800, 0.029530),  # INCH MER to MBAR
    60: (0.264170, 3.785441),  # UNITS/GAL/MIN to UNITS/LITER/MIN
    61: (0.031056, 32.199585),  # (HR-SQFT-F/BTU)2 to (M2-K /W)2
    62: (0.293, 3.412969),  # KBTU/HR to KW
    63: (0.293, 3.412969),  # KBTU to KWH
    64: (0.471900, 2.119093),  # CFM to L/S
    65: (18.288000, 0.054681),  # CFM/SQFT to M3/H-M2
    66: (1.799900, 0.555586),  # 1/R to 1/K
    67: (1.943860, 0.514440),  # 1/KNOT to SEC/M
    68: (10.763910, 0.092903),  # FOOTCANDLES to LUX
    69: (3.426259, 0.291864),  # FOOTLAMBERT to CANDELA/M2
    70: (1.0, 1.0),  # LUMEN / WATT to LUMEN / WATT
    71: (3.152480, 0.317211),  # KBTU/SQFT-YR to KWH/M2-YR
    72: (0.555556, 1.799999),  # F (DELTA) to C (DELTA)
    73: (0.012202, 81.953773),  # BTU/DAY to WATT
    74: (1.0, 1.0),  # $/YEAR to $/YEAR
    75: (0.293, 3.412969),  # BTU/WATT to WATT/WATT
    76: (1.0, 1.0),  # RADIANS to RADIANS
    77: (3.413000, 0.292997),  # WATT/BTU to WATT/WATT
    78: (1.0, 1.0),  # BTU to KWH
    79: (1.0, 1.0),  # WATT to WATT
    80: (1.0, 1.0),  # LUMENS to LUMENS
    81: (3.115335, 0.320993),  # BTU/HR-FT-R2 to W/M-K2
    82: (1.488163, 0.671969),  # LB/FT-S to KG/M-S
    83: (2.678693, 0.373316),  # LB/FT-S-R to KG/M-S-K
    84: (28.833212, 0.034682),  # LB/CUFT-R to KG/M3-K
    85: (1.730741, 0.577787),  # BTU/HR-FT-R to W/M-K
    86: (2.831700, 0.353145),  # THERM to M3
    87: (2.831700, 0.353145),  # THERM/HR to M3/HR
    88: (0.907180, 1.102317),  # TON-HRS to TONNE-HRS
    89: (0.907180, 1.102317),  # TONS to TONNES
    90: (1.0, 1.0),  # BTU/UNIT to BTU/UNIT
    91: (1.0, 1.0),  # $ to $
    92: (0.264170, 3.785441),  # KW/GAL/MIN to KW/LITER/MIN
    93: (0.448831, 2.228010),  # CUFT/GAL to M3-MIN/H-LITERS
    94: (1.0, 1.0),  # MINUTES to MINUTES
    95: (1.0, 1.0),  # UNUSED to UNUSED
    96: (1.0, 1.0),  # UNUSED to UNUSED
    97: (1.0, 1.0),  # UNUSED to UNUSED
    98: (1.0, 1.0),  # UNUSED to UNUSED
    99: (1.0, 1.0),  # UNUSED to UNUSED
    100: (1.0, 1.0),  # UNUSED to UNUSED
    101: (1.0, 1.0),  # UNUSED to UNUSED
    102: (1.0, 1.0),  # UNUSED to UNUSED
    103: (1.0, 1.0),  # UNUSED to UNUSED
    104: (1.0, 1.0),  # UNUSED to UNUSED
    105: (1.0, 1.0),  # UNUSED to UNUSED
    106: (1.0, 1.0),  # UNUSED to UNUSED
    107: (1.0, 1.0),  # UNUSED to UNUSED
    108: (1.0, 1.0),  # UNUSED to UNUSED
    109: (1.0, 1.0),  # UNUSED to UNUSED
    110: (1.0, 1.0),  # UNUSED to UNUSED
    111: (1.0, 1.0),  # UNUSED to UNUSED
    112: (1.0, 1.0),  # UNUSED to UNUSED
    113: (0.555560, 1.799986),  # BTU-F/BTU to KWH-C/KWH
    114: (1.0, 1.0),  # UNUSED to UNUSED
    115: (1.0, 1.0),  # VOLTS to VOLTS
    116: (1.0, 1.0),  # C to C
    117: (1.0, 1.0),  # AMPS to AMPS
    118: (1.0, 1.0),  # VOLTS/C to VOLTS/C
    119: (1.0, 1.0),  # 1/C to 1/C
    120: (0.005080, 196.850388),  # FT/MIN to M/S
    121: (227.160004, 0.004402),  # GAL/MIN to LITERS/HR
    122: (588.500000, 0.001699),  # KW/CFM to W/M3/HR
    123: (0.000527, 1896.892578),  # BTU/HR-F to J/K
    124: (0.102000, 9.803922),  # HP to kW
    125: (0.483200, 2.069536),  # CFM/TON to (M3/H)/KW
    126: (3.221000, 0.310463),  # CFM-F/BTUH to (M3/H)-C/WATT
    127: (0.017940, 55.741360),  # GPM/TON to L/S-KW
    128: (2.990000, 0.334448),  # FT to kPa
    129: (3.517000, 0.284333),  # TONS to KW
    130: (1.0, 1.0),  # 1/VOLTS to 1/VOLTS
    131: (1.0, 1.0),  # (C-M2)/W to (C-M2)/W
    132: (1.0, 1.0),  # (C-M-SEC)/W to (C-M-SEC)/W
    133: (1.0, 1.0),  # W/M2 to W/M2
    134: (0.293, 3.412969),  # TDV-MBTUH to TDV-MW
    135: (0.293, 3.412969),  # TDV-MBTU to TDV-MWH
    136: (0.293, 3.412969),  # TDV-KBTU/KWH to TDV-KWH/KWH
    137: (0.010000, 100.000000),  # TDV-KBTU/THERM to TDV-KWH/KWH
    138: (0.092903, 10.763915),  # FT2/HR to M2/SEC
    139: (0.063100, 15.847859),  # GPM to L/S
    140: (0.304800, 3.280840),  # FT/S to M/S
    141: (0.577800, 1.730703),  # HR-FT-F/BTU to M-K/W
}


class MasterMeters(BaseDefinition):

    bdl_command = BDL_Commands.MASTER_METERS

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.bdl_obj_instances[u_name] = self

        self.rmd.master_meters = u_name

    def __repr__(self):
        return f"MasterMeters(u_name='{self.u_name}')"


class FuelMeter(BaseDefinition):

    bdl_command = BDL_Commands.FUEL_METER

    fuel_type_map = {
        BDL_FuelTypes.NATURAL_GAS: EnergySourceOptions.NATURAL_GAS,
        BDL_FuelTypes.LPG: EnergySourceOptions.PROPANE,
        BDL_FuelTypes.FUEL_OIL: EnergySourceOptions.FUEL_OIL,
        BDL_FuelTypes.DIESEL_OIL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.COAL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.METHANOL: EnergySourceOptions.OTHER,
        BDL_FuelTypes.OTHER_FUEL: EnergySourceOptions.OTHER,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.fuel_meter_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.fuel_type = None
        self.energy_unit = None
        self.demand_unit = None
        self.thermal_value = None

    def __repr__(self):
        return f"FuelMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for FuelMeter object."""
        fuel_meter_type = self.get_inp(BDL_FuelMeterKeywords.TYPE)
        self.fuel_type = self.fuel_type_map.get(fuel_meter_type)
        self.energy_unit = self.try_int(self.get_inp(BDL_FuelMeterKeywords.UNIT_INDEX))
        self.demand_unit = self.try_int(
            self.get_inp(BDL_FuelMeterKeywords.DEM_UNIT_INDEX)
        )
        self.thermal_value = self.try_float(
            self.get_inp(BDL_FuelMeterKeywords.ENERGY_UNIT)
        )  # Energy/Unit = Btu/(Energy Unit)


class ElecMeter(BaseDefinition):

    bdl_command = BDL_Commands.ELEC_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.electric_meter_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"ElecMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        transformer_size = self.get_inp(BDL_ElecMeterKeywords.TRANSFORMER_SIZE)
        if transformer_size:
            transformer = Transformer(self)
            transformer.populate_data_elements()
            transformer.populate_data_group()
            transformer.insert_to_rpd()


class UtilityRate(BaseDefinition):

    bdl_command = BDL_Commands.UTILITY_RATE

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.utility_rate_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"UtilityRate(u_name='{self.u_name}')"


class ElecGenerator(BaseDefinition):
    """ElecGenerator object in the tree."""

    bdl_command = BDL_Commands.ELEC_GENERATOR

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.elec_generator_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

    def __repr__(self):
        return f"ElecGenerator(u_name='{self.u_name}')"


class SteamMeter(BaseNode):
    """Steam Meter object in the tree."""

    bdl_command = BDL_Commands.STEAM_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.steam_meter_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = HOT_WATER
        self.energy_source_type = OTHER

    def __repr__(self):
        return f"SteamMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.get_inp(BDL_SteamAndCHWaterMeterKeywords.CIRCULATION_LOOP)

    def populate_data_group(self):
        """Populate schema structure for ExternalFluidSource object."""
        self.data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "energy_source_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.rmd.external_fluid_sources.append(self.data_structure)


class CHWMeter(BaseNode):
    """Chiled Water Meter object in the tree."""

    bdl_command = BDL_Commands.CHW_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.chilled_water_meter_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = CHILLED_WATER
        self.energy_source_type = OTHER

    def __repr__(self):
        return f"CHWMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.get_inp(BDL_SteamAndCHWaterMeterKeywords.CIRCULATION_LOOP)

    def populate_data_group(self):
        """Populate schema structure for ExternalFluidSource object."""
        self.data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "energy_source_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.rmd.external_fluid_sources.append(self.data_structure)


class Transformer:
    def __init__(self, meter):
        self.meter = meter
        self.name = meter.u_name + " Transformer"
        self.meter.rmd.bdl_obj_instances[self.name] = self

        self.data_structure = {}

        self.transformer_type = None
        self.phase = ElectricalPhaseOptions.SINGLE_PHASE
        self.efficiency = None
        self.capacity = None
        self.peak_load = None

    def populate_data_elements(self):
        """Populate data elements for Transformer object."""
        self.capacity = (
            self.meter.try_float(
                self.meter.get_inp(BDL_ElecMeterKeywords.TRANSFORMER_SIZE)
            )
            * 1000
        )
        transformer_loss = (
            self.meter.get_inp(BDL_ElecMeterKeywords.TRANSFORMER_LOSS) or 0
        )
        self.efficiency = 1 - self.meter.try_float(transformer_loss)

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        if self.transformer_type is not None:
            self.data_structure["type"] = self.transformer_type

        for attr in ("phase", "efficiency", "capacity", "peak_load"):
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.meter.rmd.transformers.append(self.data_structure)
