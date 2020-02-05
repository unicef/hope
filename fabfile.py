from __future__ import unicode_literals
from fabric.api import local




def fakedata():
    """
    Create mock data for the django backend.
    """
    local('docker-compose exec backend python manage.py loadbusinessareas')
    local('docker-compose exec backend python manage.py generatefixtures')


def init():
    """
    Reset db, migrate and generate fixtures.
    Useful when changing branch with different migrations.
    """
    local('docker-compose exec backend python manage.py reset_db')
    local('docker-compose exec backend python manage.py migrate')
    fakedata()
