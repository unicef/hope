from django.db import connections
from django.test.runner import DiscoverRunner
from django.test.utils import get_unique_databases_and_mirrors


class LegacyDatabaseRunner(DiscoverRunner):
    """
    Test runner that will skip attempting to create any database with LEGACY=True
    in its TEST configuration dictionary
    """

    def setup_databases(self, **kwargs):
        return _setup_databases(self.verbosity, self.interactive, self.keepdb, self.debug_sql, self.parallel, **kwargs)


def _setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, **kwargs):
    """Clone of django.test.utils.setup_databases"""
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors()

    old_names = []

    for db_name, aliases in test_databases.values():
        first_alias = None
        for alias in aliases:
            connection = connections[alias]

            # This clause is all that's been added. If the database's TEST configuration
            # has LEGACY=True, skip attempting to create the database, and don't add it
            # to the list of databases to tear down after testing is complete.
            if connection.settings_dict.get("TEST", {}).get("READ_ONLY", False):
                continue

            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                connection.creation.create_test_db(
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
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names
