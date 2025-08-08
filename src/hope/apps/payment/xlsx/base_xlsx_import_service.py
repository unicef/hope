class XlsxImportBaseService:
    TYPES_READABLE_MAPPING = {
        "s": "text",
        "n": "number",
        "f": "formula",
        "b": "bool",
        "inlineStr": "inlineStr",
        "e": "error",
        "str": "text",
    }
