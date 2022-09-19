# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestActionMessageMutation::test_create_communication_message_0_with_permission_and_full_list_tp 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'FULL_LIST message body',
                'createdBy': {
                    'firstName': 'John'
                },
                'numberOfRecipients': 4,
                'title': 'FULL_LIST message title',
                'unicefId': 'MSG-22-0001'
            }
        }
    }
}

snapshots['TestActionMessageMutation::test_create_communication_message_1_with_permission_and_random_tp 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'RANDOM message body',
                'createdBy': {
                    'firstName': 'John'
                },
                'numberOfRecipients': 3,
                'title': 'RANDOM message title',
                'unicefId': 'MSG-22-0002'
            }
        }
    }
}

snapshots['TestActionMessageMutation::test_create_communication_message_2_with_permission_and_full_list_households 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'FULL_LIST message body',
                'createdBy': {
                    'firstName': 'John'
                },
                'numberOfRecipients': 4,
                'title': 'FULL_LIST message title',
                'unicefId': 'MSG-22-0003'
            }
        }
    }
}

snapshots['TestActionMessageMutation::test_create_communication_message_3_with_permission_and_random_households 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': {
            'message': {
                'body': 'RANDOM message body',
                'createdBy': {
                    'firstName': 'John'
                },
                'numberOfRecipients': 3,
                'title': 'RANDOM message title',
                'unicefId': 'MSG-22-0004'
            }
        }
    }
}

snapshots['TestActionMessageMutation::test_create_communication_message_4_with_permission_and_full_list_rdi 1'] = {
    'errors': [
        {
            'message': 'Object of type UUID is not JSON serializable'
        }
    ]
}

snapshots['TestActionMessageMutation::test_create_communication_message_5_with_permission_and_random_rdi 1'] = {
    'errors': [
        {
            'message': 'Object of type UUID is not JSON serializable'
        }
    ]
}

snapshots['TestActionMessageMutation::test_create_communication_message_6_without_permission_full_list_tp 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createAccountabilityCommunicationMessage'
            ]
        }
    ]
}

snapshots['TestActionMessageMutation::test_create_communication_message_7_without_permission_random_tp 1'] = {
    'data': {
        'createAccountabilityCommunicationMessage': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createAccountabilityCommunicationMessage'
            ]
        }
    ]
}
