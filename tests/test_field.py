"""Tests for Field class."""
import pytest
from gql_in_python.field import Field
from gql_in_python.types import FieldEnum, FieldString, Variable


class TestField:
    """Test suite for Field class."""

    def test_simple_field(self):
        """Test basic field without arguments or subfields."""
        field = Field("name")
        result = str(field)
        expected = "name"
        assert expected == result

    def test_field_with_arguments(self):
        """Test field with arguments."""
        field = Field("hero")
        field(id=123)
        result = str(field)
        expected = "hero(id: 123)"
        assert expected == result

    def test_field_with_string_argument(self):
        """Test field with string argument."""
        field = Field("hero")
        field(id="123")
        result = str(field)
        expected = 'hero(id: "123")'
        assert expected == result

    def test_field_with_multiple_arguments(self):
        """Test field with multiple arguments."""
        field = Field("hero")
        field(id=123, episode="EMPIRE")
        result = str(field)
        expected = "hero(id: 123, episode: EMPIRE)"
        assert expected == result

    def test_field_with_nested_dict_arguments(self):
        """Test field with nested dict arguments."""
        field = Field("hero")
        field(where={"id": 123})
        result = str(field)
        expected = "hero(where: {id: 123})"
        assert expected == result

    def test_field_with_subfields(self):
        """Test field with subfield selection."""
        field = Field("hero")
        field["name", "height"]
        result = str(field)
        expected = "hero { name height }"
        assert expected == result

    def test_field_with_arguments_and_subfields(self):
        """Test field with both arguments and subfields."""
        field = Field("hero")
        field(id=123)["name", "height"]
        result = str(field)
        expected = "hero(id: 123) { name height }"
        assert expected == result

    def test_field_alias(self):
        """Test field with alias."""
        field = Field("hero").alias("empireHero")
        result = str(field)
        expected = "empireHero: hero"
        assert expected == result

    def test_field_alias_with_arguments(self):
        """Test field with alias and arguments."""
        field = Field("hero").alias("empireHero")
        field(episode="EMPIRE")
        result = str(field)
        expected = "empireHero: hero(episode: EMPIRE)"
        assert expected == result

    def test_field_alias_with_subfields(self):
        """Test field with alias and subfields."""
        field = Field("hero").alias("empireHero")
        field["name"]
        result = str(field)
        expected = "empireHero: hero { name }"
        assert expected == result

    def test_field_chaining(self):
        """Test chaining field calls."""
        field = Field("hero")(id=123)["name"]
        result = str(field)
        expected = "hero(id: 123) { name }"
        assert expected == result

    def test_field_with_enum(self):
        """Test field with enum argument."""
        field = Field("hero")
        field(episode=FieldEnum("EMPIRE"))
        result = str(field)
        expected = "hero(episode: EMPIRE)"
        assert expected == result
        # Enum should not be quoted
        assert '"EMPIRE"' not in result

    def test_field_with_variable(self):
        """Test field with variable argument."""
        field = Field("hero")
        field(id=Variable("$id"))
        result = str(field)
        expected = "hero(id: $$id)"
        assert expected == result

    def test_field_with_list_subfields(self):
        """Test field with list of subfields."""
        field = Field("hero")
        field["name", "height", "appearsIn"]
        result = str(field)
        # Check all fields are present
        assert "name" in result
        assert "height" in result
        assert "appearsIn" in result
        assert "hero" in result
        # Verify it's a selection set
        assert "{" in result and "}" in result

    def test_field_repr(self):
        """Test field __repr__."""
        field = Field("hero", {"id": 123}, ["name"])
        result = repr(field)
        expected = "hero(id: 123) { name }"
        assert expected == result


class TestFieldEdgeCases:
    """Test edge cases for Field class."""

    def test_field_with_empty_arguments(self):
        """Test field with empty arguments dict."""
        field = Field("hero")
        field({})
        result = str(field)
        expected = "hero"
        assert expected == result

    def test_field_with_none_value(self):
        """Test field with None argument (should be ignored)."""
        field = Field("hero")
        field(id=None)
        result = str(field)
        expected = "hero"
        assert expected == result

    def test_field_with_mixed_call_patterns(self):
        """Test mixing __call__ patterns - last call overwrites."""
        field = Field("hero")
        # First call with dict
        field({"id": 123})
        # Then with kwargs - overwrites previous arguments
        field(episode="EMPIRE")
        result = str(field)
        expected = "hero(episode: EMPIRE)"
        assert expected == result

    def test_field_with_nested_field_subselection(self):
        """Test field with nested field as subselection."""
        inner = Field("name")
        outer = Field("hero")[inner]
        result = str(outer)
        expected = "hero { name }"
        assert expected == result

    def test_field_with_dict_alias_in_subfields(self):
        """Test using dict for alias in subfield selection."""
        field = Field("query")[
            {"empireHero": Field("hero")(episode="EMPIRE")["name"]},
            {"jediHero": Field("hero")(episode="JEDI")["name"]}
        ]
        result = str(field)
        expected = "query { empireHero: hero(episode: EMPIRE) { name } jediHero: hero(episode: JEDI) { name } }"
        assert expected == result
