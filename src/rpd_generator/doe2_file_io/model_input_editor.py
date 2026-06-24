from functools import partial

import re
from typing import TypedDict, NotRequired


class INPEdits(TypedDict):
    unique_id: str
    change_type: str  # "add", "modify", "restore_default", "delete_with_children", "delete_and_rehome"
    keyword: NotRequired[str]  # only for "modify" and "restore_default"
    value: NotRequired[str]  # only for "modify"
    command: NotRequired[str]  # only for "add" and "modify"
    parent_uid: NotRequired[str]  # only for "add"


BDL_HIERARCHY = {
    "FLOOR": ["SPACE"],
    "SPACE": ["INTERIOR-WALL", "EXTERIOR-WALL", "UNDERGROUND-WALL"],
    "INTERIOR-WALL": ["WINDOW", "DOOR"],
    "EXTERIOR-WALL": ["WINDOW", "DOOR"],
    "SYSTEM": ["ZONE"],
}


class ModelInputEditor:
    """
    This class makes use of the ModelInputReader and ModelInputWriter to expose user-friendly methods for reading and modifying DOE-2 model input files.
    """

    def __init__(self, model_input_path: str):
        self.model_input_path = model_input_path
        self.model_edits = []

    def create_command(
        self, bdl_command: str, unique_id: str, parent_uid=None, **kwargs
    ):
        """
        Queue an 'add' operation to create a new command.
        - bdl_command: e.g., 'SPACE'
        - unique_id: the name of the object instance
        - additional_keywords: list of {keyword: value} dicts
        - parent_uid: unique_id of the parent object (optional)
        """
        additional_keywords = []

        # Convert kwargs to keyword entries so user can do create_space(..., FLOOR=5, ...)
        for k, v in kwargs.items():
            additional_keywords.append({k: v})

        # Build minimal DOE-2 command block text
        block_lines = [f'"{unique_id}" = {bdl_command}']

        for kv in additional_keywords:
            for k, v in kv.items():
                block_lines.append(f"   {k:<18} = {v}")

        block_lines.append("   ..")  # Inline terminator
        block_text = "\n".join(block_lines)

        self.model_edits.append(
            dict(
                change_type="add",
                unique_id=unique_id,
                command=block_text,
                parent_uid=parent_uid,
            )
        )

    # use partial to pre-fill bdl_command and add required keywords for specific commands
    create_system_command = partial(
        create_command, bdl_command="SYSTEM", required_keywords=[]
    )
    create_zone_command = partial(
        create_command, bdl_command="ZONE", required_keywords=[]
    )
    create_space_command = partial(
        create_command, bdl_command="SPACE", required_keywords=[""]
    )
    create_schedule_command = partial(
        create_command, bdl_command="SCHEDULE", required_keywords=[]
    )
    create_week_schedule_command = partial(
        create_command, bdl_command="WEEK-SCHEDULE", required_keywords=[]
    )
    create_day_schedule_command = partial(
        create_command, bdl_command="DAY-SCHEDULE", required_keywords=[]
    )
    create_curve_fit_command = partial(
        create_command, bdl_command="CURVE-FIT", required_keywords=[]
    )
    create_exterior_wall_command = partial(
        create_command, bdl_command="EXTERIOR-WALL", required_keywords=[]
    )
    create_underground_wall_command = partial(
        create_command, bdl_command="UNDERGROUND-WALL", required_keywords=[]
    )
    create_interior_wall_command = partial(
        create_command, bdl_command="INTERIOR-WALL", required_keywords=[]
    )
    create_window_command = partial(
        create_command, bdl_command="WINDOW", required_keywords=[]
    )
    create_door_command = partial(
        create_command, bdl_command="DOOR", required_keywords=[]
    )
    create_boiler_command = partial(
        create_command, bdl_command="BOILER", required_keywords=[]
    )
    create_chiller_command = partial(
        create_command, bdl_command="CHILLER", required_keywords=[]
    )
    create_heat_rejection_command = partial(
        create_command, bdl_command="HEAT-REJECTION", required_keywords=[]
    )
    create_circulation_loop_command = partial(
        create_command, bdl_command="CIRCULATION-LOOP", required_keywords=[]
    )
    create_domestic_water_heater_command = partial(
        create_command, bdl_command="DW-HEATER", required_keywords=[]
    )
    create_pump_command = partial(
        create_command, bdl_command="PUMP", required_keywords=[]
    )
    create_construction_command = partial(
        create_command, bdl_command="CONSTRUCTION", required_keywords=[]
    )
    create_material_command = partial(
        create_command, bdl_command="MATERIAL", required_keywords=[]
    )
    create_layer_command = partial(
        create_command, bdl_command="LAYER", required_keywords=[]
    )
    create_glass_type_command = partial(
        create_command, bdl_command="GLASS-TYPE", required_keywords=[]
    )

    def modify_keyword(self, bdl_command: str, unique_id: str, keyword: str, new_value):
        self.model_edits.append(
            dict(
                change_type="modify",
                unique_id=unique_id,
                keyword=keyword,
                value=new_value,
            )
        )

    def restore_keyword_default(self, unique_id: str, keyword: str):
        self.model_edits.append(
            dict(
                change_type="restore_default",
                unique_id=unique_id,
                keyword=keyword,
            )
        )

    def delete_command_with_all_children(self, bdl_command: str, unique_id: str):
        to_delete = {unique_id}
        queue = [unique_id]

        while queue:
            uid = queue.pop()
            # scan to find direct children in the model input later during validation or via a cached parsed structure
            children = self._find_children_of(uid)
            to_delete.update(children)
            queue.extend(children)

        for uid in sorted(to_delete):
            self.model_edits.append(dict(change_type="delete", unique_id=uid))

    def delete_command_and_rehome_children(
        self, bdl_command: str, unique_id: str, new_parent_uid: str
    ):
        children = self._find_children_of(unique_id)
        for child_uid in children:
            self.model_edits.append(
                dict(
                    change_type="modify",
                    unique_id=child_uid,
                    keyword="PARENT",
                    value=f'"{new_parent_uid}"',
                )
            )
        self.model_edits.append(dict(change_type="delete", unique_id=unique_id))

    def apply(self):
        self._validate_inp_edits()
        result = self.edit_inp_file(self.model_input_path, self.model_edits)
        self.model_edits.clear()
        return result

    def _validate_inp_edits(self):
        """
        Validate the input edits before writing to the model input file.

        Make sure that:
        = unique_id specified for addition does not already exist in the input file and contains no illegal chars.
        - unique_id specificed for deletion exists in the input file.
        - unique_id for a keyword modification exists in the input file.
        - unique_id for a keyword modification is not being made after the command is deleted.
        - keyword(s) specified for modification valid keyword for the given DOE-2 command.
        - value(s) specified for modification valid type/enumeration as expected by DOE-2.
        """
        pass

    def _find_children_of(self, parent_uid: str) -> list[str]:
        """
        Return the list of UIDs of child objects belonging to the given parent object,
        based on BDL_HIERARCHY and the structural placement of blocks in the INP file.
        """
        with open(self.model_input_path, "r", encoding="cp1252", errors="replace") as f:
            lines = f.readlines()

        # Reuse the block scanning helpers from edit_inp_file, so we duplicate minimal logic here:
        def scan_until_terminator(start_idx: int) -> int:
            paren = 0
            in_quote = False
            for i in range(start_idx, len(lines)):
                s = lines[i]
                j = 0
                while j < len(s):
                    ch = s[j]
                    if ch == "$" and not in_quote:
                        break
                    if ch == '"':
                        in_quote = not in_quote
                    elif not in_quote:
                        if ch == "(":
                            paren += 1
                        elif ch == ")":
                            paren = max(0, paren - 1)
                        elif (
                            ch == "."
                            and j + 1 < len(s)
                            and s[j + 1] == "."
                            and paren == 0
                        ):
                            return i
                    j += 1
            return len(lines) - 1

        def find_block_by_uid(uid: str):
            pattern = re.compile(rf'^\s*"{re.escape(uid)}"\s*=\s*([A-Z0-9\-]+)\b')
            for i, line in enumerate(lines):
                if pattern.search(line):
                    return i, scan_until_terminator(i)
            return None

        def command_of(line: str) -> str | None:
            m = re.match(r'^\s*".+?"\s*=\s*([A-Z0-9\-]+)', line)
            return m.group(1) if m else None

        parent_block = find_block_by_uid(parent_uid)
        if not parent_block:
            return []

        p_start, p_end = parent_block
        parent_command = command_of(lines[p_start])
        if parent_command not in BDL_HIERARCHY:
            return []

        allowed_children = set(BDL_HIERARCHY[parent_command])
        children = []

        i = p_start + 1
        while i <= p_end:
            m = re.match(r'^\s*"(.+?)"\s*=\s*([A-Z0-9\-]+)\b', lines[i])
            if m:
                uid = m.group(1)
                cmd = m.group(2)
                if cmd in allowed_children:
                    children.append(uid)
                    _, child_end = scan_until_terminator(i)
                    i = child_end + 1
                    continue
            i += 1

        return children

    @staticmethod
    def edit_inp_file(inp_file_path: str, edits: list[INPEdits]) -> dict:
        """
        In-place edit of a DOE-2 INP file.

        change_type:
          - "modify": find object by unique_id; set keyword=value (insert if missing).
          - "restore_default": delete keyword from object (including multi-line values).
          - "delete_with_children": delete the whole object block and all children in family.
          = "delete_and_rehome": delete the whole object block, rehome children to new parent.
          - "add": append a new object with given command and unique_id (minimal stub).
        Notes:
          - Command/block boundaries terminate at '..' only when that token occurs
            OUTSIDE quotes and OUTSIDE any open parentheses. Parentheses may span lines.
          - Comments begin with '$' and run to end-of-line; ignored for parsing.
        """
        with open(inp_file_path, "r", encoding="cp1252", errors="replace") as f:
            lines = f.readlines()

        # --- helpers (inner closures use 'lines') ---------------------------------
        def _scan_until_terminator(start_idx: int) -> int:
            """
            From start_idx (inclusive), scan forward and return the index (inclusive)
            of the line that contains the block-terminating '..' token. The token
            must be found outside of quotes and parentheses. Handles multi-line
            parentheses; ignores anything after '$' on a line.
            """

            def _strip_comment(line: str) -> str:
                in_quote = False
                for idx, ch in enumerate(line):
                    if ch == '"':
                        in_quote = not in_quote
                    elif ch == "$" and not in_quote:
                        return line[:idx]
                return line

            def _has_standalone_terminator(line: str) -> bool:
                # Accept a standalone ".." line even if parens look unbalanced.
                cleaned = _strip_comment(line)
                return re.match(r"^\s*\.\.\s*$", cleaned) is not None

            paren = 0
            in_quote = False
            for i in range(start_idx, len(lines)):
                s = lines[i]
                if _has_standalone_terminator(s):
                    return i
                j = 0
                while j < len(s):
                    ch = s[j]

                    # line comment (ignored unless we're inside quotes)
                    if ch == "$" and not in_quote:
                        break  # ignore remainder of this line

                    # toggle quote state
                    if ch == '"':
                        in_quote = not in_quote
                        j += 1
                        continue

                    # track parentheses even across lines (unless inside quotes)
                    if not in_quote:
                        if ch == "(":
                            paren += 1
                        elif ch == ")":
                            paren = max(0, paren - 1)

                        # detect '..' only when not in parens and not in quotes
                        if (
                            ch == "."
                            and j + 1 < len(s)
                            and s[j + 1] == "."
                            and paren == 0
                        ):
                            return i  # block ends on this line

                    j += 1
            # If we get here, no terminator was found; treat the last line as end.
            return len(lines) - 1

        def _find_block_by_uid(uid: str) -> tuple[int, int] | None:
            """
            Return (start_idx, end_idx) of the block whose opening line begins with
            '"<uid>" = <COMMAND>'. If not found, return None.
            """
            pattern = re.compile(rf'^\s*"{re.escape(uid)}"\s*=\s*([A-Z0-9\-]+)\b')
            i = 0
            while i < len(lines):
                if pattern.search(lines[i]):
                    end_i = _scan_until_terminator(i)
                    return i, end_i
                i += 1
            return None

        def _find_block(start_index):
            end = _scan_until_terminator(start_index)
            return start_index, end

        def _locate_child_insertion_point(parent_uid: str, child_command: str) -> int:
            loc = _find_block_by_uid(parent_uid)
            if not loc:
                raise ValueError(f'Parent "{parent_uid}" not found.')

            p_start, p_end = loc
            children = BDL_HIERARCHY.get(_command_of_block(lines[p_start]), [])
            if child_command not in children:
                raise ValueError(
                    f"{child_command} cannot be child of {_command_of_block(lines[p_start])}."
                )

            # scan for last child block inside parent block
            i = p_start + 1
            last_child_end = p_start

            while i <= p_end:
                m = re.match(r'^\s*"(.+?)"\s*=\s*([A-Z0-9\-]+)', lines[i])
                if m:
                    this_cmd = m.group(2)
                    if this_cmd == child_command:
                        _, c_end = _find_block(i)
                        last_child_end = c_end
                        i = c_end + 1
                        continue
                i += 1

            return last_child_end + 1  # insertion just after last child

        def _command_of_block(line: str) -> str:
            m = re.match(r'^\s*".+?"\s*=\s*([A-Z0-9\-]+)', line)
            return m.group(1) if m else None

        def _locate_last_block_of_type(command):
            """
            Returns index just AFTER the last block of a given command type.
            If none found, returns index before 'END ..'.
            """
            pattern = re.compile(r'^"(.+?)"\s*=\s*' + re.escape(command) + r"\b")

            last_block_end = None

            idx = 0
            while idx < len(lines):
                if pattern.search(lines[idx]):
                    start, end = _find_block(idx)
                    last_block_end = end
                    idx = end + 1
                else:
                    idx += 1

            if last_block_end is not None:
                return last_block_end + 1

            # fallback → insert before END ..
            for i, line in enumerate(lines):
                if line.strip().startswith("END .."):
                    return i

            # else end of file
            return len(lines)

        def insert_or_replace_keyword(
            block_start: int, block_end: int, keyword: str, value: str
        ):
            """
            Replace VALUE while preserving:
              - original indent
              - original spacing around '='
              - whether '..' occurred inline on the same line
            """

            def has_inline_terminator(s: str) -> bool:
                # detect ".." outside quotes / parentheses
                in_quote = False
                paren = 0
                for j, c in enumerate(s):
                    if c == '"':
                        in_quote = not in_quote
                    elif not in_quote:
                        if c == "(":
                            paren += 1
                        elif c == ")":
                            paren = max(paren - 1, 0)
                        elif (
                            c == "."
                            and j + 1 < len(s)
                            and s[j + 1] == "."
                            and paren == 0
                        ):
                            return True
                return False

            last_match = None
            for i in range(block_start + 1, block_end + 1):
                line = lines[i].rstrip("\n")

                # must start with the keyword (allow indent)
                if not re.match(rf"^\s*{re.escape(keyword)}\b", line):
                    continue

                # find the '=' outside quotes
                in_quote = False
                eq_index = None
                for idx, ch in enumerate(line):
                    if ch == '"':
                        in_quote = not in_quote
                    elif ch == "=" and not in_quote:
                        eq_index = idx
                        break
                if eq_index is None:
                    continue

                remainder = line[eq_index + 1 :]
                had_term = has_inline_terminator(remainder)
                last_match = (i, line, eq_index, had_term)

            if last_match:
                i, line, eq_index, had_term = last_match
                prefix = line[: eq_index + 1]  # text up through '='

                # Build replacement line; we insert exactly one space after '='
                new_line = f"{prefix} {value}"
                if had_term:
                    new_line += "   .."  # DOE-2 standard formatting
                new_line += "\n"

                lines[i] = new_line
                return

            # No existing keyword → insert before block terminator
            insert_at = block_end
            lines.insert(insert_at, f"   {keyword:<18} = {value}\n")

        def delete_keyword(block_start: int, block_end: int, keyword: str):
            """
            Remove the keyword line; if the value is multi-line (parentheses not closed),
            remove subsequent lines until the closing ')', respecting quotes/comments.
            """
            kw_re = re.compile(rf"^\s*{re.escape(keyword)}\s*=\s*(.*)$")
            search_start = block_start + 1
            search_end = block_end

            while True:
                kw_start_idx = None
                for i in range(search_start, search_end + 1):
                    m = kw_re.match(lines[i])
                    if m:
                        kw_start_idx = i
                        break
                if kw_start_idx is None:
                    return  # already default / not present

                # Determine if the RHS on the first line closes all parentheses.
                # Start counting from the '=' onward of that line; then continue to next lines.
                rhs = kw_re.match(lines[kw_start_idx]).group(1)
                paren = 0
                in_quote = False

                def _eat_line_segment(seg: str):
                    nonlocal paren, in_quote
                    j = 0
                    while j < len(seg):
                        ch = seg[j]
                        if ch == "$" and not in_quote:
                            break
                        if ch == '"':
                            in_quote = not in_quote
                        elif not in_quote:
                            if ch == "(":
                                paren += 1
                            elif ch == ")":
                                paren = max(0, paren - 1)
                        j += 1

                _eat_line_segment(rhs)
                end_del = kw_start_idx
                if paren > 0:
                    # keep consuming lines until all parentheses close
                    for i in range(kw_start_idx + 1, search_end + 1):
                        _eat_line_segment(lines[i])
                        end_del = i
                        if paren == 0:
                            break

                # Delete the span
                del lines[kw_start_idx : end_del + 1]
                removed = (end_del - kw_start_idx) + 1
                search_end -= removed

        def _delete_command(block_start: int, block_end: int):
            del lines[block_start : block_end + 1]

        # --- apply edits -----------------------------------------------------------
        results = {"applied": 0, "errors": []}

        for ed in edits:
            ctype = ed["change_type"]
            uid = ed["unique_id"]

            try:
                if ctype == "delete":
                    loc = _find_block_by_uid(uid)
                    if not loc:
                        raise ValueError(f'Object "{uid}" not found for delete.')
                    _delete_command(*loc)
                    results["applied"] += 1

                elif ctype == "restore_default":
                    keyword = ed.get("keyword")
                    if not keyword:
                        raise ValueError("restore_default requires 'keyword'.")
                    loc = _find_block_by_uid(uid)
                    if not loc:
                        raise ValueError(
                            f'Object "{uid}" not found for restore_default.'
                        )
                    start, end = loc
                    delete_keyword(start, end, keyword)
                    # Re-locate the block because size may have changed
                    loc = _find_block_by_uid(uid)
                    results["applied"] += 1

                elif ctype == "modify":
                    keyword = ed.get("keyword")
                    value = ed.get("value")
                    if not keyword or value is None:
                        raise ValueError("modify requires 'keyword' and 'value'.")
                    loc = _find_block_by_uid(uid)
                    if not loc:
                        raise ValueError(f'Object "{uid}" not found for modify.')
                    insert_or_replace_keyword(*loc, keyword=keyword, value=value)
                    results["applied"] += 1

                elif ctype == "add":
                    command_text = ed["command"].rstrip()
                    m = re.match(r'^\s*"([^"]+)"\s*=\s*([A-Z0-9\-]+)', command_text)
                    if not m:
                        raise ValueError(
                            f"Cannot determine command type:\n{command_text}"
                        )
                    command_type = m.group(2)
                    parent_uid = ed.get("parent_uid")
                    if parent_uid:
                        insert_index = _locate_child_insertion_point(
                            parent_uid, command_type
                        )
                    else:
                        insert_index = _locate_last_block_of_type(command_type)
                    # Normalize lines but DO NOT add a second terminator if one already exists
                    raw_lines = [
                        line.rstrip("\n") for line in command_text.splitlines()
                    ]
                    # Check if *any* line already ends the block (inline terminator)
                    block_has_terminator = False
                    for ln in raw_lines:
                        if ".." in ln and not re.search(r'".*\.\..*"', ln):
                            block_has_terminator = True
                            break

                    new_block_lines = [(ln.rstrip() + "\n") for ln in raw_lines]
                    # Only append separate terminator if not already inline
                    if not block_has_terminator:
                        new_block_lines.append("   ..\n")
                    # Insert
                    lines[insert_index:insert_index] = new_block_lines

                elif ctype == "delete_with_children":
                    # Recursively delete this block and all nested child blocks
                    loc = _find_block_by_uid(uid)
                    if not loc:
                        raise ValueError(
                            f'Object "{uid}" not found for delete_with_children.'
                        )

                    start, end = loc

                    # Helper: recursively gather children using same logic as _find_children_of()
                    def _gather_children(uid):
                        block = _find_block_by_uid(uid)
                        if not block:
                            return []

                        b_start, b_end = block
                        parent_cmd = _command_of_block(lines[b_start])
                        allowed_children = set(BDL_HIERARCHY.get(parent_cmd, []))

                        found = []
                        i = b_start + 1
                        while i <= b_end:
                            m = re.match(r'^\s*"(.+?)"\s*=\s*([A-Z0-9\-]+)\b', lines[i])
                            if m:
                                child_uid = m.group(1)
                                child_cmd = m.group(2)
                                if child_cmd in allowed_children:
                                    found.append(child_uid)
                                    _, child_end = _find_block(i)
                                    i = child_end + 1
                                    continue
                            i += 1

                        # recursively include grandchildren
                        all_children = found[:]
                        for c in found:
                            all_children.extend(_gather_children(c))
                        return all_children

                    # get all descendants
                    all_descendants = _gather_children(uid)

                    # delete from bottom-up to keep indexes stable
                    for child_uid in sorted(all_descendants, reverse=True):
                        child_loc = _find_block_by_uid(child_uid)
                        if child_loc:
                            _delete_command(*child_loc)

                    # finally delete the parent itself
                    loc = _find_block_by_uid(uid)
                    if loc:
                        _delete_command(*loc)

                    results["applied"] += 1

                elif ctype == "delete_and_rehome":
                    # delete uid but move children to new_parent_uid
                    new_parent_uid = ed.get("parent_uid")
                    if not new_parent_uid:
                        raise ValueError("delete_and_rehome requires 'parent_uid'.")

                    loc = _find_block_by_uid(uid)
                    if not loc:
                        raise ValueError(
                            f'Object "{uid}" not found for delete_and_rehome.'
                        )

                    start, end = loc
                    parent_cmd = _command_of_block(lines[start])
                    allowed_children = set(BDL_HIERARCHY.get(parent_cmd, []))

                    # 1. Find children using local scanning logic
                    child_uids = []
                    i = start + 1
                    while i <= end:
                        m = re.match(r'^\s*"(.+?)"\s*=\s*([A-Z0-9\-]+)\b', lines[i])
                        if m:
                            child_uid = m.group(1)
                            child_cmd = m.group(2)
                            if child_cmd in allowed_children:
                                child_uids.append(child_uid)
                                _, cend = _find_block(i)
                                i = cend + 1
                                continue
                        i += 1

                    # 2. Rehome each child by modifying its PARENT keyword
                    for child_uid in child_uids:
                        child_loc = _find_block_by_uid(child_uid)
                        if not child_loc:
                            continue
                        # insert/replace keyword
                        insert_or_replace_keyword(
                            *child_loc, keyword="PARENT", value=f'"{new_parent_uid}"'
                        )

                    # 3. Delete the object being removed
                    loc = _find_block_by_uid(uid)
                    if loc:
                        _delete_command(*loc)

                    results["applied"] += 1

                else:
                    raise ValueError(f"Unknown change_type '{ctype}'.")

            except Exception as e:
                results["errors"].append(str(e))

        # write back
        with open(inp_file_path, "w", encoding="cp1252") as f:
            f.writelines(lines)

        return results
