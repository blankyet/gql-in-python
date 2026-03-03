"""Tests for FieldArguments class."""
import pytest
from gql_in_python.field_arguments import FieldArguments
from gql_in_python.types import FieldEnum, FieldString, Variable
from gql_in_python.list import FieldList


class TestFieldArguments:
    """Test suite for FieldArguments class."""

    def test_simple_arguments(self):
        """Test simple key-value arguments."""
        args = FieldArguments({"id": 123})
        result = str(args)
        assert "id: 123" in result

    def test_multiple_arguments(self):
        """Test multiple arguments."""
        args = FieldArguments({"id": 123, "name": "Luke"})
        result = str(args)
        assert "id: 123" in result
        # String should be quoted
        assert '"Luke"' in result or "Luke" in result

    def test_string_argument_quoted(self):
        """Test that string values are quoted."""
        args = FieldArguments({"name": "Luke"})
        result = str(args)
        assert '"Luke"' in result

    def test_enum_argument(self):
        """Test enum argument (uppercase string)."""
        args = FieldArguments({"episode": "EMPIRE"})
        result = str(args)
        # Uppercase strings become enums, not quoted
        assert "EMPIRE" in result
        assert '"EMPIRE"' not in result

    def test_enum_as_field_enum(self):
        """Test using FieldEnum directly."""
        args = FieldArguments({"episode": FieldEnum("EMPIRE")})
        result = str(args)
        assert "EMPIRE" in result

    def test_variable_argument(self):
        """Test variable argument (starts with $)."""
        args = FieldArguments({"id": "$id"})
        result = str(args)
        assert "$id" in result

    def test_variable_as_variable_type(self):
        """Test using Variable type directly."""
        args = FieldArguments({"id": Variable("$myVar")})
        result = str(args)
        assert "$myVar" in result

    def test_nested_dict_arguments(self):
        """Test nested dict arguments."""
        args = FieldArguments({
            "where": {
                "id": 123,
                "name": "test"
            }
        })
        result = str(args)
        assert "where" in result
        assert "id" in result
        assert "name" in result

    def test_deeply_nested_dict(self):
        """Test deeply nested dict."""
        args = FieldArguments({
            "filter": {
                "and": [
                    {"id": 1},
                    {"name": "test"}
                ]
            }
        })
        result = str(args)
        assert "filter" in result
        assert "and" in result

    def test_list_arguments(self):
        """Test list arguments."""
        args = FieldArguments({"ids": [1, 2, 3]})
        result = str(args)
        assert "ids" in result
        assert "1" in result and "2" in result and "3" in result

    def test_list_of_strings(self):
        """Test list of strings."""
        args = FieldArguments({"status": ["ACTIVE", "INACTIVE"]})
        result = str(args)
        assert "status" in result
        assert "ACTIVE" in result
        assert "INACTIVE" in result

    def test_list_of_dicts(self):
        """Test list of dicts."""
        args = FieldArguments({"items": [{"id": 1}, {"id": 2}]})
        result = str(args)
        assert "items" in result

    def test_none_value_ignored(self):
        """Test that None values are ignored."""
        args = FieldArguments({"id": 123, "name": None})
        result = str(args)
        assert "id" in result
        assert "name" not in result

    def test_compile_method(self):
        """Test compile method returns params string."""
        args = FieldArguments({"id": 123, "name": "test"})
        compiled = args.compile()
        assert "id: 123" in compiled
        assert "name" in compiled

    def test_mixed_types(self):
        """Test arguments with mixed types."""
        args = FieldArguments({
            "id": 123,
            "name": "Luke",
            "episode": "EMPIRE",
            "where": {"id": 456}
        })
        result = str(args)
        assert "id: 123" in result
        assert "name" in result
        assert "EMPIRE" in result
        assert "where" in result

    def test_field_list_conversion(self):
        """Test that lists are converted to FieldList."""
        args = FieldArguments({"list": [1, 2, 3]})
        assert isinstance(args["list"], FieldList)

    def test_field_arguments_conversion(self):
        """Test that nested dicts are converted to FieldArguments."""
        args = FieldArguments({"nested": {"key": "value"}})
        assert isinstance(args["nested"], FieldArguments)

    def test_update_arguments(self):
        """Test updating arguments after creation."""
        args = FieldArguments({"id": 123})
        args["name"] = "Luke"
        result = str(args)
        assert "id: 123" in result
        assert "name" in result


class TestFieldArgumentsEdgeCases:
    """Test edge cases for FieldArguments."""

    def test_empty_arguments(self):
        """Test empty FieldArguments."""
        args = FieldArguments({})
        result = str(args)
        # Empty FieldArguments renders as "{}"
        assert result == "{}"

    def test_boolean_values(self):
        """Test boolean argument values."""
        args = FieldArguments({"active": True, "disabled": False})
        result = str(args)
        # Booleans should be capitalized in GraphQL
        assert "True" in result or "true" in result
        assert "False" in result or "false" in result

    def test_number_types(self):
        """Test different number types."""
        args = FieldArguments({
            "int_val": 42,
            "float_val": 3.14,
            "negative": -10
        })
        result = str(args)
        assert "42" in result
        assert "3.14" in result
        assert "-10" in result

    def test_dict_with_none_values(self):
        """Test dict containing None values."""
        args = FieldArguments({"outer": {"inner": None, "keep": "value"}})
        result = str(args)
        assert "outer" in result
        assert "keep" in result
