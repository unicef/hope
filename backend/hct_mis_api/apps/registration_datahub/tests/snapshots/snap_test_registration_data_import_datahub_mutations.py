# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload_0_with_permission 1'] = {
    'data': {
        'uploadImportDataXlsxFile': {
            'errors': [
            ],
            'importData': {
                'numberOfHouseholds': 3,
                'numberOfIndividuals': 6
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload_1_without_permission 1'] = {
    'data': {
        'uploadImportDataXlsxFile': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'uploadImportDataXlsxFile'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create_0_with_permission 1'] = {
    'data': {
        'registrationXlsxImport': {
            'registrationDataImport': {
                'name': 'New Import of Data 123',
                'numberOfHouseholds': 3,
                'numberOfIndividuals': 6,
                'status': 'IMPORTING'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create_1_without_permission 1'] = {
    'data': {
        'registrationXlsxImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'registrationXlsxImport'
            ]
        }
    ]
}
