# without this line I got
# File "/app/.venv/lib/python3.13/site-packages/explorer/models.py", line 11, in <module>
#  from explorer.utils import (
#  ...<2 lines>...
#  )
#  File "/app/.venv/lib/python3.13/site-packages/explorer/utils.py", line 6, in <module>
#       from django.contrib.auth.forms import AuthenticationForm
#     File "/app/.venv/lib/python3.13/site-packages/django/contrib/auth/forms.py", line 21, in <module>
#       UserModel = get_user_model()
#     File "/app/.venv/lib/python3.13/site-packages/django/contrib/auth/__init__.py", line 164, in get_user_model
#      raise ImproperlyConfigured(
#           "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
#      )
#   django.core.exceptions.ImproperlyConfigured: AUTH_USER_MODEL refers to model 'account.User' that has not been installed
