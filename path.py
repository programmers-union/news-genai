import os
from pathlib import Path

save_dir="uploads"
base_dir = Path.cwd()  # Get script directory
new_path = os.path.join(base_dir, save_dir)

print(new_path)