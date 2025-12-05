class BaseParser:
    def parse(self, file_path):
        raise NotImplementedError("Subclasses must implement this method")  # pragma: no cover

    def validate_file_structure(self) -> bool:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    def errors(self) -> [str]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def supported_file_types(self) -> [str]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def households_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def individuals_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def individual_roles_in_households_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def accounts_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def documents_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover

    @property
    def identities_data(self) -> [dict]:
        raise NotImplementedError("Subclasses must implement this property")  # pragma: no cover
