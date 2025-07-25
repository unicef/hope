# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["TestRuleSchema::test_rule_schema_shows_only_allowed_rules 1"] = {
    "data": {
        "allSteficonRules": {
            "edges": [{"node": {"deprecated": False, "enabled": True, "name": "rule_1", "type": "TARGETING"}}]
        }
    }
}
