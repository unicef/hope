# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestUpdateRegistrationDataImport::test_update_reg_data_import_authenticated 1'] = {
    'data': {
        'updateRegistrationDataImport': {
            'registrationDataImport': {
                'dataSource': 'XLS',
                'importDate': '2019-12-20T15:00:00',
                'name': 'Test name',
                'numberOfHouseholds': 67,
                'numberOfIndividuals': 300,
                'status': 'DONE'
            }
        }
    }
}

snapshots['TestUpdateRegistrationDataImport::test_update_reg_data_import_not_authenticated 1'] = {
    'data': {
        'updateRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'updateRegistrationDataImport'
            ]
        }
    ]
}
