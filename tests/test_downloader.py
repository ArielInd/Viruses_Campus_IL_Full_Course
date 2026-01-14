import pytest
from unittest.mock import MagicMock, patch
from src.downloader import Downloader

@pytest.fixture
def mock_playwright_all(mocker):
    # Mock sync_playwright
    mock_p_factory = mocker.patch("src.downloader.sync_playwright")
    mock_p_instance = MagicMock()
    mock_p_factory.return_value.start.return_value = mock_p_instance
    
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_p_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    return {
        "p": mock_p_instance,
        "browser": mock_browser,
        "context": mock_context,
        "page": mock_page
    }

def test_login_success(mock_playwright_all):
    """Verify that login method interacts with the correct selectors."""
    downloader = Downloader(username="user", password="pass")
    downloader.login()
    
    page = mock_playwright_all["page"]
    page.goto.assert_any_call("https://app.campus.gov.il/authn/login")
    page.fill.assert_any_call("#emailOrUsername", "user")
    page.fill.assert_any_call("#password", "pass")
    page.click.assert_any_call("#sign-in")

def test_start_stop(mock_playwright_all):
    """Verify start and stop methods."""
    downloader = Downloader(username="user", password="pass")
    downloader.start()
    assert downloader.browser is not None
    assert downloader.page is not None
    
    downloader.stop()
    mock_playwright_all["browser"].close.assert_called_once()
    mock_playwright_all["p"].stop.assert_called_once()

def test_stop_no_browser():
    """Verify stop doesn't crash if browser was never started."""
    downloader = Downloader(username="user", password="pass")
    downloader.stop() # Should not raise

def test_navigate_to_course(mock_playwright_all):
    """Verify navigation to course URL."""
    downloader = Downloader(username="user", password="pass")
    downloader.page = mock_playwright_all["page"]
    
    with patch("src.downloader.config") as mock_config:
        mock_config.COURSE_URL = "https://campus.gov.il/course/test"
        downloader.navigate_to_course()
        mock_playwright_all["page"].goto.assert_called_with("https://campus.gov.il/course/test")

def test_navigate_to_course_no_page(mock_playwright_all):
    """Verify navigate_to_course starts browser if page is None."""
    downloader = Downloader(username="user", password="pass")
    
    with patch("src.downloader.config") as mock_config:
        mock_config.COURSE_URL = "https://campus.gov.il/course/test"
        downloader.navigate_to_course()
        assert downloader.page is not None
        mock_playwright_all["page"].goto.assert_called_with("https://campus.gov.il/course/test")

def test_is_logged_in_true(mock_playwright_all):
    """Verify is_logged_in returns True when user icon is present."""
    downloader = Downloader(username="user", password="pass")
    downloader.page = mock_playwright_all["page"]
    
    mock_playwright_all["page"].query_selector.return_value = MagicMock()
    
    assert downloader.is_logged_in() is True

def test_is_logged_in_false(mock_playwright_all):
    """Verify is_logged_in returns False when user icon is missing."""
    downloader = Downloader(username="user", password="pass")
    downloader.page = mock_playwright_all["page"]
    
    mock_playwright_all["page"].query_selector.return_value = None
    
    assert downloader.is_logged_in() is False

def test_is_logged_in_no_page():
    """Verify is_logged_in returns False when page is None."""
    downloader = Downloader(username="user", password="pass")
    assert downloader.is_logged_in() is False
