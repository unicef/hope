from hct_mis_api.config.settings import DEBUG, INSTALLED_APPS, IS_TEST, MIDDLEWARE

if DEBUG and not IS_TEST:
    from constance import config

    INSTALLED_APPS += ["debug_toolbar", "graphiql_debug_toolbar"]
    MIDDLEWARE.append("graphiql_debug_toolbar.middleware.DebugToolbarMiddleware")

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: config.SHOW_TOOLBAR,
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
