from pathlib import Path

import mkdocs_gen_files
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

PAT = '<a id="{id}" href="../{url}">{title}</a> | {description}'

config = mkdocs_gen_files.config

docs_dir = config["docs_dir"]
glossary_dir = "glossary"
terms_dir = Path(docs_dir) / f"{glossary_dir}/terms"
index = "glossary/index.md"

TABLE = []
TABLE.append("# Glossary")
TABLE.append("")
TABLE.append("Term | Definition")
TABLE.append("-----|-----------")

TERMS = {}

for filename in terms_dir.iterdir():
    if filename.is_dir():
        continue
    if filename.stem.startswith("."):
        continue
    fl = File(str(filename.relative_to(docs_dir)), config.docs_dir, config.site_dir, config.use_directory_urls)
    pg = Page(None, fl, config)
    pg.read_source(config)
    pg.render(config, Files([]))
    if pg.meta.get("template", "") != "term.html":
        raise Exception(f"File {filename} does not have a template meta descriptor")
    for t in pg.toc.items:
        LINE = PAT.format(
            id=filename.stem,
            title=t.title,
            url=f"{pg.url}{t.url}",
            description=pg.meta.get("description", "").strip() or "&lt; missing &gt;",
        )
        TERMS[t.title] = LINE

TABLE += [TERMS[term] for term in sorted(TERMS.keys())]

with mkdocs_gen_files.open(index, "w") as f:
    f.writelines("\n".join(TABLE))
#
# with mkdocs_gen_files.open(index, "w") as f:
#     for term in sorted(TERMS.keys()):
#         f.write(f"{TERMS[term]}")

mkdocs_gen_files.set_edit_path(index, "build_glossary.py")
