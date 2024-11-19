# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestFeedbackMessages::test_create_feedback_message_0_with_permission 1'] = {
    'data': {
        'createFeedbackMessage': {
            'feedbackMessage': {
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Doe'
                },
                'description': 'You should see this message in snapshot'
            }
        }
    }
}

snapshots['TestFeedbackMessages::test_create_feedback_message_1_without_permission 1'] = {
    'data': {
        'createFeedbackMessage': None
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
                'createFeedbackMessage'
            ]
        }
    ]
}

snapshots['TestFeedbackMessages::test_feedback_query_shows_feedback_messages_0_with_permission 1'] = {
    'data': {
        'feedback': {
            'feedbackMessages': {
                'edges': [
                    {
                        'node': {
                            'description': 'Feedback message you see',
                            'id': 'RmVlZGJhY2tNZXNzYWdlTm9kZTpjODZkOGE1OC1jNGI4LTQwNjYtOTgyMS05OGUyMzZiMTc3NDI='
                        }
                    }
                ]
            },
            'id': 'RmVlZGJhY2tOb2RlOjE3NjFkMDIwLWVhZDItNDg5Zi05NWE4LTYxODUzZmJlNTY4ZQ==',
            'issueType': 'NEGATIVE_FEEDBACK'
        }
    }
}

snapshots['TestFeedbackMessages::test_feedback_query_shows_feedback_messages_1_without_permission 1'] = {
    'data': {
        'feedback': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'feedback'
            ]
        }
    ]
}
