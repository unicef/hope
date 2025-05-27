# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create_0_with_permission 1'] = {
    'data': {
        'registrationXlsxImport': {
            'registrationDataImport': {
                'deduplicationEngineStatus': 'PENDING',
                'name': 'New Import of Data 123',
                'numberOfHouseholds': 3,
                'numberOfIndividuals': 6,
                'status': 'IMPORT_SCHEDULED'
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

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_create_validate_import_data 1'] = {
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
            'message': "['Cannot import file containing validation errors']",
            'path': [
                'registrationXlsxImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload_0_with_permission 1'] = {
    'data': {
        'uploadImportDataXlsxFileAsync': {
            'errors': [
            ],
            'importData': {
                'numberOfHouseholds': None,
                'numberOfIndividuals': None,
                'xlsxValidationErrors': [
                ]
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload_1_with_permission_invalid_file 1'] = {
    'data': {
        'uploadImportDataXlsxFileAsync': {
            'errors': [
            ],
            'importData': {
                'numberOfHouseholds': None,
                'numberOfIndividuals': None,
                'xlsxValidationErrors': [
                ]
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_registration_data_import_datahub_upload_2_without_permission 1'] = {
    'data': {
        'uploadImportDataXlsxFileAsync': None
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
                'uploadImportDataXlsxFileAsync'
            ]
        }
    ]
}

snapshots['TestRegistrationDataImportDatahubMutations::test_save_kobo_project_import_data_async_0_with_permission 1'] = {
    'data': {
        'saveKoboImportDataAsync': {
            'importData': {
                'koboAssetId': '123',
                'koboValidationErrors': [
                ],
                'onlyActiveSubmissions': True,
                'pullPictures': False
            }
        }
    }
}

snapshots['TestRegistrationDataImportDatahubMutations::test_save_kobo_project_import_data_async_1_without_permission 1'] = {
    'data': {
        'saveKoboImportDataAsync': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'saveKoboImportDataAsync'
            ]
        }
    ]
}
