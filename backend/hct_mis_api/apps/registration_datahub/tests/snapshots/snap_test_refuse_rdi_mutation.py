# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestRefuseRdiMutation::test_refuse_registration_data_import_0_with_permission 1'] = {
    'data': {
        'refuseRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'REFUSE'
            }
        }
    }
}

snapshots['TestRefuseRdiMutation::test_refuse_registration_data_import_1_with_permission 1'] = {
    'data': {
        'refuseRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 5
                }
            ],
            'message': 'Only In Review Registration Data Import can be refused',
            'path': [
                'refuseRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRefuseRdiMutation::test_refuse_registration_data_import_2_without_permission 1'] = {
    'data': {
        'refuseRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'refuseRegistrationDataImport'
            ]
        }
    ]
}
