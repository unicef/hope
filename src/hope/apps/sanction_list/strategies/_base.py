from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope.models.sanction_list import SanctionList


class BaseSanctionList:
    def __init__(self, context: "SanctionList") -> None:
        self.context = context

    def refresh(self) -> None:
        raise NotImplementedError()
