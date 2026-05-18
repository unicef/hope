import logging
import os

from django.db import migrations

logger = logging.getLogger(__name__)

REDIS_PREFIX = "constance:"
DB_PREFIX = ""


def copy_constance_from_redis(apps, schema_editor):
    redis_url = os.environ.get("CONSTANCE_REDIS_CONNECTION")
    if not redis_url:
        logger.info("CONSTANCE_REDIS_CONNECTION not set — skipping constance redis→db copy.")
        return

    try:
        import redis
    except ImportError:
        logger.warning("redis client not available — skipping constance redis→db copy.")
        return

    try:
        client = redis.from_url(redis_url)
        client.ping()
    except redis.RedisError as exc:
        logger.warning("Redis unreachable (%s) — skipping constance redis→db copy.", exc)
        return

    from django.conf import settings

    Constance = apps.get_model("constance", "Constance")

    copied = 0
    for key in settings.CONSTANCE_CONFIG:
        raw = client.get(f"{REDIS_PREFIX}{key}")
        if raw is None:
            continue
        value = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        Constance.objects.update_or_create(
            key=f"{DB_PREFIX}{key}",
            defaults={"value": value},
        )
        copied += 1

    logger.info("constance redis→db copy finished — %d keys migrated.", copied)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0022_migration"),
        ("constance", "0003_drop_pickle"),
    ]
    operations = [
        migrations.RunPython(copy_constance_from_redis, migrations.RunPython.noop),
    ]
