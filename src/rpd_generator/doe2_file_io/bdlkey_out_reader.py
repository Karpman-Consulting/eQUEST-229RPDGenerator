from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------


@dataclass
class SymbolEntry:
    name: str
    value: Optional[int] = None
    type_code: Optional[int] = None


@dataclass
class KeywordDef:
    index: int
    name: str
    abbrev: Optional[str] = None
    units: Optional[str] = None
    raw_type: Optional[str] = None
    category: Optional[str] = None  # symbolic / numeric / other
    length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[str] = None
    symbols: List[SymbolEntry] = field(default_factory=list)


@dataclass
class CommandDef:
    command_num: int
    name: str
    abbrev: Optional[str]
    keywords: Dict[str, KeywordDef] = field(default_factory=dict)

    # TYPE-specific keyword buckets, e.g.
    # TYPE=GLASS-TYPE → KW list
    type_keyword_map: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class BDLCommands:
    commands: Dict[str, CommandDef]


# ---------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------


def parse_bdl_commands(path: str) -> BDLCommands:
    with open(path, "r", errors="ignore") as f:
        text = f.read()

    commands: Dict[str, CommandDef] = {}

    # iterate over all COMMAND NUM blocks
    for block in _split_command_blocks(text):
        cmd = _parse_single_command(block)
        if cmd is not None:
            commands[cmd.name] = cmd

    return BDLCommands(commands=commands)


# ---------------------------------------------------------------------
# Split file into COMMAND NUM blocks
# ---------------------------------------------------------------------


def _split_command_blocks(text: str) -> List[str]:
    """Return each full command block text."""
    matches = list(re.finditer(r"\*{10}COMMAND NUM\s*=\s*\d+", text))
    blocks = []

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append(text[start:end])

    return blocks


# ---------------------------------------------------------------------
# Parse a single COMMAND block into a CommandDef
# ---------------------------------------------------------------------


def _parse_single_command(block: str) -> Optional[CommandDef]:
    # Extract command number
    m = re.search(r"COMMAND NUM\s*=\s*(\d+)", block)
    if not m:
        return None
    cmd_num = int(m.group(1))

    # Find command header line (the line containing command name AND abbrev)
    header_match = re.search(
        r"\n\s*([A-Z0-9\-\*]+)\s+([A-Z0-9\-\*]+)\s+\d+\s+\d+\s+\d+", block
    )
    if not header_match:
        return None

    cmd_name = header_match.group(1)
    cmd_abbrev = header_match.group(2)

    cmd = CommandDef(command_num=cmd_num, name=cmd_name, abbrev=cmd_abbrev)

    # Parse all keyword lines under this block
    kw_pattern = re.compile(r"\n\s*(\d+>)")
    iterator = list(kw_pattern.finditer(block))

    for i, match in enumerate(iterator):
        start = match.start()
        end = iterator[i + 1].start() if i + 1 < len(iterator) else len(block)
        kw_text = block[start:end]

        kw = _parse_keyword(kw_text)
        if kw:
            cmd.keywords[kw.name] = kw

    # Build TYPE→keyword mapping
    _build_type_keyword_map(cmd)

    return cmd


# ---------------------------------------------------------------------
# Parse a keyword section
# ---------------------------------------------------------------------


