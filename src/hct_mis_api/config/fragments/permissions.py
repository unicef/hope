from uuid import uuid4

from hct_mis_api.config.env import env

AA_PERMISSION_HANDLER = 3

HIJACK_PERMISSION_CHECK = "hct_mis_api.apps.utils.security.can_hijack"

ROOT_TOKEN = env.str("ROOT_ACCESS_TOKEN", uuid4().hex)
