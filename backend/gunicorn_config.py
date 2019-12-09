import os

ENV = os.getenv('ENV')
IS_DEV = ENV == 'dev'
STDOUT_DESTINATION = '-'

reload = IS_DEV
errorlog = STDOUT_DESTINATION
accesslog = STDOUT_DESTINATION
capture_output = IS_DEV
bind = ':8000'
loglevel = 'debug' if IS_DEV else 'info'
workers = 1
disable_redirect_access_to_syslog = False
worker_class = 'gevent'
