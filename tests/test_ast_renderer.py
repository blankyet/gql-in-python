from gql_in_python.ast_renderer import gql


class TestGqlDecorator:
    """Test suite for the gql decorator."""

    def test_simple_field_query(self):
        """Test a simple field query."""
        @gql
        def query():
            user()

        result = str(query())
        assert "user" in result

    def test_field_with_argument(self):
        """Test field with an argument."""
        @gql
        def query():
            user(id=123)

        result = str(query())
        assert "user" in result
        assert "id: 123" in result

    def test_field_with_subselection(self):
        """Test field with subselection using set literal."""
        @gql
        def query():
            user(),
            {
                name,
             email}


    def test_query_explicit(self):

        @gql
        def query(Name: str):
            pokemon(name=Name),
            {
                classification,
                name,
                id,
            }
        
    
        result = str(query("pokemon"))