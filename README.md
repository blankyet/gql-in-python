I tried to make GraphQL look like Python and...

<table>
<tr>
<th width="50%">Python</th>
<th width="50%">GraphQL</th>
</tr>
<tr>
<td>

```python
@gql
def TestQuery(Name: str):
    subscription, PokemonsSub,
    {
        pokemon({name: {_in: Name}}),
        {
            classification,
            name,
            id,
        }
    }

print(TestQuery("pokemon"))
```
</td>


<td>

``` GraphQL

subscription PokemonsSub {
  pokemon(name: {_in: "pokemon"}) {
    classification
    name
    id
  }
}
```
</td>
</tr>
</table>