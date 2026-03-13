A small experiment that tries to make GraphQL queries look like valid Python by abusing operator overloading and AST transformations.

<table>
<tr>
<th width="50%">Python</th>
<th width="50%">GraphQL</th>
</tr>
<tr>
<td>

```python
@gql
def GetHero():
    hero, 
    {
        name,
        appearsIn,
    }

print(GetHero())
```
</td>


<td>

``` GraphQL

query GetHero {
  hero {
    name
    appearsIn
  }
}
```
</td>
</tr>
</table>

<table>
<tr>
<th width="50%">Python</th>
<th width="50%">GraphQL</th>
</tr>
<tr>
<td>

```python
@gql
def HeroComparison(First: "Int" = 3):
    {
        {leftComparison: hero(episode=EMPIRE)}, {
            ...,comparisonFields,
        },
        {rightComparison: hero(episode=JEDI)}, {
            ...,comparisonFields,
        }
    },

    fragment, comparisonFields, on, Character,

    {
        name,
        friendsConnection(first=First), {
            totalCount,
            edges, {
            node, {
                name
            },
            }
        }
    }

result = str(HeroComparison(1))
```
</td>


<td>

``` GraphQL

query HeroComparison {
  leftComparison: hero(episode: EMPIRE) {
    ...comparisonFields
  }
  rightComparison: hero(episode: JEDI) {
    ...comparisonFields
  }
}

fragment comparisonFields on Character {
  name
  friendsConnection(first: 1) {
    totalCount
    edges {
      node {
        name
      }
    }
  }
}
```
</td>
</tr>
</table>

The idea was simple.
I looked at GraphQL syntax and thought: these look like Python dicts and sets.

The first iteration looked like this.

Using operator overloading we can change the meaning of () and [] to represent GraphQL () and {}.

In `__call__` we pass a dict of arguments, which already looks like GraphQL arguments.

And  `__getitem__` represents the GraphQL selection block.

``` Python
elements = Operation("elements", "SelectElements", "query")

elements({"where": {"id": "UUID"}})[
    "ID",
    Field("Name")({"language": "EN"})
]

print(elements) # query SelectElements {elements(where: {id: UUID}) { ID Name }}

# Field class looks something like this

class Field:
    ...
    def __call__(self, args_dict=None, **arguments: dict) -> "Field":
        final_args = {**(args_dict or {}), **arguments}
        self.arguments = FieldArguments(final_args)
        return self

    def __getitem__(self, fields: list) -> "Field":
        self.fields = FieldNames(fields)
        return self
    ...
```

Honestly, this is about as good as it gets.
It represents GraphQL without f-strings.
Arguments can be passed at runtime and it is easy to test.
Looks nice.

But it is still closer to Python than to GraphQL. So I went further down the rabbit hole.

With one small class we can remove Field("Name") and also remove the need for quotes.

```
class Namespace:
    def __getattr__(self, name):
        return Field(name)
    
g = Namespace()

elem = g.elements({g.where: {g.id: g.UUID}})[
    g.ID,
    g.Name({g.language: g.EN})[g.all]
]
print(elem) # elements(where: {id: UUID}) { ID Name(language: EN) { all } }
```
Maybe this was the point where I should have stopped.
We are already very close to GraphQL.

But I really did not like the g. prefix.

So the last step was to completely ignore Python as a language and only use its AST.

The decorator does not execute the function.
Instead it transforms the function body into Operation and Field objects from the first example.

This is the closest I could get to copy-pasting a GraphQL query into Python.

``` python
@gql
def SelectElements():
    elements({where: {id: UUID}})
    {
        ID,
        Name({language: EN}), {
            all
        }
    }

print(SelectElements()) # query SelectElements {elements(where: {id: UUID}) { ID Name(language: EN) { all } }}
```
as you can see difference is very small
``` Graphql
{
  elements(where: { id: UUID }) {
    ID
    Name(language: EN) {
      all
    }
  }
}
```
I even tried adding a function that converts GraphQL into this Python syntax.
It basically adds commas after fields and changes () to ({}).

``` python
def transform_to_gql(query):
    query = re.sub(r'\b(\w+)\b(?![:(,)])', r'\1,', query)
    query = query.replace("}", "},")

    query = query.replace("(", "({")
    query = query.replace(")", "}),")

    return query
```
The library technically supports variables (both Python and GraphQL style) and fragments, but it still lacks many features.

Dont use it in production.

# todo:
- Add pretty-print
- Add directives support (@include, @skip)
- Refactor complex AST parsing logic
- transform_to_gql - only works with simple queries