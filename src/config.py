import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @property
    def USERNAME(self):
        return os.getenv("CAMPUS_IL_USERNAME")

    @property
    def PASSWORD(self):
        return os.getenv("CAMPUS_IL_PASSWORD")

    @property
    def COURSE_URL(self):
        return os.getenv("COURSE_URL")

    def validate(self):
        """Validate that all required environment variables are set."""
        required_vars = ["CAMPUS_IL_USERNAME", "CAMPUS_IL_PASSWORD", "COURSE_URL"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()