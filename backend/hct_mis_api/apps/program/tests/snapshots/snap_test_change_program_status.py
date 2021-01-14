# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestChangeProgramStatus::test_status_change_0_draft_to_active_with_permission 1'] = {
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_2_finish_to_active_with_permission 1'] = {
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
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
            'message': "mutate() missing 1 required positional argument: 'version'",
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
            'message': "mutate() missing 1 required positional argument: 'version'",
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
}

snapshots['TestChangeProgramStatus::test_status_change_6_active_to_finished_with_permission 1'] = {
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
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
            'message': "mutate() missing 1 required positional argument: 'version'",
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
            'message': "mutate() missing 1 required positional argument: 'version'",
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
            'message': "mutate() missing 1 required positional argument: 'version'",
            'path': [
                'updateProgram'
            ]
        }
    ]
}
