# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_0_with_permission 1'] = {
    'data': {
        'registrationProgramPopulationImport': {
            'registrationDataImport': {
                'dataSource': 'PROGRAM_POPULATION',
                'name': 'New Import of Data 123',
                'screenBeneficiary': False
            }
        }
    }
}

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_1_without_permission 1'] = {
    'data': {
        'registrationProgramPopulationImport': None
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
                'registrationProgramPopulationImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_cannot_check_against_sanction_list_0_can_check_against_sanction_list 1'] = {
    'data': {
        'registrationProgramPopulationImport': {
            'registrationDataImport': {
                'dataSource': 'PROGRAM_POPULATION',
                'name': 'New Import of Data 123',
                'screenBeneficiary': True
            }
        }
    }
}

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_cannot_check_against_sanction_list_1_cannot_check_against_sanction_list 1'] = {
    'data': {
        'registrationProgramPopulationImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': "['Cannot check against sanction list']",
            'path': [
                'registrationProgramPopulationImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_nothing_to_import 1'] = {
    'data': {
        'registrationProgramPopulationImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': "['This action would result in importing 0 households and 0 individuals.']",
            'path': [
                'registrationProgramPopulationImport'
            ]
        }
    ]
}

snapshots['TestRegistrationDataProgramPopulationImportMutations::test_registration_data_import_create_program_finished 1'] = {
    'data': {
        'registrationProgramPopulationImport': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 5
                }
            ],
            'message': "['In order to proceed this action, program status must not be finished']",
            'path': [
                'registrationProgramPopulationImport'
            ]
        }
    ]
}
