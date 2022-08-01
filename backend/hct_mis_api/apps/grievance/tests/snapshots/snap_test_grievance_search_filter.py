# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQuerySearchFilter::test_grievance_list_filtered_by_household_head_family_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        'description': 'ticket_3'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['TestGrievanceQuerySearchFilter::test_grievance_list_filtered_by_ticket_household_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        'description': 'ticket_2'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['TestGrievanceQuerySearchFilter::test_grievance_list_filtered_by_ticket_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        'description': 'ticket_1'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
