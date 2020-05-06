# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload 1'] = {
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

snapshots['TestRegistrationDataImportDatahubMutations::test_approve_registration_data_import 1'] = {
    'data': {
        'approveRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'APPROVED'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_approve_registration_data_import_wrong_initial_status 1'] = {
    'data': {
        'approveRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only In Review Registration Data Import can be Approved',
            'path': [
                'approveRegistrationDataImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': '''Variable "$registrationDataImportData" got invalid value {"businessAreaSlug": "afghanistan", "importDataId": "SW1wb3J0RGF0YU5vZGU6ZTZhMTgzY2EtM2E4NS00ZjE1LWE3NGItODU0MDY3ZDEwZWY2", "name": "New Import of Data 123"}.
In field "businessAreaSlug": Unknown field.'''
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_unapprove_registration_data_import 1'] = {
    'data': {
        'unapproveRegistrationDataImport': {
            'registrationDataImport': {
                'status': 'IN_REVIEW'
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_unapprove_registration_data_import_wrong_initial_status 1'] = {
    'data': {
        'unapproveRegistrationDataImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Only Approved Registration Data Import can be Unapproved',
            'path': [
                'unapproveRegistrationDataImport'
            ]
        }
    ]
}
