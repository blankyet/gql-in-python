from collections import UserString


class FieldString(UserString):
    def __str__(self) -> str:
        return f'"{self.data}"'

    def __repr__(self) -> str:
        return self.__str__()

class FieldEnum(UserString):
    ...

class Variable(UserString):
    def __str__(self):
        return f"${self.data}"

    def __repr__(self) -> str:
        return self.__str__()

    # For the header definition: id: String!
    def define(self, gql_type):
        return f"${self.data}: {gql_type}"
