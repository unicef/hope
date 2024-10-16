import json

import factory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.dashboard.models import DashReport


class DashReportFactory(DjangoModelFactory):
    class Meta:
        model = DashReport

    business_area = factory.SubFactory(BusinessAreaFactory)

    # Provide valid JSON content
    file = factory.django.FileField(
        filename="test_report.json",
        data=json.dumps(
            [
                {
                    "id": "a319f0ce-c263-48b0-80b8-a7b38a6105aa",
                    "business_area": "afghanistan",
                    "payments": [
                        {
                            "delivered_quantity": "2103.00",
                            "delivery_date": "2024-08-14T02:31:49Z",
                            "delivered_quantity_usd": "2313.30",
                            "currency": "AFN",
                            "fsp": "RFSP1",
                            "delivery_type": "Mobile Money",
                            "status": "Transaction Successful",
                        },
                        {
                            "delivered_quantity": "434.00",
                            "delivery_date": "2024-02-26T00:51:08Z",
                            "delivered_quantity_usd": "60.76",
                            "currency": "AFN",
                            "fsp": "service prov 1",
                            "delivery_type": "Cash",
                            "status": "Transaction Successful",
                        },
                        {
                            "delivered_quantity": "4568.00",
                            "delivery_date": "2023-07-19T20:47:43Z",
                            "delivered_quantity_usd": "639.52",
                            "currency": "AFN",
                            "fsp": "service prov 1",
                            "delivery_type": "Cash",
                            "status": "Transaction Successful",
                        },
                    ],
                    "program": "First program to be done",
                    "size": 7,
                    "first_registration_date": "2023-04-17T19:47:36Z",
                    "admin1": "Kabul",
                    "admin2": "Musayi",
                    "sector": "EDUCATION",
                    "children_count": 1,
                },
                {
                    "id": "a0c45353-b508-4af1-8834-7c0da477d3ce",
                    "business_area": "afghanistan",
                    "payments": [
                        {
                            "delivered_quantity": "357.00",
                            "delivery_date": "2023-01-09T02:15:52Z",
                            "delivered_quantity_usd": "392.70",
                            "currency": "AFN",
                            "fsp": "RFSP1",
                            "delivery_type": "Cash",
                            "status": "Pending",
                        },
                        {
                            "delivered_quantity": None,
                            "delivery_date": "2022-08-15T20:16:58Z",
                            "delivered_quantity_usd": None,
                            "currency": "AFN",
                            "fsp": "RFSP1",
                            "delivery_type": "Cash",
                            "status": "Transaction Successful",
                        },
                        {
                            "delivered_quantity": "3746.00",
                            "delivery_date": "2024-04-26T05:09:30Z",
                            "delivered_quantity_usd": "4120.60",
                            "currency": "AFN",
                            "fsp": "service prov 1",
                            "delivery_type": "Mobile Money",
                            "status": "Transaction Successful",
                        },
                        {
                            "delivered_quantity": None,
                            "delivery_date": "2023-02-22T09:37:41Z",
                            "delivered_quantity_usd": None,
                            "currency": "AFN",
                            "fsp": "service prov 1",
                            "delivery_type": "Cash_by_fsp",
                            "status": "Transaction Successful",
                        },
                    ],
                    "program": "First program to be done",
                    "size": 7,
                    "first_registration_date": "2024-01-17T20:37:02Z",
                    "admin1": "Ghor",
                    "admin2": "Tolak",
                    "sector": "EDUCATION",
                    "children_count": 3,
                },
            ]
        ),
    )
    status = DashReport.COMPLETED
