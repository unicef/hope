# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["TestFSPRelatedSchema::test_query_all_financial_service_provider_xlsx_templates 1"] = {
    "errors": [
        {
            "locations": [{"column": 4, "line": 12}],
            "message": 'Cannot query field "allFinancialServiceProviderXlsxTemplates" on type "Query".',
        }
    ]
}

snapshots["TestFSPRelatedSchema::test_query_all_financial_service_providers 1"] = {
    "errors": [
        {
            "locations": [{"column": 4, "line": 16}],
            "message": 'Cannot query field "allFinancialServiceProviders" on type "Query".',
        }
    ]
}

snapshots["TestFSPRelatedSchema::test_query_single_financial_service_provider 1"] = {
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": 'Cannot query field "financialServiceProvider" on type "Query".',
        }
    ]
}

snapshots["TestFSPRelatedSchema::test_query_single_financial_service_provider_xlsx_template 1"] = {
    "errors": [
        {
            "locations": [{"column": 3, "line": 3}],
            "message": 'Cannot query field "financialServiceProviderXlsxTemplate" on type "Query".',
        }
    ]
}
