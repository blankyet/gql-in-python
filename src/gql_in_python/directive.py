from .field import Field

class Directive(Field):
    def __init__(self, name, arguments = None, fields = None, parent = None):
        if name[0] != "@":
            name = "@" + name
        super().__init__(name, arguments, fields)
    
    