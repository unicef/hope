# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestChangeProgramStatus::test_status_change_0_draft_to_active_with_permission 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_status_change_1_draft_to_acive_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_2_finish_to_active_with_permission 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'ACTIVE'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_status_change_3_finish_to_active_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_4_draft_to_finished_with_permission 1'] = {
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

snapshots['TestChangeProgramStatus::test_status_change_5_draft_to_finished_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_6_active_to_finished_with_permission 1'] = {
    'data': {
        'updateProgram': {
            'program': {
                'status': 'FINISHED'
            }
        }
    }
}

snapshots['TestChangeProgramStatus::test_status_change_7_active_to_finished_without_permission 1'] = {
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
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_8_active_to_draft 1'] = {
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

snapshots['TestChangeProgramStatus::test_status_change_9_finished_to_draft 1'] = {
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
