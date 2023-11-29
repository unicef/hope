# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCrossAreaFilterAvailable::test_cross_area_filter_true 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': None,
                        'category': 8,
                        'consent': True,
                        'description': 'Cross Area Grievance',
                        'language': 'Polish',
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestCrossAreaFilterAvailable::test_without_cross_area_filter 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'admin': None,
                        'category': 8,
                        'consent': True,
                        'description': 'Cross Area Grievance',
                        'language': 'Polish',
                        'status': 1
                    }
                },
                {
                    'node': {
                        'admin': None,
                        'category': 8,
                        'consent': True,
                        'description': 'Same Area Grievance',
                        'language': 'Polish',
                        'status': 1
                    }
                }
            ]
        }
    }
}
