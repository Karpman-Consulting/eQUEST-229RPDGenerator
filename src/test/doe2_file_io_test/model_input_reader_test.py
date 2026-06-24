import unittest
import shutil
import re
from pathlib import Path


from rpd_generator.doe2_file_io.model_input_reader import (
    ModelInputReader,
)
from rpd_generator.doe2_file_io.model_input_editor import ModelInputEditor, INPEdits


class TestModelInputReader(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.model_input_reader = ModelInputReader()

        self.test_file = str(
            Path(__file__).parents[2]
            / "test"
            / "full_rpd_test"
            / "E-1"
            / "229 Test Case E-1 (PSZHP).BDL"
        )

    def test_read_doe2_version(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual("DOE-2.3-50h", data["doe2_version"])

    def test_read_zone_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(5, len(data["file_commands"]["ZONE"]))

    def test_read_material_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(10, len(data["file_commands"]["MATERIAL"]))

    def test_read_schedule_commands(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(12, len(data["file_commands"]["SCHEDULE-PD"]))

    def test_read_library_entries(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertDictEqual(
            {
                "command": "CONSTRUCTION",
                "TYPE": "U-VALUE",
                "U-VALUE": "                      2.0800",
                "ABSORPTANCE": "                      0.7000",
                "C-C-U": "                      1.0000",
                "C-RIGID-INS-RVAL": "                      0.0000",
                "C-USER-INP-ABS": "                      0.7000",
                "C-WALL-TYPE": "                      0.0000",
                "ROUGHNESS": "                      3.0000",
            },
            data["file_commands"]["CONSTRUCTION"]["Sgl Lyr Unins Mtl Door"],
        )

    def test_raw_read_library_curve_fit_coef(self):
        data = self.model_input_reader.read_input_bdl_file(self.test_file)
        self.assertEqual(
            ["0", "0.99945700", "0.00054300"],
            data["file_commands"]["CURVE-FIT"]["DW-Gas-Pilotless-HIR-fPLR"]["COEF"],
        )


class TestEditINP(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # Find the BDL fixture and the sibling INP in the same directory
        self.bdl_path = (
            Path(__file__).parents[2]
            / "test"
            / "full_rpd_test"
            / "E-1"
            / "229 Test Case E-1 (PSZHP).BDL"
        )
        self.inp_dir = self.bdl_path.parent

        # Try common INP filename patterns in that directory or just grab the first *.inp
        candidates = list(self.inp_dir.glob("*.INP")) + list(self.inp_dir.glob("*.inp"))
        if not candidates:
            self.fail(f"No INP file found next to {self.bdl_path}")
        self.src_inp = candidates[0]

        # Work on a temp copy
        self.temp_dir = Path(self.inp_dir) / "_tmp_inp_tests"
        self.temp_dir.mkdir(exist_ok=True)
        self.temp_inp = self.temp_dir / f"{self.src_inp.stem}.INP"
        shutil.copyfile(self.src_inp, self.temp_inp)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    # ---------- helpers ----------

    def _read_lines(self) -> list[str]:
        return self.temp_inp.read_text(encoding="utf-8").splitlines(keepends=True)

    def _write_text(self, text: str):
        self.temp_inp.write_text(text, encoding="utf-8")

    def _scan_until_terminator(self, lines: list[str], start_idx: int) -> int:
        """
        Return the index (inclusive) of the line that contains the terminating '..'
        outside quotes/parentheses. Parentheses may span lines; comments ($) ignored.
        """
        paren = 0
        in_quote = False
        for i in range(start_idx, len(lines)):
            s = lines[i]
            j = 0
            while j < len(s):
                ch = s[j]
                if ch == "$" and not in_quote:
                    break  # ignore rest of line
                if ch == '"':
                    in_quote = not in_quote
                    j += 1
                    continue
                if not in_quote:
                    if ch == "(":
                        paren += 1
                    elif ch == ")":
                        paren = max(0, paren - 1)
                    elif (
                        ch == "." and j + 1 < len(s) and s[j + 1] == "." and paren == 0
                    ):
                        return i
                j += 1
        return len(lines) - 1

    def _find_block_by_uid(self, uid: str) -> tuple[int, int] | None:
        """
        Find the block bounds (start_idx, end_idx) for a unique id.
        Header line looks like: "<uid>" = COMMAND
        """
        lines = self._read_lines()
        pat = re.compile(rf'^\s*"{re.escape(uid)}"\s*=\s*([A-Z0-9\-]+)\b')
        for i, line in enumerate(lines):
            if pat.search(line):
                end_i = self._scan_until_terminator(lines, i)
                return i, end_i
        return None

    def _get_block_text(self, uid: str) -> str:
        bounds = self._find_block_by_uid(uid)
        self.assertIsNotNone(bounds, f'Block "{uid}" not found.')
        start, end = bounds
        lines = self._read_lines()
        return "".join(lines[start : end + 1])

    # ---------- tests ----------

    def test_modify_adds_keyword_when_missing(self):
        # Pick a small block that likely lacks a distinctive keyword
        uid = "Perimeter Space 1 (South)"
        edits = [
            INPEdits(
                unique_id=uid,
                change_type="modify",
                keyword="TEST-FLAG",
                value="YES",
                command="",
            )
        ]
        ModelInputEditor.edit_inp_file(str(self.temp_inp), edits)
        block = self._get_block_text(uid)
        self.assertIn("TEST-FLAG", block)
        self.assertIn("= YES", block)

    def test_modify_replaces_existing_keyword_value(self):
        uid = "Baseline System 4 (South)"
        edits = [
            INPEdits(
                unique_id=uid,
                change_type="modify",
                command="SYSTEM",
                keyword="SUPPLY-KW/FLOW",
                value="0.0006",
            )
        ]
        ModelInputEditor.edit_inp_file(str(self.temp_inp), edits)
        block = self._get_block_text(uid)
        # Ensure the new value is present
        self.assertIn("SUPPLY-KW/FLOW", block)
        self.assertIn("0.0006", block)
        # And the old value no longer appears on that keyword line
        self.assertNotIn("SUPPLY-KW/FLOW     = 0.0003", block)

    def test_restore_default_keyword_scoped_to_block(self):
        """
        Previously failing because the assertion looked at the entire file.
        Now we only assert the keyword is removed from the target block.
        """
        uid = "Baseline System 4 (East)"
        edits = [
            INPEdits(
                unique_id=uid,
                change_type="restore_default",
                keyword="COOL-SET-T",
                value="",
                command="",
            )
        ]
        ModelInputEditor.edit_inp_file(str(self.temp_inp), edits)
        block = self._get_block_text(uid)
        # Strict check: 'AREA' keyword line should not be in this block anymore
        self.assertNotRegex(
            block, r"^\s*COOL-SET-T\s*=", msg="COOL-SET-T still present in target block"
        )

        # But AREA may still exist elsewhere; prove we didn't do a global nuke
        full_text = self.temp_inp.read_text(encoding="utf-8")
        self.assertIn("COOL-SET-T", full_text)

    def test_delete_entire_block(self):
        uid = "1 - Custodial Office zn"
        edits = [
            INPEdits(
                unique_id=uid, change_type="delete", keyword="", value="", command=""
            )
        ]
        ModelInputEditor.edit_inp_file(str(self.temp_inp), edits)
        self.assertIsNone(self._find_block_by_uid(uid))

    def test_add_new_block_inserted_before_end(self):
        new_uid = "ZZZ - Test Added Block"
        cmd_text = (
            f'"{new_uid}" = SYSTEM\n'
            "   TYPE             = PSZ\n"
            "   COOLING-EIR      = 0.3333\n"
            "   .."
        )
        edits = [
            INPEdits(
                unique_id=new_uid,
                change_type="add",
                keyword="",
                value="",
                command=cmd_text,
            )
        ]
        ModelInputEditor.edit_inp_file(str(self.temp_inp), edits)
        block = self._get_block_text(new_uid)
        self.assertIn('"ZZZ - Test Added Block" = SYSTEM', block)
        self.assertIn("..", block.splitlines()[-1])

    def test_terminator_inside_quotes_is_ignored(self):
        """
        Ensure '..' inside quotes does not terminate the block. We add a block
        where a value contains '..' in quotes and then modify another keyword in the same block.
        """
        new_uid = "ZZQ - Quotes Terminator Test"
        cmd_text = (
            f'"{new_uid}" = SYSTEM\n'
            "   TYPE             = PSZ\n"
            '   NOTE             = "this string has two dots .. but is quoted"\n'
            "   COOLING-EIR      = 0.20\n"
            "   .."
        )
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="add",
                    keyword="",
                    value="",
                    command=cmd_text,
                )
            ],
        )
        # Now modify COOLING-EIR; if parser mistakenly ended at the NOTE line, it would fail to find the block
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="modify",
                    keyword="COOLING-EIR",
                    value="0.25",
                    command="",
                )
            ],
        )
        block = self._get_block_text(new_uid)
        self.assertIn("NOTE", block)
        self.assertIn(".. but is quoted", block)
        self.assertIn("COOLING-EIR      = 0.25", block)

    def test_terminator_inside_multiline_parentheses_is_ignored(self):
        """
        Add a block with a multi-line parenthetical value that contains '..' on its own line.
        The block must not terminate until the closing ')'.
        """
        new_uid = "ZZP - Paren Terminator Test"
        cmd_text = (
            f'"{new_uid}" = SYSTEM\n'
            "   TYPE             = PSZ\n"
            "   BIG-LIST         = (\n"
            "      1, 2, 3,\n"
            "      ..   $ literal dots in data row; still inside parens\n"
            "      4, 5\n"
            "   )\n"
            "   COOLING-EIR      = 0.10\n"
            "   .."
        )
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="add",
                    keyword="",
                    value="",
                    command=cmd_text,
                )
            ],
        )
        # Now restore_default BIG-LIST to ensure multi-line deletion works and terminator logic was correct
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="restore_default",
                    keyword="BIG-LIST",
                    value="",
                    command="",
                )
            ],
        )
        block = self._get_block_text(new_uid)
        self.assertNotRegex(block, r"^\s*BIG-LIST\s*=", msg="BIG-LIST still present")
        self.assertIn("COOLING-EIR", block)  # ensure rest of block survived

    def test_preserve_line_terminator_when_replacing_value_on_terminator_line(self):
        """
        If a keyword is on the same line as '..', we still want the line to end with '..'
        after replacement.
        """
        # First add a minimal block that places keyword and '..' on the same line
        new_uid = "ZZS - SameLine Terminator Test"
        cmd_text = f'"{new_uid}" = SYSTEM\n' "   TYPE             = PSZ   ..\n"
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="add",
                    keyword="",
                    value="",
                    command=cmd_text,
                )
            ],
        )
        # Now modify TYPE to a different value; the line should still end with '..'
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid,
                    change_type="modify",
                    keyword="TYPE",
                    value="PVVT",
                    command="",
                )
            ],
        )
        # Grab raw lines and check the specific line
        start, end = self._find_block_by_uid(new_uid)
        lines = self._read_lines()
        block_lines = lines[start : end + 1]
        # Find line with TYPE
        type_lines = [ln for ln in block_lines if re.match(r"^\s*TYPE\s*=", ln)]
        print("ACTUAL LINE:", repr(type_lines[0]))
        self.assertTrue(type_lines, "Modified TYPE line not found")
        self.assertTrue(
            type_lines[0].rstrip().endswith(".."),
            "Terminator '..' not preserved on same line",
        )

    def test_add_inserts_in_correct_section_order(self):
        """
        When adding another block of an existing command type, it should be inserted
        after the last block of that type (or before END if none).
        """
        # Use an existing command type from the file; SYSTEM is very common
        new_uid_1 = "ZZX - Insert Order 1"
        new_uid_2 = "ZZX - Insert Order 2"
        cmd1 = f'"{new_uid_1}" = SYSTEM\n   TYPE = PSZ\n   ..'
        cmd2 = f'"{new_uid_2}" = SYSTEM\n   TYPE = PSZ\n   ..'

        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid_1,
                    change_type="add",
                    keyword="",
                    value="",
                    command=cmd1,
                )
            ],
        )
        ModelInputEditor.edit_inp_file(
            str(self.temp_inp),
            [
                INPEdits(
                    unique_id=new_uid_2,
                    change_type="add",
                    keyword="",
                    value="",
                    command=cmd2,
                )
            ],
        )

        # Ensure block 2 appears AFTER block 1 in the file
        text = self.temp_inp.read_text(encoding="utf-8")
        pos1 = text.find(new_uid_1)
        pos2 = text.find(new_uid_2)
        self.assertTrue(
            0 <= pos1 < pos2, "Second added block did not come after the first"
        )


if __name__ == "__main__":
    unittest.main()
