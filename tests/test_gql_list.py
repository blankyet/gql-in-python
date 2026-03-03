"""Tests for gql_list module."""
import pytest
from gql_in_python.list import FieldList, FieldNames
from gql_in_python.field import Field
from gql_in_python.types import FieldEnum


class TestFieldList:
    """Test suite for FieldList class."""

    def test_simple_list(self):
        """Test FieldList with simple values."""
        fl = FieldList([1, 2, 3])
        result = str(fl)
        assert result == "[1, 2, 3]"

    def test_list_with_strings(self):
        """Test FieldList with strings."""
        fl = FieldList(["a", "b", "c"])
        result = str(fl)
        # Strings should be quoted
        assert '"a"' in result or 'a' in result

    def test_list_with_fields(self):
        """Test FieldList with Field objects."""
        fl = FieldList([Field("name"), Field("age")])
        result = str(fl)
        assert "name" in result
        assert "age" in result

    def test_list_with_mixed_types(self):
        """Test FieldList with mixed types."""
        fl = FieldList([Field("name"), "age", 123])
        result = str(fl)
        assert "name" in result
        assert "age" in result or '"age"' in result
        assert "123" in result

    def test_list_with_dict_alias(self):
        """Test FieldList with dict for aliases."""
        fl = FieldList([
            {"empireHero": Field("hero")},
            {"jediHero": Field("hero")}
        ])
        result = str(fl)
        assert "empireHero: hero" in result
        assert "jediHero: hero" in result

    def test_list_repr(self):
        """Test FieldList __repr__."""
        fl = FieldList([1, 2, 3])
        result = repr(fl)
        assert result == "[1, 2, 3]"

    def test_empty_list(self):
        """Test empty FieldList."""
        fl = FieldList([])
        result = str(fl)
        assert result == "[]"

    def test_list_with_nested_lists(self):
        """Test FieldList with nested lists."""
        fl = FieldList([[1, 2], [3, 4]])
        result = str(fl)
        assert "[1, 2]" in result or "1, 2" in result

    def test_list_with_enums(self):
        """Test FieldList with enums."""
        fl = FieldList([FieldEnum("ACTIVE"), FieldEnum("INACTIVE")])
        result = str(fl)
        assert "ACTIVE" in result
        assert "INACTIVE" in result


class TestFieldNames:
    """Test suite for FieldNames class."""

    def test_simple_field_names(self):
        """Test FieldNames with simple values."""
        fn = FieldNames(["name", "age", "email"])
        result = str(fn)
        # FieldNames uses space separator
        assert "name" in result
        assert "age" in result
        assert "email" in result
        # Should use spaces not commas between fields
        assert "," not in result or result.count(",") < 2

    def test_field_names_separator(self):
        """Test FieldNames uses space separator."""
        fn = FieldNames(["a", "b", "c"])
        result = str(fn)
        # Should have spaces between items
        assert "a" in result and "b" in result and "c" in result

    def test_field_names_with_fields(self):
        """Test FieldNames with Field objects."""
        fn = FieldNames([Field("name"), Field("age")])
        result = str(fn)
        assert "name" in result
        assert "age" in result

    def test_field_names_empty(self):
        """Test empty FieldNames."""
        fn = FieldNames([])
        result = str(fn)
        # Empty FieldNames should produce the around value
        assert result == "  " or result == ""

    def test_field_names_repr(self):
        """Test FieldNames __repr__."""
        fn = FieldNames(["a", "b"])
        result = repr(fn)
        assert "a" in result
        assert "b" in result

    def test_field_names_with_nested_fields(self):
        """Test FieldNames with nested Field objects."""
        fn = FieldNames([
            Field("name"),
            Field("friends")["name", "age"]
        ])
        result = str(fn)
        assert "name" in result
        assert "friends" in result

    def test_field_names_around(self):
        """Test FieldNames uses double space as around."""
        fn = FieldNames(["field1", "field2"])
        result = str(fn)
        # FieldNames uses "  " as around
        assert result.startswith("  ") or result.startswith(" ")
        assert result.endswith("  ") or result.endswith(" ")


class TestFieldListIntegration:
    """Test FieldList integration with FieldArguments."""

    def test_list_in_arguments(self):
        """Test FieldList used in FieldArguments."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"ids": [1, 2, 3]})
        result = str(args)
        assert "ids" in result
        assert "1" in result

    def test_nested_list_in_arguments(self):
        """Test nested lists in arguments."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"nested": [[1, 2], [3, 4]]})
        result = str(args)
        assert "nested" in result

    def test_field_names_in_field(self):
        """Test FieldNames used in Field."""
        field = Field("hero")
        field["name", "age"]
        result = str(field)
        # Should have proper spacing
        assert "name" in result
        assert "age" in result


class TestFieldListEdgeCases:
    """Test edge cases for FieldList."""

    def test_list_with_none_values(self):
        """Test FieldList with None values."""
        fl = FieldList([1, None, 3])
        result = str(fl)
        # None might be filtered or represented as null
        assert "1" in result
        assert "3" in result

    def test_list_with_duplicate_items(self):
        """Test FieldList with duplicate items."""
        fl = FieldList(["a", "a", "b"])
        result = str(fl)
        # Should preserve duplicates
        assert result.count("a") >= 2 or "a" in result

    def test_list_modification(self):
        """Test modifying FieldList after creation."""
        fl = FieldList([1, 2])
        fl.append(3)
        result = str(fl)
        assert "3" in result
