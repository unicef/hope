import importlib
import pathlib

models_dir = pathlib.Path(__file__).parent
for path in models_dir.glob("*.py"):
    if path.name != "__init__.py":
        importlib.import_module(f"{__package__}.{path.stem}")
