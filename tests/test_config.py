import pytest
import os
from unittest.mock import patch
from src.config import config

def test_config_validation_missing_env():
    """Verify that config raises an error if required env vars are missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables"):
            config.validate()

def test_config_loading():
    """Verify that config loads values correctly."""
    mock_env = {
        "CAMPUS_IL_USERNAME": "testuser",
        "CAMPUS_IL_PASSWORD": "testpassword",
        "COURSE_URL": "https://campus.gov.il/course/test"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        config.validate()
        assert config.USERNAME == "testuser"
        assert config.PASSWORD == "testpassword"
        assert config.COURSE_URL == "https://campus.gov.il/course/test"