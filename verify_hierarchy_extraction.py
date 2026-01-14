from src.downloader import Downloader
from src.config import config

print("Initializing downloader...")
downloader = Downloader(config.USERNAME, config.PASSWORD, headless=True)

try:
    print("Logging in...")
    downloader.login()
    
    print("\nExtracting course hierarchy...")
    hierarchy = downloader.get_course_hierarchy()
    
    print(f"\n{'='*60}")
    print("COURSE HIERARCHY EXTRACTION RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Total Modules: {len(hierarchy)}")
    print(f"Total Units: {sum(len(m['units']) for m in hierarchy)}\n")
    
    for module in hierarchy:
        print(f"\nModule {module['index']}: {module['title']}")
        print(f"  Units: {len(module['units'])}")
        for unit in module['units'][:3]:  # Show first 3 units
            print(f"    {unit['index']}. {unit['title']}")
            print(f"       URL: {unit['url'][:80]}...")
        if len(module['units']) > 3:
            print(f"    ... and {len(module['units']) - 3} more units")
    
    print(f"\n{'='*60}")
    
    if len(hierarchy) > 0 and sum(len(m['units']) for m in hierarchy) > 0:
        print("✅ Hierarchy extraction successful!")
    else:
        print("❌ Hierarchy extraction failed - no modules or units found")
        
except Exception as e:
    print(f"❌ An error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    downloader.stop()
