"""R39 quoted attribute and host-project proposal boundary regressions."""
import tempfile
import unittest
from pathlib import Path
from tools.fdf_workspace_probe import _attribute_present, scan
from tools.fdf_proposal_compiler import compile_plan


class R39AttributeBoundary(unittest.TestCase):
    def root(self, markup):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / 'page.tsx').write_text(markup, encoding='utf-8')
        return root

    def candidate_rules(self, markup):
        root = self.root(markup)
        before = (root / 'page.tsx').read_bytes()
        receipt = scan(root)
        plan = compile_plan(root, receipt)
        self.assertEqual((root / 'page.tsx').read_bytes(), before)
        self.assertTrue(receipt['coverage']['complete'])
        self.assertEqual(plan['coverage_admission'], 'PASS_SCOPED')
        self.assertEqual(plan['mode'], 'PROPOSE_ONLY')
        self.assertFalse(plan['mutations_performed'])
        self.assertTrue(plan['owner_approval_required'])
        return [x['rule'] for x in receipt['candidate_changes']]

    def test_alt_spoof_inside_quoted_data_value(self):
        self.assertEqual(self.candidate_rules('<img src="pic" data-note="alt=decorative">'), ['img_missing_alt'])

    def test_alt_spoof_inside_single_quoted_data_value(self):
        self.assertEqual(self.candidate_rules("<img src='pic' data-note='alt=decorative'>"), ['img_missing_alt'])

    def test_aria_spoof_inside_quoted_data_value(self):
        self.assertEqual(self.candidate_rules('<button data-note="aria-label=x"><svg></svg></button>'), ['icon_button_name'])

    def test_aria_labelledby_spoof_inside_quoted_value(self):
        self.assertEqual(self.candidate_rules("<button data-note='aria-labelledby=menu'><svg></svg></button>"), ['icon_button_name'])

    def test_alt_spoof_in_jsx_expression_literal(self):
        self.assertEqual(self.candidate_rules('<img data-note={"alt=decorative"} src="pic"/>'), ['img_missing_alt'])

    def test_aria_spoof_in_nested_jsx_expression(self):
        markup = '<button data-note={{text: "aria-label=x"}}><svg></svg></button>'
        self.assertEqual(self.candidate_rules(markup), ['icon_button_name'])

    def test_actual_alt_and_aria_are_found(self):
        self.assertEqual(self.candidate_rules('<img data-note="alt=bad" alt="Actual" src="pic">'), [])
        self.assertEqual(self.candidate_rules('<button data-note="aria-label=bad" aria-label="Menu"><svg></svg></button>'), [])

    def test_actual_attributes_after_embedded_quote_and_equals(self):
        self.assertEqual(self.candidate_rules("""<img data-note='alt=bad and "quoted"' alt={'real'}>"""), [])
        self.assertEqual(self.candidate_rules('<img data-note="src=foo alt=bad" alt = "">'), [])

    def test_hyphen_colon_and_data_keys_do_not_count(self):
        self.assertEqual(self.candidate_rules('<img data-alt="bad" aria-alt="bad" :alt="bound">'), ['img_missing_alt'])

    def test_invalid_unclosed_values_are_not_authoritative(self):
        self.assertFalse(_attribute_present('<img data-note="alt=spoof', 'alt'))
        self.assertFalse(_attribute_present('<img data-note={"alt=spoof"', 'alt'))

    def test_later_closing_markup_is_not_an_attribute(self):
        self.assertFalse(_attribute_present('<button data-note="x"><span alt="x"></span></button>', 'alt'))


if __name__ == '__main__':
    unittest.main()
