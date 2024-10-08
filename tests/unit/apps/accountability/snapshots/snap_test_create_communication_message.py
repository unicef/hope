# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCreateCommunicationMessage::test_create_accountability_communication_message_by_households_0_FULL_LIST 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'Test body',
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Wick'
                },
                'fullListArguments': '{"excluded_admin_areas": []}',
                'households': {
                    'totalCount': 14
                },
                'randomSamplingArguments': '{"excluded_admin_areas": []}',
                'registrationDataImport': None,
                'sampleSize': 14,
                'targetPopulation': None,
                'title': 'Test message'
            }
        }
    }
}

snapshots['TestCreateCommunicationMessage::test_create_accountability_communication_message_by_households_1_RANDOM 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'Test body',
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Wick'
                },
                'fullListArguments': None,
                'households': {
                    'totalCount': 1
                },
                'randomSamplingArguments': None,
                'registrationDataImport': None,
                'sampleSize': 1,
                'targetPopulation': None,
                'title': 'Test message'
            }
        }
    }
}

snapshots['TestCreateCommunicationMessage::test_create_accountability_communication_message_by_target_population_0_FULL_LIST 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'Test body',
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Wick'
                },
                'fullListArguments': '{"excluded_admin_areas": []}',
                'households': {
                    'totalCount': 14
                },
                'randomSamplingArguments': '{"excluded_admin_areas": []}',
                'registrationDataImport': None,
                'sampleSize': 14,
                'targetPopulation': {
                    'totalFamilySize': None
                },
                'title': 'Test message'
            }
        }
    }
}

snapshots['TestCreateCommunicationMessage::test_create_accountability_communication_message_by_target_population_1_RANDOM 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'Test body',
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Wick'
                },
                'fullListArguments': None,
                'households': {
                    'totalCount': 1
                },
                'randomSamplingArguments': None,
                'registrationDataImport': None,
                'sampleSize': 1,
                'targetPopulation': {
                    'totalFamilySize': None
                },
                'title': 'Test message'
            }
        }
    }
}

snapshots['TestCreateCommunicationMessage::test_create_accountability_communication_message_without_permission 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createAccountabilityCommunicationMessage'
            ]
        }
    ]
}
