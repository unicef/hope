from hope.apps.core.api.mixins import BaseAPI


class CountryWorkspaceAPI(BaseAPI):
    API_URL_SETTING_NAME = ""  # no static base — URL comes from the reset request body
    API_KEY_SETTING_NAME = ""  # no HOPE-side key — CW's signed_token is echoed in the body
    API_AUTHENTICATION_REQUIRED = False  # no `Authorization` header; auth is the signed_token in the body

    class CountryWorkspaceAPIError(Exception):
        pass

    API_EXCEPTION_CLASS = CountryWorkspaceAPIError

    def notify_rdi_deleted(self, signed_token: str) -> None:
        """Success-only ping — POST the signed token to the callback_url (== self.api_url)."""
        self._post(self.api_url, data={"signed_token": signed_token})
