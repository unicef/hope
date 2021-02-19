import os
import sys
from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
import sentry_sdk


def setup_django_for_airflow():
    sys.path.append('/usr/local/airflow/backend/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hct_mis_api.settings")

    import django
    django.setup()


class DjangoOperator(BaseOperator):

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()

    def execute(self, context, **kwargs):
        try:
            self.try_execute(context, **kwargs)
            sentry_sdk.flush()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()
            raise


class DjangoSensorOperator(BaseSensorOperator):

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()


