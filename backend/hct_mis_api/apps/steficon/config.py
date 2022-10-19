"""
Settings for Steficon namespaced in the STEFICON setting.
For example your project's `settings.py` file might look like this:
STEFICON = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}
This module provides the `api_setting` object, that is used to access
REST framework settings, checking for user settings first, then falling
back to the defaults.
"""
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

SAFETY_NONE = 0  # accept any value
SAFETY_STANDARD = 2  # only accept promitives
SAFETY_HIGH = 4  # only accept json values

DEFAULTS = {
    "USE_BLACK": False,
    "BUILTIN_MODULES": [
        "random",
        "datetime",
        "dateutil",
        "dateutil.relativedelta",
    ],
    "RESULT": "hct_mis_api.apps.steficon.result.Score",
    "USED_BY": None,
    "SAFETY_LEVEL": SAFETY_HIGH,
}


class Config:
    def __init__(self, user_settings: Optional[Dict] = None, defaults: Optional[Dict] = None) -> None:
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self) -> Dict:
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "STEFICON", {})
        return self._user_settings

    def __getattr__(self, attr: Any) -> Any:
        if attr not in self.defaults:
            raise AttributeError("Invalid STEFICON setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        if attr in "RESULT":
            val = import_string(val)
        elif attr in "USED_BY" and val:
            val = import_string(val)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self) -> None:
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


config = Config(None, DEFAULTS)


def reload_config(*args: List, **kwargs: Dict[Any, str]) -> None:
    setting: str = kwargs["setting"]
    if setting == "STEFICON":
        config.reload()


setting_changed.connect(reload_config)
