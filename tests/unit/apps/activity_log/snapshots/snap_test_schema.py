# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestLogEntriesQueries::test_all_logs_queries 1'] = {
    'data': {
        'allLogEntries': {
            '__typename': 'LogEntryNodeConnection',
            'edges': [
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'c74612a1-212c-4148-be5b-4b41d20e623c',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                },
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'ad17c53d-11b0-4e9b-8407-2e034f03fd31',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                }
            ],
            'pageInfo': {
                '__typename': 'PageInfo',
                'endCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
                'hasNextPage': False,
                'hasPreviousPage': False,
                'startCursor': 'YXJyYXljb25uZWN0aW9uOjA='
            },
            'totalCount': 2
        }
    }
}

snapshots['TestLogEntriesQueries::test_all_logs_queries_without_perms 1'] = {
    'data': {
        'allLogEntries': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 3,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allLogEntries'
            ]
        }
    ]
}

snapshots['TestLogEntriesQueries::test_filter_by_object_id 1'] = {
    'data': {
        'allLogEntries': {
            '__typename': 'LogEntryNodeConnection',
            'edges': [
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'ad17c53d-11b0-4e9b-8407-2e034f03fd31',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                }
            ],
            'pageInfo': {
                '__typename': 'PageInfo',
                'endCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                'hasNextPage': False,
                'hasPreviousPage': False,
                'startCursor': 'YXJyYXljb25uZWN0aW9uOjA='
            },
            'totalCount': 1
        }
    }
}

snapshots['TestLogEntriesQueries::test_filter_by_program_id 1'] = {
    'data': {
        'allLogEntries': {
            '__typename': 'LogEntryNodeConnection',
            'edges': [
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'ad17c53d-11b0-4e9b-8407-2e034f03fd31',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                }
            ],
            'pageInfo': {
                '__typename': 'PageInfo',
                'endCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                'hasNextPage': False,
                'hasPreviousPage': False,
                'startCursor': 'YXJyYXljb25uZWN0aW9uOjA='
            },
            'totalCount': 1
        }
    }
}

snapshots['TestLogEntriesQueries::test_filter_by_user_id 1'] = {
    'data': {
        'allLogEntries': {
            '__typename': 'LogEntryNodeConnection',
            'edges': [
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'c74612a1-212c-4148-be5b-4b41d20e623c',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                },
                {
                    '__typename': 'LogEntryNodeEdge',
                    'cursor': 'YXJyYXljb25uZWN0aW9uOjE=',
                    'node': {
                        '__typename': 'LogEntryNode',
                        'action': 'CREATE',
                        'contentType': {
                            '__typename': 'ContentTypeObjectType',
                            'appLabel': 'program',
                            'model': 'program',
                            'name': 'Programme'
                        },
                        'objectId': 'ad17c53d-11b0-4e9b-8407-2e034f03fd31',
                        'user': {
                            '__typename': 'UserNode',
                            'firstName': 'First',
                            'lastName': 'Last'
                        }
                    }
                }
            ],
            'pageInfo': {
                '__typename': 'PageInfo',
                'endCursor': 'YXJyYXljb25uZWN0aW9uOjE=',
                'hasNextPage': False,
                'hasPreviousPage': False,
                'startCursor': 'YXJyYXljb25uZWN0aW9uOjA='
            },
            'totalCount': 2
        }
    }
}

snapshots['TestLogEntriesQueries::test_log_entry_action_choices 1'] = {
    'data': {
        'logEntryActionChoices': [
            {
                'name': 'Create',
                'value': 'CREATE'
            },
            {
                'name': 'Delete',
                'value': 'DELETE'
            },
            {
                'name': 'Soft Delete',
                'value': 'SOFT_DELETE'
            },
            {
                'name': 'Update',
                'value': 'UPDATE'
            }
        ]
    }
}
