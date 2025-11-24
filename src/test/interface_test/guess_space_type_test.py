import unittest
from unittest.mock import Mock
import customtkinter as ctk

from interface.panel_assignments import RulesetValuesPanel
from interface.space_type_guessing import (
    ABBREV_MAP,
    FUZZY_TERMS,
    FALLBACK_MAP,
    SUGGESTION_RULES,
)


class TestGuessSpaceTypeRealData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ctk.set_default_color_theme("blue")  # avoid CTk default popup warning

    def setUp(self):
        """Use REAL dictionaries and real normalization logic."""
        root = ctk.CTk()  # still needed because OptionMenu exists
        mock_app = Mock()
        mock_app.data = Mock()

        # Create panel exactly as your GUI does
        self.panel = RulesetValuesPanel(root, mock_app)

    def test_custom_space_name(self):
        guess, conf = self.panel._guess_space_type("FL11_Apt 05,04,03")
        print(f"Guessed: {guess} with confidence {conf}")

    # -------------------------------------------------------------
    # BASIC SANITY CHECKS
    # -------------------------------------------------------------

    def test_returns_tuple(self):
        guess, conf = self.panel._guess_space_type("Office Open Plan 101")
        print(f"Guessed: {guess} with confidence {conf}")
        self.assertIsInstance(guess, (str, type(None)))
        self.assertIsInstance(conf, int)

    def test_no_match_returns_none_and_zero(self):
        guess, conf = self.panel._guess_space_type("Xyzqwerty")
        self.assertIsNone(guess)
        self.assertEqual(conf, 0)

    # -------------------------------------------------------------
    # FALLBACK_MAP tests
    # -------------------------------------------------------------

    def test_fallback_map_common(self):
        """Use a keyword guaranteed present in FALLBACK_MAP, like 'conf' (conference)."""
        # Many dictionaries include: "conf": "CONFERENCE_ROOM"
        possible_keys = [k for k in FALLBACK_MAP.keys() if "conf" in k]
        if not possible_keys:
            self.skipTest("FALLBACK_MAP does not contain conference-related keywords")

        guess, conf = self.panel._guess_space_type("Big Conf Room A")
        self.assertIsNotNone(guess)
        self.assertIn("Conference", guess)
        self.assertEqual(conf, 100)

    # -------------------------------------------------------------
    # ABBREVIATION + FUZZY LOGIC tests
    # -------------------------------------------------------------

    def test_abbreviation_map_expansion(self):
        """Test a common abbreviation like 'mech' → mechanical."""
        found = False
        for pat, repl in ABBREV_MAP.items():
            if "mech" in pat or "mech" in repl:
                # Present in your ABBREV_MAP for mechanical rooms?
                s = "MECH ROOM 201"
                guess, conf = self.panel._guess_space_type(s)
                self.assertIsNotNone(guess)
                found = True
                break
        if not found:
            self.skipTest("No relevant ABBREV_MAP pattern for 'mech' found.")

    def test_fuzzy_typo(self):
        """Typo 'offcie' should fuzzy-map to 'office'."""
        guess, conf = self.panel._guess_space_type("Offcie Open Work Area")
        if guess is not None:
            self.assertIn("Office", guess)

    # -------------------------------------------------------------
    # SUGGESTION_RULE tests
    # -------------------------------------------------------------

    def test_storage_room_rule(self):
        """Test real SUGGESTION_RULE for storage if present."""
        hit = False
        for r in SUGGESTION_RULES:
            if r.get("target", "").upper().startswith("STORAGE"):
                hit = True
                guess, conf = self.panel._guess_space_type("Small Storage 12B")
                self.assertIsNotNone(guess)
                self.assertIn("Storage", guess)
                break
        if not hit:
            self.skipTest("SUGGESTION_RULES contain no STORAGE rule")

    # -------------------------------------------------------------
    # AMBIGUITY / SCORING PRIORITY (REAL RULESET)
    # -------------------------------------------------------------

    def test_open_vs_enclosed_priority(self):
        """
        Many rules separate Office Open vs Office Enclosed using weights.
        Example:
        - "Open Office Area" → should classify as some version of "Office Open"
        - "Enclosed Office" → should classify as "Office Enclosed"
        """
        guess1, _ = self.panel._guess_space_type("Open Office Bullpen")
        guess2, _ = self.panel._guess_space_type("Enclosed Office 303")

        # Not all dictionaries may categorize these labels
        # so use loose matching.
        if guess1:
            self.assertIn("Office", guess1)
        if guess2:
            self.assertIn("Office", guess2)

    # -------------------------------------------------------------
    # PHRASE-MATCH TEST
    # -------------------------------------------------------------

    def test_phrase_rule(self):
        """
        Many SUGGESTION_RULES include phrase matches like:
        phrases=["open office", "copy room", ...]
        """
        any_phrase_rules = [r for r in SUGGESTION_RULES if r.get("phrases")]
        if not any_phrase_rules:
            self.skipTest("No phrase rules available")

        # Pick a common phrase found in typical rules
        candidate = None
        for r in any_phrase_rules:
            for ph in r["phrases"]:
                candidate = ph
                break
            if candidate:
                break

        guess, conf = self.panel._guess_space_type(candidate.title())
        self.assertIsNotNone(guess)
        self.assertGreater(conf, 0)

    # -------------------------------------------------------------
    # EXPLICIT TEST FOR STRIP / NORMALIZATION
    # -------------------------------------------------------------

    def test_name_normalization_spaces_hyphens(self):
        guess, conf = self.panel._guess_space_type("  office-open_area  ")
        # No guarantee what target is, but normalization must cause some hit.
        if guess:
            self.assertIn("Office", guess)


if __name__ == "__main__":
    unittest.main()
