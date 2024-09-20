# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTicketNotes::test_ticket_notes_query_all 1'] = {
    'data': {
        'allTicketNotes': {
            'edges': [
                {
                    'node': {
                        'createdBy': {
                            'firstName': 'John',
                            'lastName': 'Doe'
                        },
                        'description': 'This is a test note message'
                    }
                }
            ]
        }
    }
}

snapshots['TestTicketNotes::test_create_ticket_note_0_with_permission 1'] = {
    'data': {
        'createTicketNote': {
            'grievanceTicketNote': {
                'createdBy': {
                    'firstName': 'John',
                    'lastName': 'Doe'
                },
                'description': 'Example note description'
            }
        }
    }
}

snapshots['TestTicketNotes::test_create_ticket_note_1_without_permission 1'] = {
    'data': {
        'createTicketNote': None
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
                'createTicketNote'
            ]
        }
    ]
}
