# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAccountabilitySampleSizeQueries::test_sample_size_by_target_population_0_FULL_LIST 1'] = {
    'data': {
        'accountabilitySampleSize': {
            'numberOfRecipients': 14,
            'sampleSize': 14
        }
    }
}

snapshots['TestAccountabilitySampleSizeQueries::test_sample_size_by_target_population_1_RANDOM 1'] = {
    'data': {
        'accountabilitySampleSize': {
            'numberOfRecipients': 14,
            'sampleSize': 1
        }
    }
}
