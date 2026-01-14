import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError
from src.config import Config

def test_config_validation_missing_env():
    """Verify that config raises an error if required env vars are missing."""
    # Clear env vars and prevent reading .env file
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError):
            Config(_env_file=None)

def test_config_loading():
    """Verify that config loads values correctly from env vars."""
    mock_env = {
        "CAMPUS_IL_USERNAME": "testuser",
        "CAMPUS_IL_PASSWORD": "testpassword",
        "COURSE_URL": "https://campus.gov.il/course/test"
    }
    with patch.dict(os.environ, mock_env, clear=True):
        # Env vars should take precedence over .env file
        cfg = Config()
        assert cfg.USERNAME == "testuser"
        assert cfg.PASSWORD == "testpassword"
        assert cfg.COURSE_URL == "https://campus.gov.il/course/test"
