"""Load sanction list XML fixtures straight into a parser.

Production fetches lists only through `load_from_url()`. Tests feed the same `parse()` a local
file from `tests/unit/apps/sanction_list/test_files/` instead.
"""

from pathlib import Path
from typing import Protocol
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

TEST_FILES = Path(__file__).resolve().parents[2] / "unit" / "apps" / "sanction_list" / "test_files"


class SanctionListParser(Protocol):
    def parse(self, root: Element) -> object: ...


def load_sanction_list_xml(parser: SanctionListParser, file_name: str) -> None:
    parser.parse(ElementTree.parse(TEST_FILES / file_name).getroot())
