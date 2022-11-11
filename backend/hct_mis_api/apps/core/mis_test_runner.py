import os
from typing import Any, Dict

from django.conf import settings
from django.db import connections
from django.test.runner import ParallelTestSuite

import xmlrunner
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.connections import connections as es_connections
from snapshottest.django import TestRunner

_worker_id = 0


def _elastic_search_init_worker(counter):
    global _worker_id

    with counter.get_lock():
        counter.value += 1
        _worker_id = counter.value

    for alias in connections:
        connection = connections[alias]
        settings_dict = connection.creation.get_test_db_clone_settings(_worker_id)
        # connection.settings_dict must be updated in place for changes to be
        # reflected in django.db.connections. If the following line assigned
        # connection.settings_dict = settings_dict, new threads would connect
        # to the default database instead of the appropriate clone.
        connection.settings_dict.update(settings_dict)
        connection.close()

    # Initialize the elasticsearch connection for the current worker
    worker_connection_postfix = f"default_worker_{_worker_id}"
    es_connections.create_connection(alias=worker_connection_postfix, **settings.ELASTICSEARCH_DSL["default"])

    # Update index names and connections
    for doc in registry.get_documents():
        doc._index._name += f"_{_worker_id}"
        # Use the worker-specific connection
        doc._index._using = worker_connection_postfix


class MisParallelTestSuite(ParallelTestSuite):
    init_worker = _elastic_search_init_worker


class PostgresTestRunner(TestRunner):
    test_runner = xmlrunner.XMLTestRunner
    parallel_test_suite = MisParallelTestSuite

    def get_resultclass(self) -> None:
        # Django provides `DebugSQLTextTestResult` if `debug_sql` argument is True
        # To use `xmlrunner.result._XMLTestResult` we supress default behavior
        return None

    def get_test_runner_kwargs(self) -> Dict[str, Any]:
        # We use separate verbosity setting for our runner
        verbosity = getattr(settings, "TEST_OUTPUT_VERBOSE", 1)
        if isinstance(verbosity, bool):
            verbosity = (1, 2)[verbosity]
        verbosity = verbosity  # not self.verbosity

        output_dir = getattr(settings, "TEST_OUTPUT_DIR", ".")
        single_file = getattr(settings, "TEST_OUTPUT_FILE_NAME", None)

        # For single file case we are able to create file here
        # But for multiple files case files will be created inside runner/results
        if single_file is None:  # output will be a path (folder)
            output = output_dir
        else:  # output will be a stream
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            file_path = os.path.join(output_dir, single_file)
            output = open(file_path, "wb")

        return {
            "verbosity": verbosity,
            "descriptions": getattr(settings, "TEST_OUTPUT_DESCRIPTIONS", False),
            "failfast": self.failfast,
            "resultclass": self.get_resultclass(),  # type: ignore
            "output": output,
        }

    def run_suite(self, suite, **kwargs) -> Any:
        runner_kwargs = self.get_test_runner_kwargs()
        runner = self.test_runner(**runner_kwargs)
        results = runner.run(suite)
        if hasattr(runner_kwargs["output"], "close"):
            runner_kwargs["output"].close()
        return results

    def setup_databases(self, **kwargs: Any) -> Any:
        return super().setup_databases(**kwargs)
