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

FILE = "https://raw.githubusercontent.com/unicef/hope/develop/backend/hct_mis_api/config/env.py"
res = requests.get(FILE)
buf = StringIO(res.text)
execCode = compile(res.text, "mulstring", "exec")
exec(execCode)
for k, v in DEFAULTS.items():
    TERMS[k] = MASK.format(name=k, type=v[0], default=v[1])

for term in sorted(TERMS.keys()):
    TABLE.append(TERMS[term])


with mkdocs_gen_files.open(index, "w") as f:
    f.writelines("\n".join(TABLE))
mkdocs_gen_files.set_edit_path(index, "build_glossary.py")
