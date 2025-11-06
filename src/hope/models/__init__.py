import importlib
import inspect
import pathlib
import sys

from django.db import models as dj_models

models_dir = pathlib.Path(__file__).parent
package = __package__

for path in sorted(models_dir.glob("*.py")):
    if path.name == "__init__.py":
        continue

    module_name = f"{package}.{path.stem}"
    module = importlib.import_module(module_name)

    # --- Export Django model classes ---
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, dj_models.Model) and obj is not dj_models.Model and obj.__module__ == module_name:
            setattr(sys.modules[package], name, obj)

    # --- Export top-level constants like MALE, FEMALE... etc ---
    for name, value in module.__dict__.items():
        if name.isupper():
            setattr(sys.modules[package], name, value)

    # --- Export functions like build_summary()... etc ---
    for name, func in inspect.getmembers(module, inspect.isfunction):
        # Only export functions defined *in* this module (not imported ones)
        if func.__module__ == module_name:
            setattr(sys.modules[package], name, func)
