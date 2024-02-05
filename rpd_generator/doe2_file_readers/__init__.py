# these are only the BDL commands that are being fully processed into nodes by the rpd_generator
BDL_COMMANDS = [
    "CONSTRUCTION",
    "SCHEDULE-PD",
    "SPACE",
    "EXTERIOR-WALL",
    "INTERIOR-WALL",
    "UNDERGROUND-WALL",
    "WINDOW",
    "DOOR",
    "ZONE",
    "SYSTEM",
    "PUMP",
    "CIRCULATION-LOOP",
    "CHILLER",
    "BOILER",
    "DW-HEATER",
    "HEAT-REJECTION",
]

# these are the BDL commands that are being partially processed to determine attributes of nodes but are not being
# processed into nodes themselves
BDL_COMMANDS_PARTIAL = [
    "GLOBAL-PARAMETERS",
    "SITE-PARAMETERS",
    "BUILDING-SHADE",
    "FIXED-SHADE",
    "DAY-SCHEDULE-PD",
    "WEEK-SCHEDULE-PD",
    "FLOOR",
    "ZONE-AIR",
    "ZONE-CONTROL",
    "ZONE-FANS",
    "CONDENSING-UNIT",
]
