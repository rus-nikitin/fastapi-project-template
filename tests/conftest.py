import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
app_dir = project_root / "src"
sys.path.insert(0, str(app_dir))
