import ast
import inspect
import textwrap
from gql_in_python.directive import Directive
from gql_in_python.fragment import Fragment
from gql_in_python.list import FieldNames
from gql_in_python.types import Variable
from gql_in_python.field import Field
from gql_in_python.operation import Operation


def gql(fn):

    def wrapper(*args, **kwargs):
        source = inspect.getsource(fn)
        sig = inspect.signature(fn)
        bound = sig.bind_partial(*args, **kwargs)
        
        # 2. Iterate through all defined parameters
        args_dict = {}
        variables  = {}
        for name, param in sig.parameters.items():
            # If user provided it, use it; otherwise, use your custom default
            if name in bound.arguments:
                args_dict[name] = bound.arguments[name]
            else:
                args_dict[name] = Variable(name)
                variables[name] = param.annotation

        source = "\n".join(line for line in source.splitlines() if "@gql" not in line)
        source = textwrap.dedent(source)
        tree = ast.parse(source)

        class GQLParser(ast.NodeVisitor):
            def visit_Name(self, node):
                if node.id in args_dict:
                    return args_dict[node.id]
                return Field(node.id)

            def visit_Expr(self, node):
                # This unwraps the line and returns the Field/Set result
                return self.visit(node.value)

            def visit_Call(self, node):
                field = Field(node.func.id)
                if len(node.args) > 0 and isinstance(node.args[0], ast.Dict):
                    field = field(self.visit(node.args[0]))
                else:
                    field= field({kw.arg: self.visit(kw.value) for kw in node.keywords})
                return field


            def visit_Tuple(self, node):
                return [self.visit(e) for e in node.elts]

            def visit_List(self, node):
                return [self.visit(e) for e in node.elts]

            def visit_Dict(self, node):
                # Dicts inside Calls are data; otherwise they are selections
                data = {
                    self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values)
                }
                return data
            
            def visit_BinOp(self, node):
                # left most is a field everythin else is a directive
                active_node = node
                directives = []
                while (isinstance(active_node.left, ast.BinOp)
                       and isinstance(active_node.left.op, ast.MatMult)):
                    field = self.visit(active_node.right)
                    directives.append(Directive(field.name, field.arguments, field.fields))
                    active_node = active_node.left
                
                field = self.visit(active_node.left)
                if (hasattr(active_node, "right")):
                    field_dir = self.visit(active_node.right)
                    directives.append(Directive(field_dir.name, field_dir.arguments, field_dir.fields))
            
                return [field, *directives[::-1]]


            def visit_Set(self, node):
                elements = node.elts
                results = []
                i = 0
                while i < len(elements):
                    current_val = self.visit(elements[i])

                    if current_val is Ellipsis:
                        if i + 1 < len(elements) and isinstance(elements[i + 1], ast.Name):
                            current_val = Fragment(name=self.visit(elements[i + 1]), type_name="")
                            i += 1
                    if isinstance(current_val, dict):
                        alias, field = next(iter(current_val.items()))
                        field.alias(alias.name)
                        current_val = field
                    if isinstance(current_val, list):
                        last = current_val.pop()
                        results.extend(current_val)
                        current_val = last
                    # Look ahead within the set for a nested block
                    if i + 1 < len(elements) and isinstance(elements[i + 1], ast.Set):
                        children = self.visit(elements[i + 1])

                        current_val[children]
                        i += 1  # Consume the nested set

                    results.append(current_val)
                    i += 1
                return results

            def visit_Constant(self, node):

                return node.value

        # target = tree.body[0].body[-1]
        # target_node = target.value if hasattr(target, "value") else target
        # result = GQLParser().visit(target_nodevisit)
        # return str(result[0] if isinstance(result, list) else result)
        body = tree.body[0].body
        results = []
        parser = GQLParser()

        operation = Operation(root_name="", operation_name=fn.__name__, operation_type="query")
        prev_op = operation
        fragments = []
        for i, node in enumerate(body):
            expr_res = parser.visit(node)
            
            if isinstance(expr_res, list) and str(expr_res[0]) in ["query", "mutation", "subscription"]:
                operation = Operation(root_name=None,
                        operation_name=FieldNames(expr_res[1]),
                        operation_type=expr_res[0] 
                    )
                prev_op = operation
            elif isinstance(expr_res, list) and str(expr_res[0]) == "fragment":
                fragment = Fragment(name=expr_res[1], type_name=expr_res[3])
                prev_op = fragment
                fragments.append(fragment)
            elif isinstance(expr_res, list) and isinstance(expr_res[0], Field):
                if prev_op is not None:
     
                    if isinstance(prev_op, Operation):
                        prev_op.root = expr_res[0]
                        prev_op = expr_res[0]
                    else:
                        prev_op[expr_res]
            elif isinstance(expr_res, Field):
                if isinstance(prev_op, Operation):
                    prev_op.root = expr_res
                    prev_op = expr_res
                else:
                    prev_op[expr_res]
            elif isinstance(expr_res[0], list):
                if isinstance(expr_res[0][0], Field):
                    if prev_op is not None:
                        prev_op[expr_res[0]]
            
        
        operation.vars = variables
        operation.fragments = fragments


        return str(operation)

    return wrapper


def transform_to_gql(query):
    import re
    query = re.sub(r'\b(\w+)\b(?![:(,)])', r'\1,', query)
    query = query.replace("}", "},")

    query = query.replace("(", "({")
    query = query.replace(")", "}),")

    return query