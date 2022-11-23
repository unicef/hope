# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDiscardVerificationMutation::test_discard_active_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 38,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0N2UwY2RhZS0yNGI4LTQ5ZmQtOGNiZS1hNTM4YzU5NmZjODk=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0N2UwY2RhZS0yNGI4LTQ5ZmQtOGNiZS1hNTM4YzU5NmZjODk=']"
        }
    ]
}

snapshots['TestDiscardVerificationMutation::test_discard_active_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 38,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0N2UwY2RhZS0yNGI4LTQ5ZmQtOGNiZS1hNTM4YzU5NmZjODk=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0N2UwY2RhZS0yNGI4LTQ5ZmQtOGNiZS1hNTM4YzU5NmZjODk=']"
        }
    ]
}
