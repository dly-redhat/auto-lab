"""Resolve reviewed exceptions without turning waivers or missing evidence into passes."""
from datetime import datetime
import re

from ansible.errors import AnsibleFilterError

CONTROLS = ('snmp_service', 'snmp_community', 'console_login_banner')


def require(condition, message):
    if not condition:
        raise AnsibleFilterError(message)


def iso_date(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value),
            'Exception dates must be quoted YYYY-MM-DD strings')
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as error:
        raise AnsibleFilterError('Exception date is not a real calendar date') from error


def resolve_policy(data):
    """Explicit precedence: control record > host record > group record.

    Validate every supplied record and reject ambiguous same-level matches.
    An expired/revoked higher-priority record blocks fallback and enforcement.
    """
    today = iso_date(data['date'])
    candidates = {control: [] for control in CONTROLS}
    ids = set()
    for rank, scope in enumerate(('group', 'host', 'control')):
        records = data.get('host_records' if scope == 'host' else scope, [])
        require(isinstance(records, list), f'{scope} exceptions must be a list')
        for record in records:
            require(isinstance(record, dict), 'Exception records must be mappings')
            required = ('id', 'control', 'profile', 'status', 'kind', 'reason',
                        'approved_by', 'ticket', 'expires')
            require(all(isinstance(record.get(key), str) and record[key].strip()
                        for key in required), 'Exception metadata is incomplete')
            require(record['id'] not in ids, 'Duplicate exception ID')
            ids.add(record['id'])
            require(record['control'] in CONTROLS, 'Unknown demo control ID')
            require(record['profile'] == data['profile'], 'Exception profile mismatch')
            require(record['status'] in ('approved', 'pending', 'revoked'),
                    'Invalid exception approval status')
            require(record['kind'] in ('alternate', 'waiver'), 'Invalid exception kind')
            expiry = iso_date(record['expires'])
            if scope == 'group':
                require(record.get('group') in data['groups'], 'Exception group scope mismatch')
            else:
                require(record.get('host') == data['host'], 'Exception host scope mismatch')
            value = record.get('value', {})
            require(isinstance(value, dict), 'Exception value must be a mapping')
            if record['kind'] == 'waiver':
                require(not value, 'A waiver cannot also supply an alternate value')
            elif record['control'] == 'snmp_service':
                require(set(value) == {'enabled'} and type(value['enabled']) is bool,
                        'SNMP service alternate requires only a boolean enabled value')
            elif record['control'] == 'snmp_community':
                require(set(value) == {'community_ref'} and isinstance(value['community_ref'], str)
                        and re.fullmatch(r'[a-z][a-z0-9_]*', value['community_ref']),
                        'SNMP community alternate requires a credential reference, not a secret')
            else:
                require(set(value) == {'text'} and isinstance(value['text'], str)
                        and value['text'].strip() and value['text'].endswith('\n'),
                        'Banner alternate requires newline-terminated text')
            candidates[record['control']].append((rank, scope, record, expiry))
    resolutions = {}
    for control, matches in candidates.items():
        ranks = [item[0] for item in matches]
        require(len(ranks) == len(set(ranks)), f'Ambiguous exceptions for {control}')
        selected = max(matches, key=lambda item: item[0]) if matches else None
        record = selected[2] if selected else {}
        active = bool(selected and record['status'] == 'approved' and selected[3] >= today)
        resolutions[control] = {
            'exception': record, 'scope': selected[1] if selected else 'baseline',
            'active': active, 'review_required': bool(selected and not active),
            'waived': bool(active and record['kind'] == 'waiver'),
            'value': record.get('value', {}) if active else {},
            'superseded_ids': [item[2]['id'] for item in matches if item is not selected],
        }
    return resolutions


def disposition(resolution, baseline, effective, applicable=True, evidence=True):
    if not evidence:
        return 'unknown'
    if resolution['review_required']:
        return 'exception_review_required'
    if not applicable:
        return 'not_applicable'
    if resolution['waived']:
        return 'approved_waiver'
    if not effective:
        return 'drift'
    if resolution['active'] and not baseline:
        return 'approved_deviation'
    return 'pass'


class FilterModule:
    def filters(self):
        return {'exception_policy_resolve': resolve_policy,
                'exception_policy_disposition': disposition}
