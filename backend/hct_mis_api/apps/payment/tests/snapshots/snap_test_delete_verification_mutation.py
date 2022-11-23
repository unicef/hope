# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeleteVerificationMutation::test_delete_active_verification_plan_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 37,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0ZjM2ODY4OC1lZDdlLTRjYjAtYmRhZC1lMmYxYmUzNjY2N2U=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0ZjM2ODY4OC1lZDdlLTRjYjAtYmRhZC1lMmYxYmUzNjY2N2U=']"
        }
    ]
}

snapshots['TestDeleteVerificationMutation::test_delete_active_verification_plan_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 37,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZToyYzU1NGNhNS00MGE3LTQ1NTUtYWJiMy00Y2I2OTI0ZDQ1MmM=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZToyYzU1NGNhNS00MGE3LTQ1NTUtYWJiMy00Y2I2OTI0ZDQ1MmM=']"
        }
    ]
}

snapshots['TestDeleteVerificationMutation::test_delete_pending_verification_plan_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 37,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo4YTdkNWFlZS1lOWZmLTQ4MjAtYjllNi0yZjk4YzhjZGZkNGU=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo4YTdkNWFlZS1lOWZmLTQ4MjAtYjllNi0yZjk4YzhjZGZkNGU=']"
        }
    ]
}

snapshots['TestDeleteVerificationMutation::test_delete_pending_verification_plan_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 37,
                    'line': 2
                }
            ],
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTplMzlmMWJjYi1kMTgyLTQzNjktYWI5MC1kYTY1NzA1YWFkNTY=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTplMzlmMWJjYi1kMTgyLTQzNjktYWI5MC1kYTY1NzA1YWFkNTY=']"
        }
    ]
}
