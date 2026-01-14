from src.downloader import Downloader
from src.config import config

print("Initializing downloader...")
downloader = Downloader(config.USERNAME, config.PASSWORD, headless=False)  # Non-headless to see what's happening

try:
    print("Logging in...")
    downloader.login()
    
    print("\nNavigating to course home...")
    learning_url = "https://app.campus.gov.il/learning/course/course-v1:TAU+ACD_RFP1_HowToBeatViruses_HE+2022_1/home"
    downloader.page.goto(learning_url)
    downloader.page.wait_for_load_state("networkidle")
    
    print("Waiting for page to load...")
    import time
    time.sleep(3)
    
    # Try to click expand all
    try:
        expand_button = downloader.page.query_selector("button:has-text('הרחב הכל'), button:has-text('Expand all')")
        if expand_button:
            print("Found expand button, clicking...")
            expand_button.click()
            time.sleep(2)
        else:
            print("No expand button found")
    except Exception as e:
        print(f"Error clicking expand: {e}")
    
    # Get page HTML to analyze
    print("\nGetting page content...")
    html_content = downloader.page.content()
    
    # Save to file for analysis
    with open("course_page_debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Saved page HTML to course_page_debug.html")
    
    # Try different selectors
    print("\nTrying different selectors:")
    
    selectors_to_try = [
        "ol.course-outline > li.outline-item",
        ".course-outline .outline-item",
        "li.outline-item",
        ".outline-item",
        ".section",
        ".chapter",
        "[class*='outline']",
        "[class*='section']",
    ]
    
    for selector in selectors_to_try:
        elements = downloader.page.query_selector_all(selector)
        print(f"  {selector}: {len(elements)} elements")
    
    print("\nPress Enter to close browser...")
    input()
    
except Exception as e:
    print(f"❌ An error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    downloader.stop()
