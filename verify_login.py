from src.downloader import Downloader
from src.config import config

# WARNING: This will launch a real browser (if headless=False) 
# and attempt to log in using the credentials in your .env
downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)
try:
    print("Attempting login...")
    downloader.login()
    print(f"✅ Login completed. Redirected to: {downloader.page.url}")
    
    print("Navigating to course...")
    downloader.navigate_to_course()
    print(f"✅ Navigated to: {downloader.page.url}")
    
    if downloader.is_logged_in():
        print("✅ Login successful!")
    else:
        print("❌ Login verification failed")
except Exception as e:
    print(f"❌ An error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    downloader.stop()
