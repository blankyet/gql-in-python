from collections import UserDict
from typing import Any
from .types import FieldEnum, Variable, FieldString
from .list import FieldList

class FieldArguments(UserDict[Any, Any]):
    """helper class to represent nested dict with {} curly brakets

    elements_params = FieldArguments({
            'filter': {
                'updated': {
                    'from': from_,
                    'to': to,
                },
                'types': types,
            }
    })

    casts str to FieldString or FieldEnum if upper()
    casts list to FieldList
    casts dict to FieldArguments
    None values are ignored

    str(elements_params) => {filter: {updated: {from: 0, to: 0}, types: [MOVIES, SERIES]}}
    """

    def __setitem__(self, key, value) -> None:
        if isinstance(value, dict):
            value = FieldArguments(value)
        elif isinstance(value, list):
            value = FieldList(value)

        elif isinstance(value, str):
            if value.isupper():
                value = FieldEnum(value)
            elif value.startswith("$"):
                value = Variable(value) # Strip $ and wrap
            else:
                value = FieldString(value)
        elif value is None:
            return None

        return super().__setitem__(key, value)

    def __repr__(self) -> str:
        params = ", ".join([f"{param}: {value}" for param, value in self.items()])
        return f"{{{params}}}"

    def compile(self) -> str:
        params = ", ".join([f"{param}: {value}" for param, value in self.items()])
        return str(params)

