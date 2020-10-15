from __future__ import absolute_import

import os

import xmlrunner
from django.conf import settings
from django.db import connections
from snapshottest.django import TestRunner
from xmlrunner.extra.djangotestrunner import XMLTestRunner


def create_test_db_and_schemas(creation, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
    """
    Create a test database, prompting the user for confirmation if the
    database already exists. Return the name of the test database created.
    """
    # Don't import django.core.management if it isn't needed.
    from django.core.management import call_command

    test_database_name = creation._get_test_db_name()

    if verbosity >= 1:
        action = "Creating"
        if keepdb:
            action = "Using existing"

        creation.log(
            "%s test database for alias %s..."
            % (
                action,
                creation._get_database_display_str(verbosity, test_database_name),
            )
        )

    # We could skip this call if keepdb is True, but we instead
    # give it the keepdb param. This is to handle the case
    # where the test DB doesn't exist, in which case we need to
    # create it, then just not destroy it. If we instead skip
    # this, we will get an exception.
    creation._create_test_db(verbosity, autoclobber, keepdb)
    creation.connection.close()
    settings.DATABASES[creation.connection.alias]["NAME"] = test_database_name
    creation.connection.settings_dict["NAME"] = test_database_name

    creation.connection.cursor().execute("CREATE SCHEMA IF NOT EXISTS ca")
    creation.connection.cursor().execute("CREATE SCHEMA IF NOT EXISTS mis")
    creation.connection.cursor().execute("CREATE SCHEMA IF NOT EXISTS erp")
    # We report migrate messages at one level lower than that requested.
    # This ensures we don't get flooded with messages during testing
    # (unless you really ask to be flooded).
    call_command(
        "migrate",
        verbosity=max(verbosity - 1, 0),
        interactive=False,
        database=creation.connection.alias,
        run_syncdb=True,
    )

    # We then serialize the current state of the database into a string
    # and store it on the connection. This slightly horrific process is so people
    # who are testing on databases without transactions or who are using
    # a TransactionTestCase still get a clean database on every test run.
    if serialize:
        creation.connection._test_serialized_contents = creation.serialize_db_to_string()

    call_command("createcachetable", database=creation.connection.alias)

    # Ensure a connection for the side effect of initializing the test database.
    creation.connection.ensure_connection()

    return test_database_name


def create_fake_test_db(creation, verbosity=1, autoclobber=False, serialize=True, keepdb=False):
    """
    Create a test database, prompting the user for confirmation if the
    database already exists. Return the name of the test database created.
    """
    # Don't import django.core.management if it isn't needed.
    from django.core.management import call_command

    test_database_name = creation._get_test_db_name()

    if verbosity >= 1:
        action = "Creating"
        if keepdb:
            action = "Using existing"

        creation.log(
            "%s test database for alias %s..."
            % (
                action,
                creation._get_database_display_str(verbosity, test_database_name),
            )
        )

    # We could skip this call if keepdb is True, but we instead
    # give it the keepdb param. This is to handle the case
    # where the test DB doesn't exist, in which case we need to
    # create it, then just not destroy it. If we instead skip
    # this, we will get an exception.
    creation.connection.close()
    settings.DATABASES[creation.connection.alias]["NAME"] = test_database_name
    creation.connection.settings_dict["NAME"] = test_database_name
    call_command(
        "migrate",
        verbosity=max(verbosity - 1, 0),
        interactive=False,
        database=creation.connection.alias,
        run_syncdb=True,
    )
    # We then serialize the current state of the database into a string
    # and store it on the connection. This slightly horrific process is so people
    # who are testing on databases without transactions or who are using
    # a TransactionTestCase still get a clean database on every test run.
    creation.connection.ensure_connection()

    call_command("createcachetable", database=creation.connection.alias)

    return test_database_name


def _setup_schema_database(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, alias=None, **kwargs):
    """Create the test databases."""

    connection = connections[alias]
    old_name = (connection, alias, True)
    create_test_db_and_schemas(
        connection.creation,
        verbosity=verbosity,
        autoclobber=not interactive,
        keepdb=keepdb,
        serialize=connection.settings_dict.get("TEST", {}).get("SERIALIZE", True),
    )
    if parallel > 1:
        for index in range(parallel):
            connection.creation.clone_test_db(
                suffix=str(index + 1),
                verbosity=verbosity,
                keepdb=keepdb,
            )
    return [old_name]


class PostgresTestRunner(TestRunner):
    test_runner = xmlrunner.XMLTestRunner

    def get_resultclass(self):
        # Django provides `DebugSQLTextTestResult` if `debug_sql` argument is True
        # To use `xmlrunner.result._XMLTestResult` we supress default behavior
        return None

    def get_test_runner_kwargs(self):
        # We use separate verbosity setting for our runner
        verbosity = getattr(settings, 'TEST_OUTPUT_VERBOSE', 1)
        if isinstance(verbosity, bool):
            verbosity = (1, 2)[verbosity]
        verbosity = verbosity  # not self.verbosity

        output_dir = getattr(settings, 'TEST_OUTPUT_DIR', '.')
        single_file = getattr(settings, 'TEST_OUTPUT_FILE_NAME', None)

        # For single file case we are able to create file here
        # But for multiple files case files will be created inside runner/results
        if single_file is None:  # output will be a path (folder)
            output = output_dir
        else:  # output will be a stream
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            file_path = os.path.join(output_dir, single_file)
            output = open(file_path, 'wb')

        return dict(
            verbosity=verbosity,
            descriptions=getattr(settings, 'TEST_OUTPUT_DESCRIPTIONS', False),
            failfast=self.failfast,
            resultclass=self.get_resultclass(),
            output=output,
        )

    def run_suite(self, suite, **kwargs):
        runner_kwargs = self.get_test_runner_kwargs()
        runner = self.test_runner(**runner_kwargs)
        results = runner.run(suite)
        if hasattr(runner_kwargs['output'], 'close'):
            runner_kwargs['output'].close()
        return results

    def teardown_databases(self, old_config, **kwargs):
        connections["cash_assist_datahub_ca"].close()
        connections["cash_assist_datahub_erp"].close()
        return super().teardown_databases(old_config, **kwargs)

    def setup_databases(self, **kwargs):
        old_names = []
        created = False
        for alias in connections:
            if alias in (
                "cash_assist_datahub_mis",
                "cash_assist_datahub_ca",
                "cash_assist_datahub_erp",
            ):

                aliases = kwargs.get("aliases")
                aliases.discard(alias)
                if not created:
                    old_names.extend(
                        _setup_schema_database(
                            self.verbosity, self.interactive, self.keepdb, self.debug_sql, self.parallel, alias=alias
                        )
                    )
                    created = True
                else:
                    connection = connections[alias]
                    create_fake_test_db(
                        connection.creation,
                        verbosity=self.verbosity,
                        autoclobber=not self.interactive,
                        keepdb=self.keepdb,
                        serialize=connection.settings_dict.get("TEST", {}).get("SERIALIZE", True),
                    )
        old_names.extend(super().setup_databases(**kwargs))

        return old_names
