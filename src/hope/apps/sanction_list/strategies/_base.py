from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class BaseSanctionList:
    def __init__(self, context: "SanctionList") -> None:
        self.context = context

    def refresh(self) -> None:
        raise NotImplementedError()
