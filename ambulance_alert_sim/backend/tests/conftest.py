import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
src_dir = os.path.join(backend_dir, "src")

for p in [src_dir, backend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)
