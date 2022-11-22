# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_household_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_household_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_individual_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_individual_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_payment_record_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[0]'; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_payment_record_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[0]'; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_two_payment_records_0_with_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[0]'; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[1]'; ID cannot represent value: <UUID instance>"
        }
    ]
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_two_payment_records_1_without_permission 1'] = {
    'data': None,
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 6
                }
            ],
            'message': "Variable '$household' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 7
                }
            ],
            'message': "Variable '$individual' got invalid value <UUID instance>; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[0]'; ID cannot represent value: <UUID instance>"
        },
        {
            'locations': [
                {
                    'column': 7,
                    'line': 8
                }
            ],
            'message': "Variable '$paymentRecord' got invalid value <UUID instance> at 'paymentRecord[1]'; ID cannot represent value: <UUID instance>"
        }
    ]
}
