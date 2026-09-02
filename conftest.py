import sys
import os

# Add platform_app/ to sys.path so `from server.*` imports work in tests
platform_dir = os.path.join(os.path.dirname(__file__), "platform_app")
if platform_dir not in sys.path:
    sys.path.insert(0, platform_dir)
