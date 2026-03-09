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