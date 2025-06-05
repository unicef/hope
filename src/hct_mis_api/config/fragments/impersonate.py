from hct_mis_api.config.settings import ADMIN_PANEL_URL

IMPERSONATE = {
    "REDIRECT_URL": f"/api/{ADMIN_PANEL_URL}/",
    "PAGINATE_COUNT": 50,
    "DISABLE_LOGGING": False,
}
