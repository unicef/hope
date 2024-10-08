# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestSampleSize::test_number_of_queries 1'] = {
    'data': {
        'sampleSize': {
            '__typename': 'GetCashplanVerificationSampleSizeObject',
            'paymentRecordCount': 4,
            'sampleSize': 4
        }
    }
}
