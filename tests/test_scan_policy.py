import unittest
from scripts.check_scan import blockers


class ScanPolicyTests(unittest.TestCase):
    def test_fixable_critical_blocks_but_unfixed_remains_report_only(self):
        fixed = {"Severity": "CRITICAL", "FixedVersion": "2.0"}
        unfixed = {"Severity": "CRITICAL", "FixedVersion": ""}
        low = {"Severity": "LOW", "FixedVersion": "2.0"}
        report = {"Results": [{"Vulnerabilities": [fixed, unfixed, low]}]}
        self.assertEqual(blockers(report), [fixed])

    def test_clean_target_can_have_no_vulnerability_list(self):
        self.assertEqual(blockers({"Results": [{"Vulnerabilities": None}]}), [])
