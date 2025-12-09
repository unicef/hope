from typing import Any


class BaseParser:
    def parse(self, file_path):
        raise NotImplementedError("Subclasses must implement this method")

    def validate_file_structure(self) -> bool:
        raise NotImplementedError("Subclasses must implement this property")

    def errors(self) -> list[str]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def supported_file_types(self) -> list[str]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def households_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def individuals_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def individual_roles_in_households_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def accounts_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def documents_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")

    @property
    def identities_data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement this property")
