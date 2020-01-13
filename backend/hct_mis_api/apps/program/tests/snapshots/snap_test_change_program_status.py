# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestChangeProgramStatus::test_active_to_finished 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'FINISHED'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_draft_to_active 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_finished_to_active 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_active_to_draft 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Active status can only be changed to Finished',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_draft_to_finished 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Draft status can only be changed to Active',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_finished_to_draft 1'] = {
    'data': {
        'updateProgram': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Finished status can only be changed to Active',
            'path': [
                'updateProgram'
            ]
        }
    ]
}
