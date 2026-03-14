from gql_in_python.ast_renderer import gql
from graphql import parse


def validate_graphql(query: str) -> None:
    """Validate a GraphQL query is syntactically valid."""
    try:
        parse(query)
    except Exception as e:
        raise AssertionError(f"GraphQL parsing failed: {e}")


class TestGqlDecorator:
    """Test suite for the gql decorator."""

    def test_simple_field_query(self):
        """Test a simple field query."""
        @gql
        def TestQuery():
            user()

        result = str(TestQuery())
        expected = "query TestQuery {user}"
        assert expected == result
        validate_graphql(result)

    def test_field_with_argument(self):
        """Test field with an argument."""
        @gql
        def TestQuery():
            user(id=123)

        result = str(TestQuery())
        expected = "query TestQuery {user(id: 123)}"
        assert expected == result
        validate_graphql(result)

    def test_field_with_subselection(self):
        """Test field with subselection using set literal."""
        @gql
        def TestQuery():
            user,
            {
                name,
                email
            }
        result = str(TestQuery())
        expected = "query TestQuery {user { name email }}"
        assert expected == result
        validate_graphql(result)

    def test_query_explicit(self):
        @gql
        def TestQuery(Name: str):
            pokemon(name=Name)
            {
                classification,
                name,
                id,
            }
        
        result = str(TestQuery("pokemon"))
        expected = 'query TestQuery {pokemon(name: "pokemon") { classification name id }}'
        assert expected == result
        validate_graphql(result)

    def test_subscription_explicit(self):
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
        
        result = str(TestQuery("pokemon"))
        expected = 'subscription PokemonsSub {pokemon(name: {_in: "pokemon"}) { classification name id }}'
        assert expected == result
        validate_graphql(result)

    def test_hero_with_fragment(self):
        """Test hero comparison with fragments showcasing complex nested structures."""
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

        expected = """query HeroComparison { leftComparison: hero(episode: EMPIRE) { ...comparisonFields } rightComparison: hero(episode: JEDI) { ...comparisonFields } }
fragment comparisonFields on Character { name friendsConnection(first: 1) { totalCount edges { node { name } } } }"""
        assert expected == result.strip()
        validate_graphql(result)


    def test_directives(self):
        @gql
        def TestQuery(Name: str):
            subscription, PokemonsSub @ directive({where: none})
            {
                pokemon({name: {_in: Name}}),
                {
                    classification @skip({why: {_in: [1, 2]}}) @include, {
                        all
                    },
                    name,
                    id,
                }
            }
        
        result = str(TestQuery("pokemon"))
        expected = 'subscription  PokemonsSub @directive(where: none)  {pokemon(name: {_in: "pokemon"}) { classification @skip(why: {_in: [1, 2]}) @include { all } name id }}'
        assert expected == result
        validate_graphql(result)