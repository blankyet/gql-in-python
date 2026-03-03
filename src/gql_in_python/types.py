from collections import UserString


class FieldString(UserString):
    def __str__(self) -> str:
        return f'"{self.data}"'

    def __repr__(self) -> str:
        return self.__str__()

class FieldEnum(UserString):
    ...

class Variable(UserString):
    def __repr__(self):
        return f"${self}"

    # For the header definition: id: String!
    def define(self, gql_type):
        return f"${self}: {gql_type}"
