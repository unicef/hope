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
                        'coreRules': '{"sex": "MALE", "intake_group": "Bit sound base religious gun treat let really.", "num_individuals_max": 13, "num_individuals_min": 2}',
                        'flexRules': '{"age_max": 58, "age_min": 10}',
                        'targetPopulation': {
                            'name': 'Be several suffer town firm.'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "MALE", "intake_group": "In avoid drive task.", "num_individuals_max": 10, "num_individuals_min": 2}',
                        'flexRules': '{"age_max": 114, "age_min": 7}',
                        'targetPopulation': {
                            'name': 'Be several suffer town firm.'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "OTHER", "intake_group": "Couple moment one popular.", "num_individuals_max": 16, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 20, "age_min": 10}',
                        'targetPopulation': {
                            'name': 'Be several suffer town firm.'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "MALE", "intake_group": "Government want high training back goal.", "num_individuals_max": 20, "num_individuals_min": 1}',
                        'flexRules': '{"age_max": 11, "age_min": 3}',
                        'targetPopulation': {
                            'name': 'Be several suffer town firm.'
                        }
                    }
                },
                {
                    'node': {
                        'coreRules': '{"sex": "OTHER", "intake_group": "Me from daughter interest benefit assume.", "num_individuals_max": 6, "num_individuals_min": 2}',
                        'flexRules': '{"age_max": 38, "age_min": 4}',
                        'targetPopulation': {
                            'name': 'Be several suffer town firm.'
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
            'coreRules': '{"sex": "MALE", "intake_group": "Bit sound base religious gun treat let really.", "num_individuals_max": 13, "num_individuals_min": 2}',
            'flexRules': '{"age_max": 58, "age_min": 10}',
            'targetPopulation': {
                'name': 'Be several suffer town firm.'
            }
        }
    }
}
