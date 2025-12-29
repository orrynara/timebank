
import sys
import os

# 현재 디렉토리를 sys.path에 추가하여 모듈 인식 가능하게 함
sys.path.append(os.getcwd())

print("Attempting to import ui.home.main...")
try:
    from ui.home import main
    print("SUCCESS: Successfully imported 'main' from 'ui.home'")
except ImportError as e:
    print(f"ERROR: Failed to import 'main' from 'ui.home': {e}")
except Exception as e:
    print(f"ERROR: An unexpected error occurred during import: {e}")

print("Attempting to import sub-pages...")
try:
    import ui.booking
    import ui.products
    import ui.investor
    import ui.admin
    print("SUCCESS: Successfully imported all sub-page modules")
except ImportError as e:
    print(f"ERROR: Failed to import sub-pages: {e}")
