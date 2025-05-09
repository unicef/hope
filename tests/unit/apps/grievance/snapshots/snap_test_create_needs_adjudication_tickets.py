# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestCreateNeedsAdjudicationTicketsBiometrics::test_ticket_biometric_query_response 1"] = {
    "data": {
        "allGrievanceTicket": {
            "edges": [
                {
                    "node": {
                        "category": 8,
                        "issueType": 25,
                        "needsAdjudicationTicketDetails": {
                            "extraData": {
                                "dedupEngineSimilarityPair": {
                                    "individual1": {
                                        "fullName": "test name",
                                    },
                                    "individual2": {
                                        "fullName": "Test2 Name2",
                                    },
                                    "similarityScore": "55.55",
                                },
                                "goldenRecords": [],
                                "possibleDuplicate": [],
                            }
                        },
                        "status": 1,
                    }
                }
            ],
            "totalCount": 1,
        }
    }
}
