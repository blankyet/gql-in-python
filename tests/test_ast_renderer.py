from gql_in_python.ast_renderer import gql


class TestGqlDecorator:
    """Test suite for the gql decorator."""

    def test_simple_field_query(self):
        """Test a simple field query."""
        @gql
        def query():
            user()

        result = str(query())
        assert "query query  { user }" == result

    def test_field_with_argument(self):
        """Test field with an argument."""
        @gql
        def TestQuery():
            user(id=123)

        result = str(TestQuery())
        assert "query TestQuery  { user(id: 123) }" == result

    def test_field_with_subselection(self):
        """Test field with subselection using set literal."""
        @gql
        def TestQuery():
            user()
            {
                name,
                email
            }
        result = str(TestQuery())
        assert "query TestQuery  { user { name email } }" == result

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
        assert 'query TestQuery  { pokemon(name: "pokemon") { classification name id } }' == result

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
        assert 'subscription PokemonsSub  { pokemon(name: {_in: "pokemon"}) { classification name id } }' == result


    def test_hero_with_fragment(self):
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

        assert """
query HeroComparison  { leftComparison: hero(episode: EMPIRE) { ...comparisonFields } rightComparison: hero(episode: JEDI) { ...comparisonFields } }
fragment comparisonFields on Character { name friendsConnection(first: 1) { totalCount edges { node { name } } } }
        """.strip() == result.strip()
