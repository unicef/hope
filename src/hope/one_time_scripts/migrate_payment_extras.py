import time

from django.db import connection, transaction
from psycopg2 import sql

from hope.models import Payment

ADVISORY_LOCK_NAME = "hope.migrate_payment_extras"
DEFAULT_BLOCKS_PER_BATCH = 10_000
DEFAULT_LOCK_TIMEOUT_MS = 5_000
LEGACY_EXTRAS_PREDICATE = """
extras - ARRAY['extra_fields', 'fsp_extra_fields']::text[] <> '{}'::jsonb
"""


def _get_legacy_extras_count(table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                SELECT COUNT(*)
                FROM {table}
                WHERE {predicate}
                """
            ).format(
                table=sql.Identifier(table_name),
                predicate=sql.SQL(LEGACY_EXTRAS_PREDICATE),
            )
        )
        return cursor.fetchone()[0]


def _get_total_blocks(table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                pg_relation_size(%s::regclass),
                current_setting('block_size')::bigint
            """,
            [table_name],
        )
        relation_size, block_size = cursor.fetchone()
        return (relation_size + block_size - 1) // block_size


def _acquire_advisory_lock() -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(hashtext(%s))", [ADVISORY_LOCK_NAME])
        return cursor.fetchone()[0]


def _release_advisory_lock() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_unlock(hashtext(%s))", [ADVISORY_LOCK_NAME])


def migrate_payment_extras(
    blocks_per_batch: int = DEFAULT_BLOCKS_PER_BATCH,
    sleep_seconds: float = 0.1,
    lock_timeout_ms: int = DEFAULT_LOCK_TIMEOUT_MS,
    statement_timeout_ms: int = 0,
) -> None:
    if connection.vendor != "postgresql":
        raise RuntimeError("migrate_payment_extras requires PostgreSQL.")
    if blocks_per_batch <= 0:
        raise ValueError("blocks_per_batch must be greater than zero.")
    if sleep_seconds < 0:
        raise ValueError("sleep_seconds cannot be negative.")
    if lock_timeout_ms < 0:
        raise ValueError("lock_timeout_ms cannot be negative.")
    if statement_timeout_ms < 0:
        raise ValueError("statement_timeout_ms cannot be negative.")
    if not _acquire_advisory_lock():
        raise RuntimeError("Another migrate_payment_extras function is already running.")

    table_name = Payment._meta.db_table
    updated_rows = 0
    try:
        total_blocks = _get_total_blocks(table_name)
        total_batches = (total_blocks + blocks_per_batch - 1) // blocks_per_batch
        print(f"Starting Payment.extras migration: {total_blocks:,} table blocks in {total_batches:,} batches.")

        for batch_number, start_block in enumerate(range(0, total_blocks, blocks_per_batch), start=1):
            end_block = min(start_block + blocks_per_batch, total_blocks)
            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('lock_timeout', %s, true)",
                    [f"{lock_timeout_ms}ms"],
                )
                cursor.execute(
                    "SELECT set_config('statement_timeout', %s, true)",
                    [f"{statement_timeout_ms}ms"],
                )
                cursor.execute("SELECT set_config('enable_seqscan', 'off', true)")
                cursor.execute(
                    sql.SQL(
                        """
                        UPDATE {table}
                        SET extras =
                            jsonb_build_object(
                                'extra_fields',
                                (extras - ARRAY['extra_fields', 'fsp_extra_fields']::text[])
                                || COALESCE(extras->'extra_fields', '{}'::jsonb)
                            )
                            || CASE
                                WHEN extras ? 'fsp_extra_fields'
                                THEN jsonb_build_object('fsp_extra_fields', extras->'fsp_extra_fields')
                                ELSE '{}'::jsonb
                            END
                        WHERE ctid >= %s::tid
                          AND ctid < %s::tid
                          AND {predicate}
                        """
                    ).format(
                        table=sql.Identifier(table_name),
                        predicate=sql.SQL(LEGACY_EXTRAS_PREDICATE),
                    ),
                    [
                        f"({start_block},0)",
                        f"({end_block},0)",
                    ],
                )
                batch_updated_rows = cursor.rowcount

            updated_rows += batch_updated_rows
            print(
                f"Batch {batch_number:,}/{total_batches:,}, blocks {start_block:,}-{end_block:,}: "
                f"updated {batch_updated_rows:,}, total {updated_rows:,}."
            )
            if sleep_seconds:
                time.sleep(sleep_seconds)

        remaining_rows = _get_legacy_extras_count(table_name)
        if remaining_rows:
            print(
                f"[WARNING] Migration updated {updated_rows:,} rows, but {remaining_rows:,} legacy rows remain. "
                "Run the function again after checking for concurrent legacy writes."
            )
        else:
            print(f"Done. Migrated {updated_rows:,} rows. Remaining legacy Payment.extras rows: 0.")
    finally:
        _release_advisory_lock()
