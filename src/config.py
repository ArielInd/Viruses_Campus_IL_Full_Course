import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self._username = os.getenv("CAMPUS_IL_USERNAME")
        self._password = os.getenv("CAMPUS_IL_PASSWORD")
        self._course_url = os.getenv("COURSE_URL")

    @property
    def USERNAME(self):
        return self._username

    @property
    def PASSWORD(self):
        return self._password

    @property
    def COURSE_URL(self):
        return self._course_url

    def validate(self):
        """Validate that all required environment variables are set."""
        required_vars = ["CAMPUS_IL_USERNAME", "CAMPUS_IL_PASSWORD", "COURSE_URL"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()
