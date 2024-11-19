# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan 1'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 4,
            'totalCount': 4
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan 2'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 1,
            'totalCount': 1
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan 3'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 2,
            'totalCount': 2
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 1'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 2,
            'totalCount': 2
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 2'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 1,
            'totalCount': 1
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 3'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 4'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 2,
            'totalCount': 2
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 5'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 6'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 2,
            'totalCount': 2
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 7'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 8'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_cash_plan_and_household_and_program 9'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_household 1'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 3,
            'totalCount': 3
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_household 2'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 4,
            'totalCount': 4
        }
    }
}

snapshots['TestAllPaymentRecords::test_fetch_payment_records_filter_by_household 3'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}
