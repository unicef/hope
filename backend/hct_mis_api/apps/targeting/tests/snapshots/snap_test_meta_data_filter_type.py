# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestMetaDataFilterType::test_meta_data_filter_type_query 1'] = {
    'data': {
        'metaDataFilterType': {
            'coreFieldTypes': [
                '{"type": "INTEGER", "name": "years_in_school", "label": "years in school", "hint": "number of years spent in school", "required": true, "choices": [], "associated_with": "individual_fields"}',
                '{"type": "INTEGER", "name": "age", "label": "age", "hint": "age in years", "required": true, "choices": [], "associated_with": "individual_fields"}',
                '{"type": "INTEGER", "name": "family_size", "label": "Family Size", "hint": "how many persons in the household", "required": true, "choices": [], "associated_with": "household_fields"}',
                '{"type": "SELECT_ONE", "name": "residence_status", "required": true, "label": "Residence Status", "hint": "residential status of household", "choices": [], "associated_with": "household_fields"}'
            ],
            'flexFieldTypes': [
            ]
        }
    }
}
