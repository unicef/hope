"""Register the `v9` ES9 shadow-cluster connection from ELASTICSEARCH_HOST_V9.

Keeps the shadow wiring next to the migration commands instead of in core
settings (config/fragments/es.py); no-op if the env var is unset. On master the
delta runs on the `default` connection (ELASTICSEARCH_HOST), so this helper is
not wired into es_populate_delta -- kept only for a multi-alias shadow setup.
"""

import os

from django.conf import settings
from elasticsearch.dsl import connections


def register_shadow_connection(alias: str = "v9", env_var: str = "ELASTICSEARCH_HOST_V9") -> bool:
    """Add `alias` to ELASTICSEARCH_DSL + the connections registry at runtime. True if registered."""
    host = os.environ.get(env_var, "").strip()
    if not host:
        return False
    settings.ELASTICSEARCH_DSL.setdefault(alias, {"hosts": host, "request_timeout": 30})
    connections.configure(**settings.ELASTICSEARCH_DSL)
    return True
