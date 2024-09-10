# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_approved_0_with_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': {
            'edges': [
                {
                    'node': {
                        'residenceStatus': 'HOST',
                        'size': 1
                    }
                }
            ],
            'totalCount': 1
        }
    }
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_approved_1_without_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulationHouseholds'
            ]
        }
    ]
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_first_10_0_with_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_first_10_1_without_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulationHouseholds'
            ]
        }
    ]
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_residence_status_0_with_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_residence_status_1_without_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulationHouseholds'
            ]
        }
    ]
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_size_0_with_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': {
            'edges': [
            ],
            'totalCount': 0
        }
    }
}

snapshots['TargetPopulationHouseholdsQueryTestCase::test_candidate_households_list_by_targeting_criteria_size_1_without_permission 1'] = {
    'data': {
        'targetPopulationHouseholds': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'targetPopulationHouseholds'
            ]
        }
    ]
}
