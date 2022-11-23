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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTplYTU5YzI4NC1kYzBiLTRhNDctYjY3Ni0zZDc2ZTJjZDZkNDI=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTplYTU5YzI4NC1kYzBiLTRhNDctYjY3Ni0zZDc2ZTJjZDZkNDI=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo3ODM0N2E5Yi1mOWQyLTQyZjUtODI2Ni0zNTA4ZTgzZmFiMDM=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo3ODM0N2E5Yi1mOWQyLTQyZjUtODI2Ni0zNTA4ZTgzZmFiMDM=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0ZmVhNGYzYy00NTgxLTRiZjgtYjNhZS1jOTY0Mjg0Y2Q2ZmY=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0ZmVhNGYzYy00NTgxLTRiZjgtYjNhZS1jOTY0Mjg0Y2Q2ZmY=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDEyNmJlYy05ZTM3LTQwMmUtOWQzYS04NzBhNmRlNDAwMzM=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDEyNmJlYy05ZTM3LTQwMmUtOWQzYS04NzBhNmRlNDAwMzM=']"
        }
    ]
}
