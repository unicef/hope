# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GrievanceDocumentsUploadTestCase::test_user_can_send_one_document 1'] = {
    'data': {
        'createGrievanceDocumentsMutation': {
            'success': True
        }
    }
}

snapshots['GrievanceDocumentsUploadTestCase::test_user_can_send_one_document_other 1'] = {
    'data': {
        'createGrievanceTicket': {
            'grievanceTickets': [
                {
                    'admin': 'City Test',
                    'category': 5,
                    'consent': True,
                    'description': 'Test Feedback',
                    'language': 'Polish, English',
                    'negativeFeedbackTicketDetails': {
                        'household': None,
                        'individual': None
                    }
                }
            ]
        }
    }
}
