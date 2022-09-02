# import defaults
from importlib import import_module

from .base import *  # noqa: F403

overrides = import_module(f"hct_mis_api.settings.{ENV}")

# apply imported overrides
for attr in dir(overrides):
    # we only want to import settings (which have to be variables in ALLCAPS)
    if attr.isupper():
        # update our scope with the imported variables. We use globals() instead of locals()
        # because locals() is readonly and it returns a copy of itself upon assignment.
        globals()[attr] = getattr(overrides, attr)
