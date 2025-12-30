#!/usr/bin/env python3
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path


def start(cmd: str, cwd: str | Path | None = None) -> subprocess.Popen:
    return subprocess.Popen(cmd, shell=True, cwd=cwd, env=os.environ.copy())


def runserver_with_frontend(runserver_args: list[str]) -> None:
    processes: list[subprocess.Popen] = []

    try:
        nvm_bin = os.environ.get("NVM_BIN")
        node = str(Path(nvm_bin) / "node") if nvm_bin else "node"

        yarn_js = shutil.which("yarn")
        if not yarn_js:
            sys.exit("❌  Could not find 'yarn' in PATH. Please install yarn or add it to PATH.")

        # frontend: yarn build-and-watch
        processes.append(start(f"{node} {yarn_js} build-and-watch", cwd="src/frontend"))

        # backend: call manage.py runserver with --classic to avoid recursion
        backend_cmd = f"{sys.executable} {Path(sys.argv[0])} runserver"
        if runserver_args:
            backend_cmd += " " + " ".join(runserver_args)
        backend_cmd += " --classic"

        processes.append(start(backend_cmd))

    except Exception as exc:
        for p in processes:
            p.terminate()
        for p in processes:
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()
        sys.exit(f"❌  Failed to start runserver with frontend: {exc}")

    def shutdown(*_):
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
            # if any process exits, shut everything down
            for p in processes:
                if p.poll() is not None:
                    shutdown()
            signal.pause()
    except KeyboardInterrupt:
        shutdown()


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope.config.settings")

    from django.core.management import execute_from_command_line

    argv = sys.argv[:]

    is_runserver = len(argv) > 1 and argv[1] == "runserver"
    if is_runserver:
        runserver_args = argv[2:]
        classic_flag = "--classic"

        if classic_flag in runserver_args:
            # classic Django runserver without frontend
            runserver_args = [a for a in runserver_args if a != classic_flag]
            new_argv = [argv[0], "runserver", *runserver_args]
            execute_from_command_line(new_argv)
            return

        # default: runserver + yarn build-and-watch
        runserver_with_frontend(runserver_args)
        return

    execute_from_command_line(argv)


if __name__ == "__main__":
    main()
