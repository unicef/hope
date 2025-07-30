import importlib
import pathlib

admin_dir = pathlib.Path(__file__).parent
for path in admin_dir.glob("*.py"):
    if path.name != "__init__.py":
        importlib.import_module(f"{__package__}.{path.stem}")
