# check_path.py
import sys
from PIL import ImageFont

print("--- PYTHON EXECUTABLE ---")
print(sys.executable)
print("-" * 25)

print("--- PYTHON SYS.PATH ---")
for path in sys.path:
    print(path)
print("-" * 25)

print("--- PIL.IMAGEFONT LOCATION ---")
try:
    print(ImageFont.__file__)
except Exception as e:
    print(f"Could not find ImageFont location: {e}")
print("-" * 25)