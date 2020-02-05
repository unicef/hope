from __future__ import unicode_literals
from fabric.api import local
from fabric.context_managers import shell_env


def ssh(service):
    """
    ssh into running service container
    :param service: ['backend', 'frontend', 'proxy', 'db']
    """
    assert service in ['backend', 'frontend', 'proxy', 'db'], "%s is unrecognized service"
    local('docker-compose exec %s bash' % service)


def managepy(command=''):
    """
    Run specified manage.py command
    """
    cmd = 'docker-compose exec backend python manage.py {}'.format(command)
    local(cmd)


def fakedata(clean_before=True):
    """
    Create mock data for the django backend.
    """
    local('docker-compose exec backend python manage.py loadbusinessareas')
    local('docker-compose exec backend python manage.py generatefixtures')


def reset_db():
    """
    Reset db, migrate and generate fixtures.
    Useful when changing branch with different migrations.
    """
    local('docker-compose exec backend python manage.py reset_db')
    local('docker-compose exec backend python manage.py migrate')
    fakedata(clean_before=False)


def tests(test_path=''):
    """
    Run unit tests.
    """
    local('docker-compose exec backend python manage.py test {} --parallel --noinput'.format(test_path))


def remove_untagged_images():
    """
    Delete all untagged (<none>) images
    """
    local('docker rmi $(docker images | grep "^<none>" | awk "{print $3}")')


def lint():
    """
    Run python code linter
    """
    local('docker-compose exec backend flake8 ./ --count')


def clean_pyc():
    """
    Cleanup pyc files
    """
    local('docker-compose exec backend find . -name \'*.pyc\' -delete')


def compose():
    with shell_env(DOCKER_CLIENT_TIMEOUT='300', COMPOSE_HTTP_TIMEOUT='300'):
        local(
            'docker-compose stop '
            '&& '
            'docker-compose up --build --abort-on-container-exit --remove-orphans'
        )


def restart():
    with shell_env(DOCKER_CLIENT_TIMEOUT='300', COMPOSE_HTTP_TIMEOUT='300'):
        local(
            'docker-compose stop '
            '&& '
            'docker-compose up'
        )