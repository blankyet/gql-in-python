"""Tests for Operation class."""
import pytest
from gql_in_python.operation import Operation
from gql_in_python.field import Field
from gql_in_python.fragment import Fragment
from gql_in_python.types import Variable, FieldEnum


class TestOperation:
    """Test suite for Operation class."""

    def test_simple_query(self):
        """Test basic query without arguments."""
        op = Operation("hero")
        result = str(op["name"])
        # Expected: query hero { hero { name } }
        assert "query hero" in result
        assert "hero" in result
        assert "name" in result
        assert "{" in result and "}" in result

    def test_query_with_args(self):
        """Test query with arguments."""
        op = Operation("hero")
        result = str(op(id=123)["name"])
        assert "query hero" in result
        assert "hero(id: 123)" in result
        assert "name" in result

    def test_query_with_dict_args(self):
        """Test query with dict arguments."""
        op = Operation("hero")
        result = str(op({"id": 123})["name"])
        assert "hero(id: 123)" in result
        assert "name" in result

    def test_query_with_multiple_args(self):
        """Test query with multiple arguments."""
        op = Operation("hero")
        result = str(op(id=123, episode="EMPIRE")["name"])
        assert "hero(id: 123, episode: EMPIRE)" in result
        assert "name" in result

    def test_query_with_string_arg(self):
        """Test query with string argument."""
        op = Operation("hero")
        result = str(op(id="123")["name"])
        assert 'hero(id: "123")' in result
        assert "name" in result

    def test_nested_fields(self):
        """Test nested field selection."""
        op = Operation("hero")
        result = str(op["name", "height"])
        assert "hero" in result
        assert "name" in result
        assert "height" in result

    def test_deeply_nested_fields(self):
        """Test deeply nested field selection."""
        op = Operation("hero")
        result = str(op["name", Field("friends")["name", "age"]])
        assert "hero" in result
        assert "friends" in result
        assert "name" in result and "age" in result

    def test_operation_with_name(self):
        """Test query with custom operation name."""
        op = Operation("hero", operation_name="GetHero")
        result = str(op["name"])
        assert "query GetHero" in result
        assert "hero" in result
        assert "name" in result

    def test_mutation_operation(self):
        """Test mutation operation."""
        op = Operation("createHero", operation_type="mutation")
        result = str(op(name="Luke")["id", "name"])
        assert result.startswith("mutation createHero")
        assert "createHero" in result
        assert "name" in result and "id" in result

    def test_subscription_operation(self):
        """Test subscription operation."""
        op = Operation("hero", operation_name="HeroSelectRightNow", operation_type="subscription")
        result = str(op(id=1000)["name"])
        assert result.startswith("subscription HeroSelectRightNow")
        assert "hero" in result
        assert "name" in result

    def test_operation_with_variables_header(self):
        """Test operation with variable definitions in header."""
        op = Operation("hero", vars={"id": "ID!", "episode": "Episode"})
        result = str(op["name"])
        assert "$id: ID!" in result
        assert "$episode: Episode" in result
        assert "query hero" in result

    def test_operation_with_variables_usage(self):
        """Test operation using variables in arguments."""
        op = Operation("hero", vars={"id": "ID!"})
        result = str(op(id=Variable("$id"))["name"])
        assert 'hero(id: $id)' in result
        assert "name" in result

    def test_operation_with_multiple_root_fields(self):
        """Test operation with multiple root fields (aliases)."""
        op = Operation("hero")
        result = str(op[
            {"empireHero": Field("hero")(episode="EMPIRE")["name"]},
            {"jediHero": Field("hero")(episode="JEDI")["name"]}
        ])
        assert "empireHero: hero" in result
        assert "jediHero: hero" in result
        assert "EMPIRE" in result and "JEDI" in result

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
        assert "fragment comparisonFields on Character" in result
        assert "left: hero" in result
        assert "right: hero" in result
        assert "friends" in result

    def test_inline_fragment(self):
        """Test inline fragment."""
        op = Operation("HeroComparison")[
            {"left": Field("hero")(episode="EMPIRE")[
                Fragment("Droid", "Droid")["primaryFunction"]
            ]}
        ]
        result = str(op)
        # Inline fragment shows as "...Droid" (without "on")
        assert "...Droid" in result
        assert "primaryFunction" in result

    def test_operation_repr_without_fields(self):
        """Test operation representation when no fields selected."""
        op = Operation("hero")
        result = repr(op)
        assert "query hero" in result
        assert "{" in result
        assert "hero" in result

    def test_operation_str_consistency(self):
        """Test that str and repr produce same output."""
        op = Operation("hero")["name"]
        assert str(op) == repr(op)
        assert "hero" in str(op)
        assert "name" in str(op)


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
        assert "EMPIRE" in result
        # Should not be quoted
        assert '"EMPIRE"' not in result

    def test_operation_with_list_args(self):
        """Test operation with list arguments."""
        op = Operation("hero")
        result = str(op(ids=[1, 2, 3])["name"])
        assert "ids" in result
        assert "1" in result and "2" in result and "3" in result

    def test_operation_with_nested_dict_args(self):
        """Test operation with nested dict arguments."""
        op = Operation("hero")
        result = str(op(where={"id": 123})["name"])
        assert "where" in result
        assert "id" in result
