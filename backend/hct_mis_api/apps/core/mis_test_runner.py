import os
import unittest
from typing import Any, Dict, List

from django.conf import settings
from django.test.runner import ParallelTestSuite, partition_suite_by_case

import xmlrunner
from snapshottest.django import TestRunner

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase


def elastic_search_partition_suite_by_case(suite) -> List:
    """Ensure to run all elastic search without parallel"""
    groups = []
    other_tests = []
    suite_class = type(suite)
    es_group = []
    for test in suite:
        if not isinstance(test, BaseElasticSearchTestCase):
            other_tests.append(test)
            continue
        if isinstance(test, unittest.TestCase):
            es_group.append(test)

    groups.append(suite_class(es_group))
    groups.extend(partition_suite_by_case(suite_class(other_tests)))
    return groups


class MisParallelTestSuite(ParallelTestSuite):
    def __init__(self, suite, processes, failfast=False):
        self.processes = processes
        self.failfast = failfast
        super().__init__(suite, processes, failfast)
        self.subsuites = elastic_search_partition_suite_by_case(suite)


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

    def setup_databases(self, **kwargs: Dict) -> Any:
        return super().setup_databases(**kwargs)
