
from collections import UserList


class FieldList(UserList):
    sep = ", "
    around = "[]"

    def __init__(self, initlist=None):
        super().__init__()
        if initlist:
            for item in initlist:
                # The "Cheat": If we see a dict, treat it as {alias: Field}
                if isinstance(item, dict):
                    for alias, field in item.items():
                        # Ensure we are working with a Field-like object
                        if hasattr(field, 'name'):
                            field.label = alias
                            self.data.append(field)
                else:
                    self.data.append(item)

    def __repr__(self) -> str:
        # Use str(item) to trigger the custom Field/Raw representations
        sequence_str = self.sep.join([str(item) for item in self.data])
        return f"{self.around[0]}{sequence_str}{self.around[1]}"
    

class FieldNames(FieldList):
    sep = " "
    around = "  "
    # str([id, updated]) => "id updated"

