# conftest.py en la raíz del proyecto
import sys
from pathlib import Path

# Añade src al path de Python para todos los tests
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))