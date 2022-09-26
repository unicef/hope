# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['GrievanceDocumentsUploadTestCase::test_user_can_send_one_document 1'] = {
    'errors': [
        {
            'message': 'Object of type SimpleUploadedFile is not JSON serializable'
        }
    ]
}
