# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceQueryElasticSearch::test_grievance_query_es_search_unicef_id 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': 'City Test',
                        'category': 7,
                        'consent': True,
                        'createdAt': '2022-08-17T16:19:52.506299',
                        'description': 'Just random description',
                        'id': 'R3JpZXZhbmNlVGlja2V0Tm9kZToxZTgyZjA3NS1hYjk4LTRiNzAtYjg3NC1kYmNlNWU1YmE1N2M=',
                        'language': 'Polish',
                        'status': 1
                    }
                }
            ]
        }
    }
}
