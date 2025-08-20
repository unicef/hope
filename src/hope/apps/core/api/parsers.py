from typing import IO, Any, Mapping

from nested_multipart_parser.drf import NestedParser
from rest_framework.exceptions import ParseError
from rest_framework.parsers import DataAndFiles, MultiPartParser


class DictDrfNestedParser(MultiPartParser):
    def parse(
        self,
        stream: IO,
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> DataAndFiles:
        clsDataAndFile = super().parse(stream, media_type, parser_context)

        data = clsDataAndFile.data.dict()
        data.update(clsDataAndFile.files.dict())  # add files to data

        parser = NestedParser(data)
        if parser.is_valid():
            return parser.validate_data.dict()
        raise ParseError(parser.errors)
