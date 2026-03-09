"""Tests for gql_types module."""
import pytest
from gql_in_python.types import FieldString, FieldEnum, Variable


class TestFieldString:
    """Test suite for FieldString class."""

    def test_field_string_repr(self):
        """Test FieldString representation."""
        fs = FieldString("test")
        assert str(fs) == '"test"'
        assert repr(fs) == '"test"'

    def test_field_string_with_special_chars(self):
        """Test FieldString with special characters."""
        fs = FieldString("test's value")
        result = str(fs)
        assert "test" in result and "value" in result
        # Should have quotes
        assert '"' in result

    def test_field_string_in_arguments(self):
        """Test FieldString used in FieldArguments."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"name": FieldString("Luke")})
        result = str(args)
        assert '"Luke"' in result


class TestFieldEnum:
    """Test suite for FieldEnum class."""

    def test_field_enum_repr(self):
        """Test FieldEnum representation."""
        fe = FieldEnum("EMPIRE")
        # FieldEnum inherits from UserString, repr() shows quoted string
        assert str(fe) == "EMPIRE"
        assert repr(fe) == "'EMPIRE'"  # UserString repr includes quotes

    def test_field_enum_in_arguments(self):
        """Test FieldEnum used in FieldArguments."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"episode": FieldEnum("EMPIRE")})
        result = str(args)
        # Should not be quoted
        assert "EMPIRE" in result
        assert '"EMPIRE"' not in result

    def test_field_enum_multiple_values(self):
        """Test multiple enum values."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"status": FieldEnum("ACTIVE")})
        result = str(args)
        assert "ACTIVE" in result


class TestVariable:
    """Test suite for Variable class."""

    def test_variable_repr(self):
        """Test Variable representation."""
        var = Variable("id")
        # Variable str() returns the data without $, repr() adds $
        assert str(var) == "$id"
        assert repr(var) == "$id"

    def test_variable_define(self):
        """Test Variable define method."""
        var = Variable("id")
        definition = var.define("ID!")
        assert definition == "$id: ID!"

    def test_variable_with_type(self):
        """Test variable with different types."""
        var = Variable("user")
        definition = var.define("User")
        assert definition == "$user: User"

    def test_variable_in_arguments(self):
        """Test Variable used in FieldArguments."""
        from gql_in_python.field_arguments import FieldArguments
        args = FieldArguments({"id": Variable("$id")})
        result = str(args)
        assert "$id" in result

    def test_variable_in_operation_vars(self):
        """Test Variable in operation vars dict."""
        from gql_in_python.operation import Operation
        op = Operation("hero", vars={"id": "ID!"})
        result = str(op)
        assert "$id: ID!" in result

    def test_variable_define_with_complex_type(self):
        """Test variable with complex type (input object)."""
        var = Variable("input")
        definition = var.define("UserInput!")
        assert definition == "$input: UserInput!"


class TestTypeIntegration:
    """Test integration between gql_types and other modules."""

    def test_enum_with_field(self):
        """Test FieldEnum used with Field."""
        from gql_in_python.field import Field
        field = Field("hero")
        field(episode=FieldEnum("EMPIRE"))
        result = str(field)
        assert "EMPIRE" in result
        assert '"EMPIRE"' not in result

    def test_variable_with_field(self):
        """Test Variable used with Field."""
        from gql_in_python.field import Field
        field = Field("hero")
        field(id=Variable("$heroId"))
        result = str(field)
        assert "$heroId" in result

    def test_string_with_field(self):
        """Test FieldString used with Field."""
        from gql_in_python.field import Field
        field = Field("hero")
        field(name=FieldString("Luke"))
        result = str(field)
        assert '"Luke"' in result
