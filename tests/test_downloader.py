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
    page.goto.assert_any_call("https://campus.gov.il/login/")
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
