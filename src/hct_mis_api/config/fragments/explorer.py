EXPLORER_CONNECTIONS = {
    "default": "default",
}
EXPLORER_DEFAULT_CONNECTION = "default"
EXPLORER_PERMISSION_VIEW = lambda r: r.user.has_perm("explorer.view_query")
EXPLORER_PERMISSION_CHANGE = lambda r: r.user.has_perm("explorer.change_query")
