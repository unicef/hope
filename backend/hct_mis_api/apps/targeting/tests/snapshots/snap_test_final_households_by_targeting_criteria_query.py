# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_finalized 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 1,
                        'residenceStatus': 'IDP'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 2,
                        'residenceStatus': 'REFUGEE'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_1_edit 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 1,
                        'residenceStatus': 'CITIZEN'
                    }
                },
                {
                    'node': {
                        'familySize': 1,
                        'residenceStatus': 'IDP'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_size_2_edit 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 2,
                        'residenceStatus': 'REFUGEE'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['FinalListTargetingCriteriaQueryTestCase::test_final_households_list_by_targeting_criteria_residence_status 1'] = {
    'data': {
        'finalHouseholdsListByTargetingCriteria': {
            'edges': [
                {
                    'node': {
                        'familySize': 1,
                        'residenceStatus': 'CITIZEN'
                    }
                }
            ],
            'totalCount': 1
        }
    }
}
