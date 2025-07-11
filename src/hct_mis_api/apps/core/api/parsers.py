from typing import IO

from nested_multipart_parser.drf import NestedParser
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser


class DictDrfNestedParser(MultiPartParser):
    def parse(self, stream: IO, media_type: str | None = None, parser_context: dict | None = None) -> dict:
        clsDataAndFile = super().parse(stream, media_type, parser_context)

        data = clsDataAndFile.data.dict()
        data.update(clsDataAndFile.files.dict())  # add files to data

        parser = NestedParser(data)
        if parser.is_valid():
            return parser.validate_data.dict()
        raise ParseError(parser.errors)
