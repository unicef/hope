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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphODM3MTI2NC1mYjczLTRmNzAtODVjMy00NzFkYTI1ZWYwMTI=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphODM3MTI2NC1mYjczLTRmNzAtODVjMy00NzFkYTI1ZWYwMTI=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo4ZTU2MjhmYS1iZTFiLTRjZDItYjg2Ni0zMGI3MzMwY2M3NGM=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo4ZTU2MjhmYS1iZTFiLTRjZDItYjg2Ni0zMGI3MzMwY2M3NGM=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDBmNGFiYS1iN2IxLTQzNWYtYjY3YS01MGRjMmRiZjkwNTU=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDBmNGFiYS1iN2IxLTQzNWYtYjY3YS01MGRjMmRiZjkwNTU=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZToyNDBlOTg3OC0xNTIyLTRhYTMtODVmZC1iNzU2ZjNmZGZjNTc=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZToyNDBlOTg3OC0xNTIyLTRhYTMtODVmZC1iNzU2ZjNmZGZjNTc=']"
        }
    ]
}
