from io import StringIO

import mkdocs_gen_files
import requests

MASK = """
### {name}

*Type:* `{type}`

*Default:* `{default}`

-----------

"""
DEFAULTS = {}
TABLE = []
TABLE.append("# Settings")
TABLE.append("")
TERMS = {}

index = "guide-adm/hope/settings.md"

FILE = "https://raw.githubusercontent.com/unicef/hope/develop/backend/hope/config/env.py"
res = requests.get(FILE)
buf = StringIO(res.text)
exec_code = compile(res.text, "mulstring", "exec")
exec(exec_code)
for k, v in DEFAULTS.items():
    TERMS[k] = MASK.format(name=k, type=v[0], default=v[1])

TABLE += [TERMS[term] for term in sorted(TERMS.keys())]


with mkdocs_gen_files.open(index, "w") as f:
    f.writelines("\n".join(TABLE))
mkdocs_gen_files.set_edit_path(index, "build_glossary.py")
