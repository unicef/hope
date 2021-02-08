import os
import sys
from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
from sentry_sdk import capture_exception, Hub, capture_message


def setup_django_for_airflow():
    sys.path.append('/usr/local/airflow/backend/')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hct_mis_api.settings")

    import django
    django.setup()


class DjangoOperator(BaseOperator):

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()

    def execute(self, context, **kwargs):
        print(Hub.current)
        capture_message('Something went wrong')
        # try:
        self.try_execute(context, **kwargs)
        # except Exception as e:
        #     print(Hub.current)
        #     capture_exception(e)
        #     raise


class DjangoSensorOperator(BaseSensorOperator):

    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()


