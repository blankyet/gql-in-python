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
        expected = "{id: 123}"
        assert expected == result

    def test_multiple_arguments(self):
        """Test multiple arguments."""
        args = FieldArguments({"id": 123, "name": "Luke"})
        result = str(args)
        expected = '{id: 123, name: "Luke"}'
        assert expected == result

    def test_string_argument_quoted(self):
        """Test that string values are quoted."""
        args = FieldArguments({"name": "Luke"})
        result = str(args)
        expected = '{name: "Luke"}'
        assert expected == result

    def test_enum_argument(self):
        """Test enum argument (uppercase string)."""
        args = FieldArguments({"episode": "EMPIRE"})
        result = str(args)
        expected = "{episode: EMPIRE}"
        assert expected == result

    def test_enum_as_field_enum(self):
        """Test using FieldEnum directly."""
        args = FieldArguments({"episode": FieldEnum("EMPIRE")})
        result = str(args)
        expected = "{episode: EMPIRE}"
        assert expected == result

    def test_variable_argument(self):
        """Test variable argument (starts with $)."""
        args = FieldArguments({"id": "$id"})
        result = str(args)
        expected = "{id: $$id}"
        assert expected == result

    def test_variable_as_variable_type(self):
        """Test using Variable type directly."""
        args = FieldArguments({"id": Variable("$myVar")})
        result = str(args)
        expected = "{id: $$myVar}"
        assert expected == result

    def test_nested_dict_arguments(self):
        """Test nested dict arguments."""
        args = FieldArguments({
            "where": {
                "id": 123,
                "name": "test"
            }
        })
        result = str(args)
        expected = '{where: {id: 123, name: "test"}}'
        assert expected == result

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
        expected = "{filter: {and: []}}"
        assert expected == result

    def test_list_arguments(self):
        """Test list arguments."""
        args = FieldArguments({"ids": [1, 2, 3]})
        result = str(args)
        expected = "{ids: [1, 2, 3]}"
        assert expected == result

    def test_list_of_strings(self):
        """Test list of strings."""
        args = FieldArguments({"status": ["ACTIVE", "INACTIVE"]})
        result = str(args)
        expected = "{status: [ACTIVE, INACTIVE]}"
        assert expected == result

    def test_list_of_dicts(self):
        """Test list of dicts."""
        args = FieldArguments({"items": [{"id": 1}, {"id": 2}]})
        result = str(args)
        expected = "{items: []}"
        assert expected == result

    def test_none_value_ignored(self):
        """Test that None values are ignored."""
        args = FieldArguments({"id": 123, "name": None})
        result = str(args)
        expected = "{id: 123}"
        assert expected == result

    def test_compile_method(self):
        """Test compile method returns params string."""
        args = FieldArguments({"id": 123, "name": "test"})
        compiled = args.compile()
        expected = "id: 123, name: \"test\""
        assert expected == compiled

    def test_mixed_types(self):
        """Test arguments with mixed types."""
        args = FieldArguments({
            "id": 123,
            "name": "Luke",
            "episode": "EMPIRE",
            "where": {"id": 456}
        })
        result = str(args)
        expected = '{id: 123, name: "Luke", episode: EMPIRE, where: {id: 456}}'
        assert expected == result

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
        expected = '{id: 123, name: "Luke"}'
        assert expected == result


class TestFieldArgumentsEdgeCases:
    """Test edge cases for FieldArguments."""

    def test_empty_arguments(self):
        """Test empty FieldArguments."""
        args = FieldArguments({})
        result = str(args)
        expected = "{}"
        assert expected == result

    def test_boolean_values(self):
        """Test boolean argument values."""
        args = FieldArguments({"active": True, "disabled": False})
        result = str(args)
        expected = "{active: True, disabled: False}"
        assert expected == result

    def test_number_types(self):
        """Test different number types."""
        args = FieldArguments({
            "int_val": 42,
            "float_val": 3.14,
            "negative": -10
        })
        result = str(args)
        expected = "{int_val: 42, float_val: 3.14, negative: -10}"
        assert expected == result

    def test_dict_with_none_values(self):
        """Test dict containing None values."""
        args = FieldArguments({"outer": {"inner": None, "keep": "value"}})
        result = str(args)
        expected = '{outer: {keep: "value"}}'
        assert expected == result
