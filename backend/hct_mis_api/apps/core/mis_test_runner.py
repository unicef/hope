from __future__ import absolute_import

from types import MethodType

from django.db import connections
from snapshottest.django import TestRunner


def prepare_schema(self):
    self.connect()

    options = self.connection.info.options
    schema = options.replace("-c search_path=", "")
    self.connection.cursor().execute(
        f"CREATE SCHEMA IF NOT EXISTS {schema}"
    )


class PostgresTestRunner(TestRunner):
    def setup_databases(self, **kwargs):
        for connection_name in connections:
            if connection_name in (
                "cash_assist_datahub_mis",
                "cash_assist_datahub_ca",
                "cash_assist_datahub_erp",
            ):
                connection = connections[connection_name]
                connection.prepare_database = MethodType(
                    prepare_schema, connection
                )
                aliases = kwargs.get("aliases")
                aliases.discard(connection_name)

        return super().setup_databases(**kwargs)
