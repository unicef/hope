# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_approved 1'] = {
    'data': {
        'candidateHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'CITIZEN',
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_size 1'] = {
    'data': {
        'candidateHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_residence_status 1'] = {
    'data': {
        'candidateHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_first_10 1'] = {
    'data': {
        'candidateHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'REFUGEE',
                        'size': 2
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
