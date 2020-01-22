# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeleteRegistrationDataImport::test_delete_reg_data_import_authenticated 1'] = {
    'data': {
        'deleteRegistrationDataImport': {
            'ok': True
        }
    }
}

snapshots['TestDeleteRegistrationDataImport::test_delete_reg_data_import_not_authenticated 1'] = {
    'data': {
        'deleteRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User is not authenticated.',
            'path': [
                'deleteRegistrationDataImport'
            ]
        }
    ]
}
