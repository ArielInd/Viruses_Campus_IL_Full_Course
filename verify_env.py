from src.config import config
try:
    config.validate()
    print("✅ Environment configuration is valid.")
except Exception as e:
    print(f"❌ Verification failed: {e}")
