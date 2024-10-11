import os
from typing import Any

bind = "0.0.0.0:8000"
backlog = 2048


worker_class = "gthread"
timeout = 65
keepalive = 2
workers = os.getenv("GUNICORN_WORKERS") or 4
threads = os.getenv("GUNICORN_THREADS") or 8

proc_name = None
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
max_requests = 500

errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


def post_fork(server: Any, worker: Any) -> None:
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server: Any, worker: Any) -> None:
    pass


def pre_exec(server: Any) -> None:
    server.log.info("Forked child, re-executing.")


def when_ready(server: Any) -> None:
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker: Any) -> None:
    worker.log.info("Worker received INT or QUIT signal")

    # get traceback info
    import sys
    import threading
    import traceback

    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: {}({})".format(id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "{}", line {}, in {}'.format(filename, lineno, name))
            if line:
                code.append("  {}".format(line.strip()))
    worker.log.warning("\n".join(code))


def worker_abort(worker: Any) -> None:
    worker.log.info("worker received SIGABRT signal")
