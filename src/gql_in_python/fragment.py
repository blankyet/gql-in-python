from .list import FieldNames


class Fragment:
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.fields = None

    def __getitem__(self, selections):
        if not isinstance(selections, (tuple, list)):
            selections = [selections]
        self.fields = FieldNames(selections)
        return self

    def __repr__(self):
        return f"...{self.name}"

    def definition(self):
        return f"fragment {self.name} on {self.type_name} {{{self.fields}}}"
    