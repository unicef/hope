from hct_mis_api.apps.core.celery import app


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
