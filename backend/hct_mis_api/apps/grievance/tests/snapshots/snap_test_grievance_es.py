# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_by_admin 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-18T16:03:30.484038+00:00',
                        'description': 'Just random description',
                        'householdUnicefId': 'HH-20-0000.0001',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZTo2NDczYzRmMi05YTg1LTQxOTItOTg3ZC0wYmYxNzQ1NmY2Mjk=',
                        'issueType': None,
                        'language': 'Polish',
                        'priority': 1,
                        'status': 1,
                        'unicefId': 'GRV-0000136',
                        'urgency': 2
                    }
                }
            ]
        }
    }
}
