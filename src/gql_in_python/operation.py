
from .types import Variable
from .field import Field


class Operation:
    def __init__(self, root_name, operation_name = None, operation_type = "query", vars = None) -> None:
        self.operation_type = operation_type or "query"
        self.operation_name = operation_name or root_name
        self.root = Field(root_name, None, None)
        self.arguments = None
        self.fields = None
        self.fragments = None
        self.vars = vars or {} # {"id": "ID!"}

    def __call__(self, args_dict=None, **arguments: dict) -> "Field":
        final_args = {**(args_dict or {}), **arguments}
        self.root(final_args)
        return self

    def __getitem__(self, fields: list) -> "Field":
        self.root[fields]
        return self

    def __repr__(self) -> str:
        # Build header: query Hero($id: ID!)
        var_defs = ", ".join(
            [Variable(k).define(v) for k, v in self.vars.items()]
        )
        header_args = f"({var_defs})" if var_defs else ""

        query = f"{self.operation_type} {self.operation_name}{header_args} {self.root}"

        fragments = self.fragments or self.root._find_fragments(self.root)
        frag_defs = "\n".join([f.definition() for f in fragments])
        
        return f"{query}\n{frag_defs}".strip()


    