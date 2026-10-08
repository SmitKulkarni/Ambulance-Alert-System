import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
src_dir = os.path.join(backend_dir, "src")

for p in [project_root, backend_dir, src_dir]:
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
