# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceAreaQuery::test_admin2_is_filtered_when_partner_has_business_area_access_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': 'doshi'
                    }
                },
                {
                    'node': {
                        'description': 'burka'
                    }
                },
                {
                    'node': {
                        'description': 'quadis'
                    }
                },
                {
                    'node': {
                        'description': 'no_admin'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceAreaQuery::test_admin2_is_filtered_when_partner_has_business_area_access_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceAreaQuery::test_admin2_is_filtered_when_partner_has_business_area_acess_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceAreaQuery::test_grievance_ticket_are_filtered_when_partner_is_unicef_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': 'doshi'
                    }
                },
                {
                    'node': {
                        'description': 'burka'
                    }
                },
                {
                    'node': {
                        'description': 'quadis'
                    }
                },
                {
                    'node': {
                        'description': 'no_admin'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceAreaQuery::test_grievance_ticket_are_filtered_when_partner_is_unicef_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceAreaQuery::test_many_admin2_is_filtered_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': 'doshi'
                    }
                },
                {
                    'node': {
                        'description': 'burka'
                    }
                },
                {
                    'node': {
                        'description': 'quadis'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceAreaQuery::test_many_admin2_is_filtered_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceAreaQuery::test_one_admin2_is_filtered_0_with_permission 1'] = {
    'data': {
        'allGrievanceTicket': {
            'edges': [
                {
                    'node': {
                        'description': 'doshi'
                    }
                }
            ]
        }
    }
}

snapshots['TestGrievanceAreaQuery::test_one_admin2_is_filtered_1_without_permission 1'] = {
    'data': {
        'allGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'allGrievanceTicket'
            ]
        }
    ]
}
