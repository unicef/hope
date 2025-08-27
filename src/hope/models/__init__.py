import importlib
import pathlib

models_dir = pathlib.Path(__file__).parent
for path in models_dir.glob("*.py"):
    if path.name != "__init__.py":
        importlib.import_module(f"{__package__}.{path.stem}")

# __all__ = []
#
# models_dir = pathlib.Path(__file__).parent
# for path in models_dir.glob("*.py"):
#     if path.name == "__init__.py":
#         continue
#
#     module = importlib.import_module(f"{__package__}.{path.stem}")
#
#     # Loop through everything in the module
#     for attr_name in dir(module):
#         if attr_name.startswith("_"):
#             continue
#
#         attr = getattr(module, attr_name)
#         # Only pull classes (models will be classes)
#         globals()[attr_name] = attr
#         __all__.append(attr_name)
