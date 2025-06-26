#!/usr/bin/env python3
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path


def start(cmd: str, cwd: str | Path | None = None) -> subprocess.Popen:
    return subprocess.Popen(cmd, shell=True, cwd=cwd, env=os.environ.copy())


def run_dev() -> None:
    processes: list[subprocess.Popen] = []
    try:
        node = str(Path(os.environ.get("NVM_BIN", "")) / "node") if os.environ.get("NVM_BIN") else "node"
        yarn_js = shutil.which("yarn")
        subprocess.check_call(f"{node} {yarn_js}", shell=True, cwd="src/frontend")
        processes.append(start(f"{node} {yarn_js} dev", cwd="src/frontend"))
        subprocess.check_call("uv sync --no-install-package hope", shell=True)
        processes.append(start(f"{sys.executable} manage.py runserver 127.0.0.1:8080"))
        processes.append(
            start(
                f"{sys.executable} -m celery -A hct_mis_api.apps.core.celery beat -l INFO --scheduler hct_mis_api.apps.core.models:CustomDatabaseScheduler"
            )
        )
        processes.append(
            start(
                f"watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- {sys.executable} -m celery -A hct_mis_api.apps.core.celery worker -E -l info -Q default --max-tasks-per-child=4 --concurrency=4"
            )
        )
    except subprocess.CalledProcessError as exc:
        sys.exit(f"❌  {exc.cmd} exited with {exc.returncode}")

    def shutdown(*_):
        print("\n⇢  Stopping all services…")
        for p in processes:
            p.terminate()
        for p in processes:
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"⚠️  {p.args} exited with {p.returncode}")
                    shutdown()
            signal.pause()
    except KeyboardInterrupt:
        shutdown()


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        sys.argv.pop(1)
        run_dev()
        return
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hct_mis_api.config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
