from .fragment import Fragment
from .gql_list import FieldNames
from .field_arguments import FieldArguments


class Field:
    def __init__(self, name, arguments = None, fields = None):
        self.name = name
        self.arguments = FieldArguments(arguments)
        self.fields = FieldNames(fields)

    def __call__(self, args_dict=None, **arguments: dict) -> "Field":
        final_args = {**(args_dict or {}), **arguments}
        self.arguments = FieldArguments(final_args)
        return self

    def __getitem__(self, fields: list) -> "Field":
        self.fields = FieldNames(fields)
        return self
    
    def alias(self, alias) ->"Field":
        self.label = alias
        return self

    def _find_fragments(self, field_obj, found=None):
        if found is None:
            found = set()
        
        # Iterate through the FieldNames (UserList)
        for item in field_obj.fields:
            if isinstance(item, Fragment):
                found.add(item)
                # Recursively check the fragment's own fields
                self._find_fragments(item, found)
            elif isinstance(item, Field):
                # Recursively check nested fields
                self._find_fragments(item, found)
                
        return found

    def __repr__(self):
        # Handle Alias (label: name)
        display_name = f"{self.label}: {self.name}" if getattr(self, "label", None) else self.name
        
        if self.arguments and self.fields:
            return f"{display_name}({self.arguments.compile()}) {{{self.fields}}}"
        elif self.fields:
            return f"{display_name} {{{self.fields}}}"
        elif self.arguments:
            return f"{display_name}({self.arguments.compile()})"
        return display_name
        