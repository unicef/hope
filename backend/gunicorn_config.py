import multiprocessing
import os

bind = "0.0.0.0:8000"
backlog = 2048


worker_class = "gthread"
timeout = 65
keepalive = 2
workers = os.getenv("GUNICORN_WORKERS") if os.getenv("GUNICORN_WORKERS") else 4
threads = os.getenv("GUNICORN_THREADS") if os.getenv("GUNICORN_THREADS") else 14

proc_name = None
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None


errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
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


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
