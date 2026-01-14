import pytest
import os
from unittest.mock import patch
from src.config import Config

def test_config_validation_missing_env():
    """Verify that config raises an error if required env vars are missing."""
    with patch.dict(os.environ, {}, clear=True):
        # Create a new Config instance to pick up the mocked environment
        test_config = Config()
        with pytest.raises(ValueError, match="Missing required environment variables"):
            test_config.validate()

def test_config_loading():
    """Verify that config loads values correctly."""
    mock_env = {
        "CAMPUS_IL_USERNAME": "testuser",
        "CAMPUS_IL_PASSWORD": "testpassword",
        "COURSE_URL": "https://campus.gov.il/course/test"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        # Create a new Config instance to pick up the mocked environment
        test_config = Config()
        test_config.validate()
        assert test_config.USERNAME == "testuser"
        assert test_config.PASSWORD == "testpassword"
        assert test_config.COURSE_URL == "https://campus.gov.il/course/test"