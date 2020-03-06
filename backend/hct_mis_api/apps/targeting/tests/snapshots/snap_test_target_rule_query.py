# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestTargetRuleQuery::test_filter_query 1'] = {
    'data': {
        'targetRules': [
        ]
    }
}

snapshots['TestSavedTargetRuleQuery::test_all_saved_target_rule_query 1'] = {
    'data': {
        'allSavedTargetRule': {
            'edges': [
                {
                    'node': {
                        'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 25, "age_min": 1}',
                        'targetPopulation': {
                            'name': 'sentence'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 25, "age_min": 1}',
                        'targetPopulation': {
                            'name': 'sentence'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 25, "age_min": 1}',
                        'targetPopulation': {
                            'name': 'sentence'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 25, "age_min": 1}',
                        'targetPopulation': {
                            'name': 'sentence'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 25, "age_min": 1}',
                        'targetPopulation': {
                            'name': 'sentence'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['TestSavedTargetRuleQuery::test_saved_target_rule_query 1'] = {
    'data': {
        'savedTargetRule': {
            'coreRules': '{"sex": "Male", "intake_group": "registration import name", "num_individuals_max": 5, "num_individuals_min": 1}',
            'flexRules': '{"age_max": 25, "age_min": 1}',
            'targetPopulation': {
                'name': 'sentence'
            }
        }
    }
}
