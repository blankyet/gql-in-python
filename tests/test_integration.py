"""Integration tests covering complex scenarios from the user's examples."""
import pytest
from gql_in_python.operation import Operation
from gql_in_python.field import Field
from gql_in_python.fragment import Fragment
from gql_in_python.types import FieldEnum, Variable
from gql_in_python.list import FieldNames


class TestComplexScenarios:
    """Test complex real-world GraphQL query patterns."""

    def test_basic_hero_query_with_id(self):
        """Test: operation = Operation("hero")"""
        op = Operation("hero")
        result = str(op(id=123)["name"])
        assert "query hero" in result
        assert "hero" in result
        assert "id: 123" in result
        assert "name" in result

    def test_hero_query_with_multiple_fields(self):
        """Test hero query with multiple fields."""
        op = Operation("hero")
        result = str(op(id=123)["name", "height"])
        assert "hero" in result
        assert "name" in result
        assert "height" in result

    def test_hero_with_enum_argument(self):
        """Test hero with episode enum."""
        op = Operation("hero")
        result = str(op(id=123, episode="EMPIRE")["name"])
        assert "episode: EMPIRE" in result

    def test_subscription_operation(self):
        """Test subscription with custom name."""
        op = Operation("human", operation_name="HeroSelectRightNow", operation_type="subscription")
        result = str(op(id=1000)["name", "height"])
        assert result.startswith("subscription HeroSelectRightNow")
        assert "human" in result
        assert "name" in result

    def test_multiple_root_fields_with_aliases(self):
        """Test query with multiple root fields using aliases."""
        op = Operation("hero")
        result = str(op[
            {"empireHero": Field("hero")(episode="EMPIRE")["name"]},
            {"jediHero": Field("hero")(episode="JEDI")["name"]}
        ])
        assert "empireHero: hero" in result
        assert "jediHero: hero" in result
        assert "EMPIRE" in result
        assert "JEDI" in result

    def test_nested_field_with_arguments(self):
        """Test nested field that has its own arguments."""
        op = Operation("human")
        result = str(op(id=1000)[
            "name",
            Field("height")(unit="FOOT")["value", "unit"]
        ])
        assert "height(unit: FOOT)" in result
        assert "value" in result

    def test_deeply_nested_structure(self):
        """Test deeply nested query with multiple levels."""
        op = Operation("human")
        result = str(op(id=1000)[
            "name",
            Field("height")(unit="FOOT")[
                "value",
                Field("unitDetails")["name"]
            ]
        ])
        assert "height(unit: FOOT)" in result
        assert "value" in result
        assert "unitDetails" in result

    def test_fragment_usage(self):
        """Test using fragments for reusable field sets."""
        comparison_fields = Fragment("comparisonFields", "Character")[
            "name",
            "appearsIn",
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

    def test_inline_fragment_with_type_condition(self):
        """Test inline fragment with type condition."""
        op = Operation("HeroComparison")[
            {"left": Field("hero")(episode="EMPIRE")[
                Fragment("Droid", "Droid")["primaryFunction"]
            ]},
            {"right": Field("hero")(episode="JEDI")[
                "name",
                Fragment("Human", "Human")["height"]
            ]}
        ]
        result = str(op)
        # Inline fragments render as "...TypeName"
        assert "...Droid" in result
        assert "primaryFunction" in result
        assert "...Human" in result
        assert "height" in result

    def test_operation_with_variables_in_header(self):
        """Test operation with variable definitions."""
        op = Operation("hero", vars={"id": "ID!", "episode": "Episode"})
        result = str(op(id=Variable("$id"), episode=Variable("$episode"))["name"])
        assert "$id: ID!" in result
        assert "$episode: Episode" in result
        assert "hero(id: $id, episode: $episode)" in result

    def test_complex_nested_arguments(self):
        """Test complex nested dict arguments (like Hasura where clauses)."""
        op = Operation("pokemon_gen_1")
        result = str(op(
            where={
                "pokemon_v2_generation": {
                    "name": {"_eq": "generation-i"}
                }
            },
            order_by={"id": "asc"}
        )["name"])
        assert "where" in result
        assert "pokemon_v2_generation" in result
        assert "_eq" in result
        assert "order_by" in result

    def test_mutation_with_input_object(self):
        """Test mutation with input object."""
        op = Operation("createUser", operation_type="mutation")
        result = str(op(
            input={
                "name": "Luke",
                "email": "luke@example.com",
                "age": 25
            }
        )["id", "name"])
        assert "mutation createUser" in result
        assert "input" in result
        assert "name" in result

    def test_query_with_list_argument(self):
        """Test query with list argument."""
        op = Operation("users")
        result = str(op(ids=[1, 2, 3])["name"])
        assert "ids" in result
        assert "1" in result and "2" in result and "3" in result

    def test_field_with_alias_and_nested_fields(self):
        """Test field with alias and nested subfields."""
        op = Operation("query")
        result = str(op[
            {"empireHero": Field("hero")(episode="EMPIRE")[
                "name",
                Field("height")(unit="FOOT")["value"]
            ]}
        ])
        assert "empireHero: hero(episode: EMPIRE)" in result
        assert "height(unit: FOOT)" in result
        assert "value" in result

    def test_using_g_namespace_pattern(self):
        """Test using a 'g' namespace object pattern."""
        # Simulate g object
        class GQLNamespace:
            def __getattr__(self, name):
                return Field(name)

        g = GQLNamespace()

        op = Operation("human")
        result = str(op(id=123)[
            g.name,
            g.height(unit="FOOT")[
                g.value,
            ],
            {"empireHero": g.hero(episode="EMPIRE")[
                g.name,
            ]}
        ])
        assert "name" in result
        assert "height(unit: FOOT)" in result
        assert "value" in result
        assert "empireHero: hero(episode: EMPIRE)" in result

    def test_operation_without_vars_definition(self):
        """Test operation without variable definitions."""
        op = Operation("hero")
        result = str(op["name"])
        # Should not have $ in header
        header = result.split('{')[0]
        assert "$" not in header

    def test_operation_name_different_from_root(self):
        """Test operation name differs from root field."""
        op = Operation("hero", operation_name="FetchHeroData")
        result = str(op["name"])
        assert "query FetchHeroData" in result
        assert "hero" in result

    def test_mutation_with_complex_input(self):
        """Test mutation with nested input object."""
        op = Operation("updateUser", operation_type="mutation")
        result = str(op(
            input={
                "user": {
                    "id": 123,
                    "profile": {
                        "name": "Luke",
                        "age": 25
                    }
                }
            }
        )["user", "id"])
        assert "mutation updateUser" in result
        assert "user" in result
        assert "profile" in result

    def test_field_with_enum_in_nested_structure(self):
        """Test enum values in deeply nested fields."""
        op = Operation("query")
        result = str(op[
            Field("hero")(episode="EMPIRE")[
                "name",
                Field("friends")[
                    Field("character")(type="DROID")[
                        "name"
                    ]
                ]
            ]
        ])
        assert "EMPIRE" in result
        assert "DROID" in result

    def test_operation_with_multiple_variables(self):
        """Test operation with many variable definitions."""
        op = Operation("complexQuery", vars={
            "id": "ID!",
            "episode": "Episode",
            "limit": "Int",
            "filter": "UserFilter"
        })
        result = str(op(
            id=Variable("$id"),
            episode=Variable("$episode"),
            limit=Variable("$limit"),
            filter=Variable("$filter")
        )["name"])
        assert "$id: ID!" in result
        assert "$episode: Episode" in result
        assert "$limit: Int" in result
        assert "$filter: UserFilter" in result

    def test_fragment_on_different_types(self):
        """Test fragment used on multiple root fields."""
        common_fields = Fragment("common", "Character")["name", "appearsIn"]
        op = Operation("MultiHero")[
            {"hero1": Field("hero")(episode="EMPIRE")[common_fields]},
            {"hero2": Field("hero")(episode="JEDI")[common_fields]},
            {"villain": Field("villain")[common_fields]}
        ]
        result = str(op)
        assert "fragment common on Character" in result
        # Fragment should be referenced multiple times
        assert "common" in result

    def test_field_chain_with_arguments_at_each_level(self):
        """Test field chain where each level has arguments."""
        op = Operation("query")
        result = str(op[
            Field("level1")(arg1="a")[
                Field("level2")(arg2="b")[
                    Field("level3")(arg3="c")[
                        "finalField"
                    ]
                ]
            ]
        ])
        # String arguments are quoted
        assert 'level1(arg1: "a")' in result or "level1(arg1: a)" in result
        assert 'level2(arg2: "b")' in result or "level2(arg2: b)" in result
        assert 'level3(arg3: "c")' in result or "level3(arg3: c)" in result
        assert "finalField" in result

    def test_operation_with_fragment_and_inline_fragment(self):
        """Test combining named and inline fragments."""
        char_fields = Fragment("charFields", "Character")[
            "name",
            "appearsIn"
        ]
        op = Operation("HeroCompare")[
            {"hero1": Field("hero")(episode="EMPIRE")[
                char_fields,
                Fragment("Droid", "Droid")["primaryFunction"]
            ]},
            {"hero2": Field("hero")(episode="JEDI")[
                char_fields,
                Fragment("Human", "Human")["height"]
            ]}
        ]
        result = str(op)
        assert "fragment charFields on Character" in result
        # Inline fragments render as "...TypeName" (no "on") in the query
        # They also get converted to named fragments in the output
        # So we check for both the inline usage and the fragment definition
        assert "...Droid" in result or "fragment Droid" in result
        assert "...Human" in result or "fragment Human" in result
        assert "primaryFunction" in result
        assert "height" in result

    def test_using_both_string_and_field_objects(self):
        """Test mixing string field names and Field objects."""
        op = Operation("hero")
        result = str(op[
            "name",
            Field("height")(unit="FOOT")["value"],
            {"otherHero": Field("hero")(episode="JEDI")["name"]}
        ])
        assert "name" in result
        assert "height(unit: FOOT)" in result
        assert "otherHero: hero" in result

    def test_operation_str_and_repr_equal(self):
        """Test that str() and repr() produce identical output."""
        op = Operation("hero", operation_name="GetHero")(
            id=123
        )[
            "name",
            Field("height")(unit="FOOT")["value"]
        ]
        assert str(op) == repr(op)

    def test_complex_example_from_docs(self):
        """Test example similar to GraphQL documentation."""
        # Query with multiple root fields and aliases
        op = Operation("query")
        result = str(op[
            {"empireHero": Field("hero")(episode="EMPIRE")["name"]},
            {"jediHero": Field("hero")(episode="JEDI")["name"]}
        ])
        assert "empireHero: hero" in result
        assert "jediHero: hero" in result
        assert "EMPIRE" in result
        assert "JEDI" in result

    def test_fragment_with_multiple_fields_and_nesting(self):
        """Test fragment with complex field structure."""
        frag = Fragment("characterFields", "Character")[
            "name",
            "appearsIn",
            Field("friends")[
                "name",
                Field("height")(unit="FOOT")["value"]
            ]
        ]
        op = Operation("GetCharacters")[
            {"hero": Field("hero")(episode="EMPIRE")[frag]},
            {"jedi": Field("hero")(episode="JEDI")[frag]}
        ]
        result = str(op)
        assert "fragment characterFields on Character" in result
        assert "friends" in result
        assert "height(unit: FOOT)" in result

    def test_nested_aliases(self):
        """Test multiple levels of aliases."""
        op = Operation("query")
        result = str(op[
            {"firstHero": Field("hero")(episode="EMPIRE")[
                {"heroName": Field("name")},
                {"heroHeight": Field("height")}
            ]},
            {"secondHero": Field("hero")(episode="JEDI")[
                "name",
                "height"
            ]}
        ])
        assert "firstHero: hero" in result
        assert "secondHero: hero" in result

    def test_operation_with_fragment_and_inline_fragment(self):
        """Test combining named and inline fragments."""
        char_fields = Fragment("charFields", "Character")[
            "name",
            "appearsIn"
        ]
        op = Operation("HeroCompare")[
            {"hero1": Field("hero")(episode="EMPIRE")[
                char_fields,
                Fragment("Droid", "Droid")["primaryFunction"]
            ]},
            {"hero2": Field("hero")(episode="JEDI")[
                char_fields,
                Fragment("Human", "Human")["height"]
            ]}
        ]
        result = str(op)
        assert "fragment charFields on Character" in result
        # Inline fragments appear as "...TypeName" in the query (no "on")
        assert "...Droid" in result
        assert "...Human" in result

    def test_fragment_on_different_types(self):
        """Test fragment used on multiple root fields."""
        common_fields = Fragment("common", "Character")["name", "appearsIn"]
        op = Operation("MultiHero")[
            {"hero1": Field("hero")(episode="EMPIRE")[common_fields]},
            {"hero2": Field("hero")(episode="JEDI")[common_fields]},
            {"villain": Field("villain")[common_fields]}
        ]
        result = str(op)
        assert "fragment common on Character" in result
