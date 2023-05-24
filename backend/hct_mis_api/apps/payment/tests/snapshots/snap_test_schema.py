# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPaymentSchema::test_query_all_fsp_xlsx_templates 1'] = {
    'data': {
        'allFinancialServiceProviderXlsxTemplates': {
            'edges': [
                {
                    'node': {
                        'columns': [
                            'column_1',
                            'column_2'
                        ],
                        'name': 'FSP_template_1'
                    }
                },
                {
                    'node': {
                        'columns': [
                            'column_3',
                            'column_4'
                        ],
                        'name': 'FSP_template_2'
                    }
                }
            ]
        }
    }
}
