# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestMetaDataFilterType::test_core_meta_type_query 1'] = {
    'data': {
        'allFieldsAttributes': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 14,
                    'line': 3
                }
            ],
            'message': "'SoftDeletableQuerySet' object can't be concatenated",
            'path': [
                'allFieldsAttributes'
            ]
        }
    ]
}
