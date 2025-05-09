# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestCrossAreaFilter::test1_cross_area_filter_true_full_area_access_with_permission 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Cross Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestCrossAreaFilter::test1_cross_area_filter_true_full_area_access_without_permission 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Cross Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Same Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
            ]
        }
    }
}

snapshots["TestCrossAreaFilter::test_cross_area_filter_true 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Cross Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                }
            ]
        }
    }
}

snapshots["TestCrossAreaFilter::test_cross_area_filter_true_but_area_restrictions 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Cross Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Same Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
            ]
        }
    }
}

snapshots["TestCrossAreaFilter::test_without_cross_area_filter 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Cross Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
                {
                    "node": {
                        "admin": "Admin Area 2",
                        "category": 8,
                        "consent": True,
                        "description": "Same Area Grievance",
                        "language": "Polish",
                        "status": 1,
                    }
                },
            ]
        }
    }
}
