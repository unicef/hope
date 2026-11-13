import pytest

from extras.test_utils.factories import UserFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import User

pytestmark = pytest.mark.django_db()

ADMIN_URL = "/api/unicorn/"
NORMAL_USERNAME = "normal_user"
NORMAL_PASSWORD = "normal_password"

USERNAME_INPUT = "#id_username"
PASSWORD_INPUT = "#id_password"
LOGIN_BUTTON = '#login-form input[type="submit"]'
CONTENT_MAIN = "#content-main"
ERROR_NOTE = ".errornote"
LOGOUT_BUTTON = "#logout-form button"

INVALID_CREDENTIALS_ERROR = (
    "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
)


@pytest.fixture
def normal_user() -> User:
    user = UserFactory(is_superuser=False, is_staff=True, username=NORMAL_USERNAME, email="normal@user.com")
    user.set_password(NORMAL_PASSWORD)
    user.save()
    return user


def submit_admin_login(browser: HopeTestBrowser, username: str, password: str) -> None:
    browser.open(ADMIN_URL)
    browser.type(USERNAME_INPUT, username)
    browser.type(PASSWORD_INPUT, password)
    browser.click(LOGIN_BUTTON)


@pytest.mark.parametrize(
    ("username", "password", "expected_text"),
    [
        pytest.param("superuser", "testtest2", "Permissions", id="superuser"),
        pytest.param(
            NORMAL_USERNAME,
            NORMAL_PASSWORD,
            "You don't have permission to view or edit anything.",
            id="staff-without-permissions",
        ),
    ],
)
def test_admin_login(
    browser: HopeTestBrowser, normal_user: User, username: str, password: str, expected_text: str
) -> None:
    submit_admin_login(browser, username, password)

    browser.assert_text(expected_text, CONTENT_MAIN)


@pytest.mark.parametrize(
    ("username", "password"),
    [
        pytest.param(NORMAL_USERNAME, "wrong", id="invalid-password"),
        pytest.param("wrong", NORMAL_PASSWORD, id="invalid-username"),
        pytest.param("wrong", "wrong123123312", id="invalid-username-and-password"),
    ],
)
def test_admin_login_with_invalid_credentials_shows_error(
    browser: HopeTestBrowser, normal_user: User, username: str, password: str
) -> None:
    submit_admin_login(browser, username, password)

    browser.assert_text(INVALID_CREDENTIALS_ERROR, ERROR_NOTE)


def test_anonymous_user_sees_login_page(browser: HopeTestBrowser) -> None:
    browser.open("/")

    browser.assert_text("Login via Active Directory", "#root")


def test_log_out_via_admin_panel(login: HopeTestBrowser) -> None:
    login.open(ADMIN_URL)
    login.click(LOGOUT_BUTTON)

    login.assert_text("Logged out", "#content")
