from hope.config.env import env
from hope.config.settings import ALLOWED_HOSTS, DEBUG, FRONTEND_HOST

# Content-Security-Policy (django-csp).
#
# django-csp >= 4.0 only honors the CONTENT_SECURITY_POLICY dict format; the
# legacy CSP_* top-level settings are no longer read by the middleware and only
# trigger the csp.E001 system check. The CSP_* env vars below stay configurable.
#
# `'unsafe-inline'` / `'unsafe-eval'` are still required by the bundled
# admin/editor assets. Migrating away from them (nonces / hashes, strict CSP)
# must be done incrementally; start with CONTENT_SECURITY_POLICY in "report-only"
# mode and monitor before enforcing a stricter policy, see
# https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
_report_only = env("CSP_REPORT_ONLY")
_report_percentage = env("CSP_REPORT_PERCENTAGE")

default_src: tuple[str, ...] = env.tuple("CSP_DEFAULT_SRC")
frame_ancestors: tuple[str, ...] = env.tuple("CSP_FRAME_ANCESTORS")
style_src: tuple[str, ...] = env.tuple("CSP_STYLE_SRC")
manifest_src: tuple[str, ...] = env.tuple("CSP_MANIFEST_SRC")
script_src: tuple[str, ...] = env.tuple("CSP_SCRIPT_SRC")
img_src: tuple[str, ...] = env.tuple("CSP_IMG_SRC")
font_src: tuple[str, ...] = env.tuple("CSP_FONT_SRC")
media_src: tuple[str, ...] = env.tuple("CSP_MEDIA_SRC")
connect_src: tuple[str, ...] = env.tuple("CSP_CONNECT_SRC")

if DEBUG:
    connect_src += (FRONTEND_HOST,)
    font_src += (FRONTEND_HOST,)
    img_src += (FRONTEND_HOST,)
    script_src += (FRONTEND_HOST,)
    style_src += (FRONTEND_HOST,)
    manifest_src += (FRONTEND_HOST,)

    ALLOWED_HOSTS.extend(["backend", "localhost", "127.0.0.1", "10.0.2.2", env("DOMAIN")])

_directives = {
    "default-src": default_src,
    "frame-ancestors": frame_ancestors,
    "style-src": style_src,
    "manifest-src": manifest_src,
    "script-src": script_src,
    "img-src": img_src,
    "font-src": font_src,
    "media-src": media_src,
    "connect-src": connect_src,
    "frame-src": ["'self'"],
    "object-src": ["'none'"],
    "base-uri": ["'self'"],
    "worker-src": ["'self'", "blob:"],
}
_report_uri = tuple(uri for uri in env.tuple("CSP_REPORT_URI") if uri)
if _report_uri:
    _directives["report-uri"] = _report_uri

if _report_only:
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {
        "DIRECTIVES": _directives,
        "REPORT_PERCENTAGE": _report_percentage * 100,
    }
else:
    CONTENT_SECURITY_POLICY = {
        "DIRECTIVES": _directives,
        "REPORT_PERCENTAGE": _report_percentage * 100,
    }
