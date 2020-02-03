# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestCreateRegistrationDataImport::test_create_reg_data_import_authenticated 1'] = {
    'data': {
        'createRegistrationDataImport': {
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

snapshots['TestCreateRegistrationDataImport::test_create_reg_data_import_not_authenticated 1'] = {
    'data': {
        'createRegistrationDataImport': None
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
                'createRegistrationDataImport'
            ]
        }
    ]
}
