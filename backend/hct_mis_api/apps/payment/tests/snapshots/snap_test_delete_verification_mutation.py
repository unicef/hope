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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTowYWRjZTQ5MC1hNmQ4LTRlZDQtOTAyMy1lNDQwMGJlYjE5MzI=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTowYWRjZTQ5MC1hNmQ4LTRlZDQtOTAyMy1lNDQwMGJlYjE5MzI=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDVhNjI1MS1mYWFkLTQ1YTktYTI4MC1iNGNmNjE3MDFhNjI=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTphNDVhNjI1MS1mYWFkLTQ1YTktYTI4MC1iNGNmNjE3MDFhNjI=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0YzcwZTYzZC1kZmI4LTQyZmItOTcxOS00YzRkZmFiNmUxZWE=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo0YzcwZTYzZC1kZmI4LTQyZmItOTcxOS00YzRkZmFiNmUxZWE=']"
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
            'message': "Variable '$cashPlanVerificationId' got invalid value ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo3M2M1ZjIxMy1kNTAyLTRhMjctYTY4Mi03ZWQ3ODNkNTkxN2I=']; ID cannot represent value: ['Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTo3M2M1ZjIxMy1kNTAyLTRhMjctYTY4Mi03ZWQ3ODNkNTkxN2I=']"
        }
    ]
}
