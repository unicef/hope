# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllProgramsQuery::test_all_programs_query_0_with_permission 1'] = {
    'data': {
        'allPrograms': {
            'edges': [
                {
                    'node': {
                        'name': 'Program with all partners access'
                    }
                },
                {
                    'node': {
                        'name': 'Program with partner access'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['TestAllProgramsQuery::test_all_programs_query_1_without_permission 1'] = {
    'data': {
        'allPrograms': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allPrograms'
            ]
        }
    ]
}

snapshots['TestAllProgramsQuery::test_all_programs_query_unicef_partner 1'] = {
    'data': {
        'allPrograms': {
            'edges': [
                {
                    'node': {
                        'name': 'Program with all partners access'
                    }
                },
                {
                    'node': {
                        'name': 'Program with none partner access'
                    }
                },
                {
                    'node': {
                        'name': 'Program with partner access'
                    }
                },
                {
                    'node': {
                        'name': 'Program without partner access'
                    }
                }
            ],
            'totalCount': 4
        }
    }
}
