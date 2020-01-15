# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeliveryTypeChoices::test_delivery_type_choices_query 1'] = {
    'data': {
        'paymentDeliveryTypeChoices': [
            [
                'DELIVERED',
                'Delivered'
            ],
            [
                'IN_PROGRESS',
                'In Progress'
            ]
        ]
    }
}
