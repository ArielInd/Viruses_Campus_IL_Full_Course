import importlib

def test_playwright_installed():
    """Verify that playwright is installed and importable."""
    spec = importlib.util.find_spec("playwright")
    assert spec is not None, "Playwright is not installed"

def test_dotenv_installed():
    """Verify that python-dotenv is installed and importable."""
    spec = importlib.util.find_spec("dotenv")
    assert spec is not None, "python-dotenv is not installed"

def test_src_package_importable():
    """Verify that the src package is importable."""
    spec = importlib.util.find_spec("src")
    assert spec is not None, "src package is not importable"
