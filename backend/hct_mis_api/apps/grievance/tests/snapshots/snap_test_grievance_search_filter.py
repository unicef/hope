# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQuerySearchFilter::test_grievance_list_filtered_by_household_head_family_name 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ],
            'totalCount': 0
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
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTphM2RjNWVhNC1lMmExLTQxYWItYTRiOC1hODM1YTAyMDc1Zjg='
                    }
                },
                {
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
                    'node': {
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo2YTRmOTgzYy1kMzJlLTRkM2UtYWNjMS03MjkwNzRmODFmNDQ='
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['TestGrievanceQuerySearchFilter::test_grievance_list_filtered_by_ticket_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}
