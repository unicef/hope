# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_approved 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_size 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_residence_status 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 13,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}

snapshots['CandidateListTargetingCriteriaQueryTestCase::test_candidate_households_list_by_targeting_criteria_first_10 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 17,
                    'line': 7
                }
            ],
            'message': 'Cannot query field "familySize" on type "HouseholdNode".'
        }
    ]
}
