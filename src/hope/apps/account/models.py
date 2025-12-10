"""The file is required so that Django recognizes our custom User model.

and other models that belong to the "account" app.

Why do we need this?
--------------------
Django expects every app listed in INSTALLED_APPS to have either:
  - a `models.py` file, OR
  - a `models/` package with an __init__.py

When Django runs migrations or loads AUTH_USER_MODEL ("account.User"),
it imports `account.models`. If this file does not import the actual
User model, Django cannot find it, and you'll get:

    django.core.exceptions.ImproperlyConfigured:
    AUTH_USER_MODEL refers to model 'account.User'
    that has not been installed

Even though we keep our models in a shared folder (`hope/models/`),
this "bridge file" ensures Django can still discover them correctly
under the `account` app label.

Example:
-------
- Actual model code lives in `hope/models/user.py`
- This file imports `User` so Django knows
  `account.User` exists for AUTH_USER_MODEL.

"""

from hope.models.user import User  # noqa: F401
