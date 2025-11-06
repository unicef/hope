import importlib
import inspect
import pathlib
import sys

models_dir = pathlib.Path(__file__).parent

for path in models_dir.glob("*.py"):
    if path.name == "__init__.py":
        continue

    module_name = f"{__package__}.{path.stem}"
    module = importlib.import_module(module_name)

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__ == module_name:
            setattr(sys.modules[__package__], name, obj)
