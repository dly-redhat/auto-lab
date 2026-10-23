"""Run with unittest in the explicitly selected supported EE through Navigator."""
import copy
import importlib.util
from pathlib import Path
import unittest

from ansible.errors import AnsibleFilterError

path = Path(__file__).resolve().parents[1] / 'roles/compliance_exceptions/filter_plugins/exception_policy.py'
spec = importlib.util.spec_from_file_location('exception_policy', path)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ExceptionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.data = {'date': '2026-10-23', 'host': 'server1', 'groups': ['database_servers'],
                     'profile': 'linux_demo', 'group': [], 'host_records': [], 'control': []}
        self.record = {'id': 'EXC-001', 'control': 'snmp_service', 'profile': 'linux_demo',
                       'group': 'database_servers', 'status': 'approved', 'kind': 'alternate',
                       'reason': 'Approved database policy', 'approved_by': 'reviewer',
                       'ticket': 'CHG-001', 'expires': '2026-12-31', 'value': {'enabled': False}}

    def resolved(self, control='snmp_service'):
        return policy.resolve_policy(self.data)[control]

    def test_baseline_pass_and_drift(self):
        self.assertEqual(policy.disposition(self.resolved(), True, True), 'pass')
        self.assertEqual(policy.disposition(self.resolved(), False, False), 'drift')

    def test_group_alternate_is_enforced_not_blanket_skipped(self):
        self.data['group'] = [self.record]
        result = self.resolved()
        self.assertEqual(result['value'], {'enabled': False})
        self.assertEqual(policy.disposition(result, False, True), 'approved_deviation')
        self.assertEqual(policy.disposition(result, False, False), 'drift')

    def test_host_overrides_group_and_retains_provenance(self):
        self.data['group'] = [self.record]
        self.data['host_records'] = [dict(self.record, id='EXC-002', host='server1', value={'enabled': True})]
        result = self.resolved()
        self.assertEqual(result['scope'], 'host')
        self.assertEqual(result['value'], {'enabled': True})
        self.assertEqual(result['superseded_ids'], ['EXC-001'])

    def test_control_waiver_never_becomes_a_pass(self):
        self.data['control'] = [dict(self.record, host='server1', kind='waiver', value={})]
        for matches in (True, False):
            self.assertEqual(policy.disposition(self.resolved(), matches, matches), 'approved_waiver')

    def test_expired_high_priority_record_blocks_fallback(self):
        self.data['group'] = [self.record]
        self.data['control'] = [dict(self.record, id='EXC-002', host='server1', expires='2000-01-01')]
        result = self.resolved()
        self.assertTrue(result['review_required'])
        self.assertEqual(result['value'], {})
        self.assertEqual(policy.disposition(result, True, True), 'exception_review_required')

    def test_expiry_includes_whole_utc_date(self):
        self.data['group'] = [dict(self.record, expires=self.data['date'])]
        self.assertTrue(self.resolved()['active'])

    def test_revoked_and_pending_are_not_active(self):
        for status in ('revoked', 'pending'):
            self.data['group'] = [dict(self.record, status=status)]
            self.assertTrue(self.resolved()['review_required'])

    def test_unknown_and_not_applicable_are_distinct(self):
        self.assertEqual(policy.disposition(self.resolved(), False, False, evidence=False), 'unknown')
        self.assertEqual(policy.disposition(self.resolved(), False, False, applicable=False), 'not_applicable')

    def test_scope_date_metadata_control_and_boolean_validation(self):
        for change in ({'group': 'wrong'}, {'profile': 'wrong'}, {'expires': '2026-02-30'},
                       {'expires': '2026-1-1'}, {'ticket': ''}, {'control': 'CIS-1.1'},
                       {'value': {'enabled': 'false'}}, {'kind': 'waiver', 'value': {'enabled': False}}):
            with self.subTest(change=change):
                self.data['group'] = [dict(self.record, **change)]
                with self.assertRaises(AnsibleFilterError):
                    self.resolved()

    def test_duplicate_ids_and_same_priority_ambiguity_are_rejected(self):
        for second in (copy.deepcopy(self.record), dict(self.record, id='EXC-OTHER')):
            self.data['group'] = [self.record, second]
            with self.assertRaises(AnsibleFilterError):
                self.resolved()

    def test_host_scope_mismatch_is_rejected(self):
        self.data['host_records'] = [dict(self.record, host='wrong')]
        with self.assertRaises(AnsibleFilterError):
            self.resolved()

    def test_community_is_a_reference_not_a_secret(self):
        self.data['host_records'] = [dict(self.record, host='server1', control='snmp_community',
                                          value={'community_ref': 'special'})]
        self.assertEqual(self.resolved('snmp_community')['value'], {'community_ref': 'special'})
        self.data['host_records'][0]['value'] = {'community': 'not-allowed'}
        with self.assertRaises(AnsibleFilterError):
            self.resolved()


if __name__ == '__main__':
    unittest.main()
