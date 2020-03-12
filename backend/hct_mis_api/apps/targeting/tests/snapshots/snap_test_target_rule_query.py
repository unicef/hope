# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSavedTargetRuleQuery::test_all_saved_target_rule_query 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 8
                }
            ],
            'message': 'Field "targetPopulation" of type "TargetPopulationNode!" must have a sub selection.'
        }
    ]
}

snapshots['TestTargetRuleQuery::test_filter_query 1'] = {
    'data': {
        'targetRules': [
        ]
    }
}
