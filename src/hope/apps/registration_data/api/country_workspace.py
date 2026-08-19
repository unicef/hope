from hope.apps.core.api.mixins import BaseAPI


class CountryWorkspaceAPI(BaseAPI):
    """Outbound client for the per-request signed callback to Country Workspace.

    The base URL is not static config — it is the signed ``callback_url`` supplied
    per reset request and passed as ``api_url`` to the constructor. Auth travels in
    the signed URL itself, so no ``Authorization`` header and no settings key.
    """

    API_URL_SETTING_NAME = ""  # no static base — URL comes from the reset body
    API_KEY_SETTING_NAME = ""  # signed URL carries its own auth — no token
    API_AUTHENTICATION_REQUIRED = False  # no Authorization header; signature is in the URL

    class CountryWorkspaceAPIError(Exception):
        pass

    API_EXCEPTION_CLASS = CountryWorkspaceAPIError

    def notify_rdi_deleted(self, signed_token: str) -> None:
        """Success-only ping — POST the signed token to the callback_url (== self.api_url)."""
        self._post(self.api_url, data={"signed_token": signed_token})
