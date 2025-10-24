from hope.config.env import env
from hope.config.settings import ALLOWED_HOSTS, DEBUG, FRONTEND_HOST

CSP_REPORT_URI = env.tuple("CSP_REPORT_URI")
CSP_REPORT_ONLY = env("CSP_REPORT_ONLY")
CSP_REPORT_PERCENTAGE = env("CSP_REPORT_PERCENTAGE")

# default source as self
CSP_DEFAULT_SRC: tuple[str, ...] = env.tuple("CSP_DEFAULT_SRC")
CSP_FRAME_ANCESTORS: tuple[str, ...] = env.tuple("CSP_FRAME_ANCESTORS")
CSP_STYLE_SRC: tuple[str, ...] = env.tuple("CSP_STYLE_SRC")
CSP_MANIFEST_SRC: tuple[str, ...] = env.tuple("CSP_MANIFEST_SRC")
CSP_SCRIPT_SRC: tuple[str, ...] = env.tuple("CSP_SCRIPT_SRC")
CSP_IMG_SRC: tuple[str, ...] = env.tuple("CSP_IMG_SRC")
CSP_FONT_SRC: tuple[str, ...] = env.tuple("CSP_FONT_SRC")
CSP_MEDIA_SRC: tuple[str, ...] = env.tuple("CSP_MEDIA_SRC")
CSP_CONNECT_SRC: tuple[str, ...] = env.tuple("CSP_CONNECT_SRC")

if DEBUG:
    CSP_CONNECT_SRC += (FRONTEND_HOST,)
    CSP_FONT_SRC += (FRONTEND_HOST,)
    CSP_IMG_SRC += (FRONTEND_HOST,)
    CSP_SCRIPT_SRC += (FRONTEND_HOST,)
    CSP_STYLE_SRC += (FRONTEND_HOST,)
    CSP_MANIFEST_SRC += (FRONTEND_HOST,)

    ALLOWED_HOSTS.extend(["backend", "localhost", "127.0.0.1", "10.0.2.2", env("DOMAIN")])
