from django.http import HttpRequest

from hct_mis_api.settings.settings import DEBUG, MIDDLEWARE, INSTALLED_APPS

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    # DEBUG TOOLBAR
    def show_ddt(request: HttpRequest) -> None:  # pragma: no-cover
        from flags.state import flag_enabled

        return flag_enabled("DEVELOP_DEBUG_TOOLBAR", request=request)

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_ddt,
        "JQUERY_URL": "",
    }
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "flags.panels.FlagsPanel",
        "flags.panels.FlagChecksPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
