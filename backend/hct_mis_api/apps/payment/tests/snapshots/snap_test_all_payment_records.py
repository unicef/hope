# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestAllPaymentRecords::test_fetch_payment_records_only_for_single_household 1'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 3,
            'totalCount': 3
        }
    }
}

snapshots['TestAllPaymentRecords::test_household_without_payment_records_should_return_empty_list 1'] = {
    'data': {
        'allPaymentRecords': {
            'edgeCount': 0,
            'totalCount': 0
        }
    }
}
