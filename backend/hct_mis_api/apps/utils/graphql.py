from graphql import ResolveInfo
from graphql.language.ast import SelectionSet


def does_path_exist_in_query(path: str, info: ResolveInfo) -> bool:
    def does_path_exist_in_selection(_path: str, selection_set: SelectionSet) -> bool:
        if "." not in _path:
            return _path in (field.name.value for field in selection_set.selections)
        left, right = _path.split(".", 1)
        for field in selection_set.selections:
            if field.name.value == left:
                return does_path_exist_in_selection(right, field.selection_set)
        return False

    # TODO: Argument 2 to "does_path_exist_in_selection" has incompatible type "Optional[SelectionSet]"; expected "SelectionSet"
    return does_path_exist_in_selection(path, info.field_asts[0].selection_set)  # type: ignore
