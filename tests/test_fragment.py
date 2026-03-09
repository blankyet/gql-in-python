"""Tests for Fragment class."""
import pytest
from gql_in_python.fragment import Fragment
from gql_in_python.field import Field


class TestFragment:
    """Test suite for Fragment class."""

    def test_simple_fragment(self):
        """Test basic fragment."""
        frag = Fragment("comparisonFields", "Character")
        frag["name", "appearsIn"]
        result = str(frag)
        expected = "...comparisonFields"
        assert expected == result
        # Type name and fields are in definition(), not str()

    def test_fragment_with_nested_fields(self):
        """Test fragment with nested fields."""
        frag = Fragment("comparisonFields", "Character")
        frag["name", Field("friends")["name"]]
        result = str(frag)
        # str() only shows fragment name, not fields
        expected = "...comparisonFields"
        assert expected == result
        # Fields are in definition()
        definition = frag.definition()
        assert "friends" in definition
        assert "name" in definition

    def test_fragment_definition(self):
        """Test fragment definition method."""
        frag = Fragment("comparisonFields", "Character")
        frag["name"]
        definition = frag.definition()
        expected = "fragment comparisonFields on Character { name }"
        assert expected == definition

    def test_fragment_repr(self):
        """Test fragment __repr__."""
        frag = Fragment("test", "Type")
        result = repr(frag)
        expected = "...test"
        assert expected == result

    def test_fragment_with_multiple_fields(self):
        """Test fragment with many fields."""
        frag = Fragment("allFields", "User")
        frag["id", "name", "email", "age"]
        result = str(frag)
        # str() only shows fragment name
        expected = "...allFields"
        assert expected == result
        # Fields are in definition()
        definition = frag.definition()
        expected_def = "fragment allFields on User { id name email age }"
        assert expected_def == definition

    def test_fragment_in_operation(self):
        """Test fragment used within an operation."""
        from gql_in_python.operation import Operation
        comparison_fields = Fragment("comparisonFields", "Character")[
            "name",
            "appearsIn"
        ]
        op = Operation("HeroComparison")[
            {"left": Field("hero")(episode="EMPIRE")[comparison_fields]},
            {"right": Field("hero")(episode="JEDI")[comparison_fields]}
        ]
        result = str(op)
        expected = "query HeroComparison {HeroComparison { left: hero(episode: EMPIRE) { ...comparisonFields } right: hero(episode: JEDI) { ...comparisonFields } }}\nfragment comparisonFields on Character { name appearsIn }"
        assert expected == result


class TestFragmentEdgeCases:
    """Test edge cases for Fragment class."""

    def test_fragment_with_no_fields(self):
        """Test fragment with no fields selected."""
        frag = Fragment("empty", "Type")
        result = str(frag)
        expected = "...empty"
        assert expected == result

    def test_fragment_with_complex_type_name(self):
        """Test fragment with complex type name (e.g., union, interface)."""
        frag = Fragment("onUnion", "UnionType")
        frag["name"]
        result = str(frag)
        # str() shows fragment name only
        expected = "...onUnion"
        assert expected == result
        # Type name is in definition()
        definition = frag.definition()
        expected_def = "fragment onUnion on UnionType { name }"
        assert expected_def == definition

    def test_fragment_name_with_underscores(self):
        """Test fragment with underscores in name."""
        frag = Fragment("my_custom_fragment", "MyType")
        frag["field"]
        result = str(frag)
        expected = "...my_custom_fragment"
        assert expected == result
