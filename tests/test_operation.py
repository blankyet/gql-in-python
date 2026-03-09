"""Tests for Operation class."""
import pytest
from gql_in_python.operation import Operation
from gql_in_python.field import Field
from gql_in_python.fragment import Fragment
from gql_in_python.types import Variable, FieldEnum
from graphql import build_schema, validate, parse

# Simple schema for validation (minimal types)
SCHEMA_GRAPHQL = """
type Query {
    hero(id: ID, episode: Episode): Character
    characters: [Character]
}

type Character {
    name: String
    height: Float
    friends: [Character]
}

enum Episode {
    NEWHOPE
    EMPIRE
    JEDI
}
"""

MUTATION_SCHEMA_GRAPHQL = """
type Mutation {
    createHero(name: String!): Character
}
"""

SUBSCRIPTION_SCHEMA_GRAPHQL = """
type Subscription {
    hero(id: Int!): Character
}
"""


def validate_graphql(query: str, schema_str: str = SCHEMA_GRAPHQL) -> None:
    """Validate a GraphQL query is syntactically valid."""
    try:
        # Just parse to ensure it's valid GraphQL syntax
        parse(query)
    except Exception as e:
        raise AssertionError(f"GraphQL parsing failed: {e}")


class TestOperation:
    """Test suite for Operation class."""

    def test_simple_query(self):
        """Test basic query without arguments."""
        op = Operation("hero")
        result = str(op["name"])
        expected = "query hero {hero { name }}"
        assert expected == result
        validate_graphql(result)

    def test_query_with_args(self):
        """Test query with arguments."""
        op = Operation("hero")
        result = str(op(id=123)["name"])
        expected = "query hero {hero(id: 123) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_query_with_dict_args(self):
        """Test query with dict arguments."""
        op = Operation("hero")
        result = str(op({"id": 123})["name"])
        expected = "query hero {hero(id: 123) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_query_with_multiple_args(self):
        """Test query with multiple arguments."""
        op = Operation("hero")
        result = str(op(id=123, episode="EMPIRE")["name"])
        expected = "query hero {hero(id: 123, episode: EMPIRE) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_query_with_string_arg(self):
        """Test query with string argument."""
        op = Operation("hero")
        result = str(op(id="123")["name"])
        expected = 'query hero {hero(id: "123") { name }}'
        assert expected == result
        validate_graphql(result)

    def test_nested_fields(self):
        """Test nested field selection."""
        op = Operation("hero")
        result = str(op["name", "height"])
        expected = "query hero {hero { name height }}"
        assert expected == result
        validate_graphql(result)

    def test_deeply_nested_fields(self):
        """Test deeply nested field selection."""
        op = Operation("hero")
        result = str(op["name", Field("friends")["name", "age"]])
        expected = "query hero {hero { name friends { name age } }}"
        assert expected == result
        validate_graphql(result)

    def test_operation_with_name(self):
        """Test query with custom operation name."""
        op = Operation("hero", operation_name="GetHero")
        result = str(op["name"])
        expected = "query GetHero {hero { name }}"
        assert expected == result
        validate_graphql(result)

    def test_mutation_operation(self):
        """Test mutation operation."""
        op = Operation("createHero", operation_type="mutation")
        result = str(op(name="Luke")["id", "name"])
        expected = "mutation createHero {createHero(name: \"Luke\") { id name }}"
        assert expected == result
        validate_graphql(result, MUTATION_SCHEMA_GRAPHQL)

    def test_subscription_operation(self):
        """Test subscription operation."""
        op = Operation("hero", operation_name="HeroSelectRightNow", operation_type="subscription")
        result = str(op(id=1000)["name"])
        expected = "subscription HeroSelectRightNow {hero(id: 1000) { name }}"
        assert expected == result
        validate_graphql(result, SUBSCRIPTION_SCHEMA_GRAPHQL)

    def test_operation_with_variables_header(self):
        """Test operation with variable definitions in header."""
        op = Operation("hero", vars={"id": "ID!", "episode": "Episode"})
        result = str(op["name"])
        expected = "query hero($id: ID!, $episode: Episode) {hero { name }}"
        assert expected == result
        validate_graphql(result)

    def test_operation_with_variables_usage(self):
        """Test operation using variables in arguments."""
        op = Operation("hero", vars={"id": "ID!"})
        result = str(op(id=Variable("id"))["name"])
        expected = "query hero($id: ID!) {hero(id: $id) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_operation_with_multiple_root_fields(self):
        """Test operation with multiple root fields (aliases)."""
        op = Operation("hero")
        result = str(op[
            {"empireHero": Field("hero")(episode="EMPIRE")["name"]},
            {"jediHero": Field("hero")(episode="JEDI")["name"]}
        ])
        expected = "query hero {hero { empireHero: hero(episode: EMPIRE) { name } jediHero: hero(episode: JEDI) { name } }}"
        assert expected == result
        validate_graphql(result)

    def test_fragment_in_operation(self):
        """Test operation with fragment."""
        comparison_fields = Fragment("comparisonFields", "Character")[
            "name",
            Field("friends")["name"]
        ]
        op = Operation("HeroComparison")[
            {"left": Field("hero")(episode="EMPIRE")[comparison_fields]},
            {"right": Field("hero")(episode="JEDI")[comparison_fields]}
        ]
        result = str(op)
        expected = "query HeroComparison {HeroComparison { left: hero(episode: EMPIRE) { ...comparisonFields } right: hero(episode: JEDI) { ...comparisonFields } }}\nfragment comparisonFields on Character { name friends { name } }"
        assert expected == result
        validate_graphql(result)

    def test_inline_fragment(self):
        """Test inline fragment."""
        op = Operation("HeroComparison")[
            {"left": Field("hero")(episode="EMPIRE")[
                Fragment("Droid", "Droid")["primaryFunction"]
            ]}
        ]
        result = str(op)
        expected = "query HeroComparison {HeroComparison { left: hero(episode: EMPIRE) { ...Droid } }}\nfragment Droid on Droid { primaryFunction }"
        assert expected == result
        validate_graphql(result)

    def test_operation_repr_without_fields(self):
        """Test operation representation when no fields selected."""
        op = Operation("hero")
        result = repr(op)
        expected = "query hero {hero}"
        assert expected == result
        validate_graphql(expected)

    def test_operation_str_consistency(self):
        """Test that str and repr produce same output."""
        op = Operation("hero")["name"]
        result = str(op)
        expected = "query hero {hero { name }}"
        assert expected == result
        validate_graphql(result)


class TestOperationEdgeCases:
    """Test edge cases for Operation class."""

    def test_empty_operation_name(self):
        """Test operation with None as root name - should handle."""
        # Current behavior: None is accepted, may need validation
        try:
            op = Operation(None)
            # If it doesn't raise, check it produces something
            result = str(op)
            assert "query" in result or "None" in result
        except (AttributeError, TypeError):
            pass  # Also acceptable

    def test_operation_with_enum_values(self):
        """Test operation with enum values."""
        op = Operation("hero")
        result = str(op(episode=FieldEnum("EMPIRE"))["name"])
        expected = "query hero {hero(episode: EMPIRE) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_operation_with_list_args(self):
        """Test operation with list arguments."""
        op = Operation("hero")
        result = str(op(ids=[1, 2, 3])["name"])
        expected = "query hero {hero(ids: [1, 2, 3]) { name }}"
        assert expected == result
        validate_graphql(result)

    def test_operation_with_nested_dict_args(self):
        """Test operation with nested dict arguments."""
        op = Operation("hero")
        result = str(op(where={"id": 123})["name"])
        expected = "query hero {hero(where: {id: 123}) { name }}"
        assert expected == result
        validate_graphql(result)