def _parse_keyword(text: str) -> Optional[KeywordDef]:
    """
    text contains:
       n> KEYWORD ... TYPE ... LEN ... (for numeric) MIN ... MAX ... DEFAULT
       SYMBOL TABLE ENTRY lines (for symbolic keywords)
    """

    # 1) Find the first non-empty line that contains "n>"
    header = None
    for line in text.splitlines():
        if line.strip():
            header = line
            break

    if header is None:
        return None

    # Expect something like:
    #   "  1> TYPE  ... "
    m = re.match(r"\s*(\d+)>?\s+([A-Z0-9\-\*\/]+)(.*)", header)
    if not m:
        return None

    index = int(m.group(1))
    name = m.group(2)
    rest = m.group(3)

    # 2) Tokenize the rest of the header (everything after the keyword name)
    tokens = rest.split()

    # 3) Find where the TYPE column starts, e.g. "Symbolic", "Numeric", "Numnric"
    type_idx = _find_type_token(tokens)
    if type_idx is None:
        raw_type = None
        after_type_tokens: List[str] = []
    else:
        # TYPE is usually two tokens, e.g. "Symbolic Defined", "Numeric Err,Err"
        # but we don't rely on exactly two; we take tokens until the first numeric.
        raw_type_tokens: List[str] = []
        j = type_idx
        while j < len(tokens) and not _is_number(tokens[j]):
            raw_type_tokens.append(tokens[j])
            j += 1
        raw_type = " ".join(raw_type_tokens)
        after_type_tokens = tokens[j:]

    # 4) Category (symbolic / numeric / other)
    category: Optional[str]
    if raw_type:
        if "Symbolic" in raw_type or "Sym" in raw_type:
            category = "symbolic"
        elif "Num" in raw_type or "Numeric" in raw_type or "Numnric" in raw_type:
            category = "numeric"
        else:
            category = "other"
    else:
        category = None

    # 5) Pre-type tokens → abbrev + units (if present)
    abbrev = None
    units = None
    if type_idx is not None and type_idx > 0:
        pre = tokens[:type_idx]
        if len(pre) == 1:
            abbrev = pre[0]
        elif len(pre) >= 2:
            abbrev = pre[0]
            units = " ".join(pre[1:])

    # 6) Parse LEN / MIN / MAX / DEFAULT
    length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[str] = None

    nums = [t for t in after_type_tokens if _is_number(t)]
    if nums:
        # First numeric after TYPE is the LEN
        try:
            length = int(float(nums[0]))
        except ValueError:
            length = None

    # MIN/MAX only make sense for numeric keywords; the CODE-WORD numeric (e.g. 142)
    # that appears for Symbolic keywords is *not* a min/max bound.
    if category == "numeric" and len(nums) >= 3:
        try:
            min_value = float(nums[1])
            max_value = float(nums[2])
        except ValueError:
            min_value = max_value = None

    # DEFAULT: last numeric or a "*...*" phrase like "* Required *", "*No Default*"
    # We scan the entire header so we pick up the trailing default area.
    default_match = re.search(r"(\*[^*]*\*|-?\d+\.\d+|-?\d+)$", header.strip())
    if default_match:
        default = default_match.group(1)

    # 7) SYMBOL TABLE ENTRY lines for symbolic keywords
    symbols: List[SymbolEntry] = []
    for line in text.splitlines()[1:]:
        if "SYMBOL TABLE ENTRY" in line:
            # Standard form:
            # SYMBOL TABLE ENTRY   ON/OFF  TYPE =  142 DEF/REF  -1/ -1  VALUE =    1
            sm = re.search(
                r"ENTRY\s+([A-Z0-9\-\*\/]+)\s+.*TYPE\s*=\s*(\d+).*VALUE\s*=\s*(\d+)",
                line,
            )
            if sm:
                symbols.append(
                    SymbolEntry(
                        name=sm.group(1),
                        type_code=int(sm.group(2)),
                        value=int(sm.group(3)),
                    )
                )
            else:
                # Fallback: at least capture the symbol name
                sm = re.search(r"ENTRY\s+([A-Z0-9\-\*\/]+)", line)
                if sm:
                    symbols.append(SymbolEntry(name=sm.group(1)))

    return KeywordDef(
        index=index,
        name=name,
        abbrev=abbrev,
        units=units,
        raw_type=raw_type,
        category=category,
        length=length,
        min_value=min_value,
        max_value=max_value,
        default=default,
        symbols=symbols,
    )


# ---------------------------------------------------------------------
# TYPE-conditioned keywords
# ---------------------------------------------------------------------


def _build_type_keyword_map(cmd: CommandDef):
    """
    Build TYPE-conditioned keyword buckets.
    Example:
        TYPE = GLASS-TYPE-CODE
        then those keywords belong to the TYPE bucket.
    """
    type_kw = cmd.type_keyword_map

    if "TYPE" not in cmd.keywords:
        return

    type_symbol_names = [s.name for s in cmd.keywords["TYPE"].symbols]

    for sym in type_symbol_names:
        type_kw[sym] = []

    # rule: any keyword whose default type matches TYPE symbols goes into bucket
    for kw in cmd.keywords.values():
        for sym in type_symbol_names:
            if sym in kw.name:
                type_kw[sym].append(kw.name)


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------


def _find_type_token(tokens: List[str]) -> Optional[int]:
    for i, t in enumerate(tokens):
        if "Sym" in t or "Symbolic" in t or "Num" in t or "Numeric" in t:
            return i
    return None


def _is_number(tok: str) -> bool:
    try:
        float(tok.replace(",", ""))
        return True
    except ValueError:
        return False
