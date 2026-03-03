"""Validate generated GraphQL queries are syntactically correct."""
from gql_in_python.operation import Operation
from gql_in_python.field import Field
from gql_in_python.fragment import Fragment
from graphql import parse

# Test that queries are syntactically valid GraphQL
test_cases = [
    ('Simple query', str(Operation('hero')['name'])),
    ('Query with args', str(Operation('hero')(id=123)['name', 'height'])),
    ('Query with string arg', str(Operation('hero')(id='123')['name'])),
    ('Multiple root fields', str(Operation('query')[
        {'empireHero': Field('hero')(episode='EMPIRE')['name']},
        {'jediHero': Field('hero')(episode='JEDI')['name']}
    ])),
    ('Nested fields', str(Operation('human')(id=1000)[
        'name',
        Field('height')(unit='FOOT')['value']
    ])),
    ('With fragment', str(
        Fragment('charFields', 'Character')['name', 'appearsIn']
    )),
    ('Mutation', str(Operation('createHero', operation_type='mutation')(name='Luke')['id'])),
    ('Subscription', str(Operation('hero', operation_type='subscription')(id=1)['name'])),
    ('With variables', str(Operation('hero', vars={'id': 'ID!'})(id='$id')['name'])),
]

print('GraphQL Syntax Validation (parse only)')
print('=' * 60)
all_valid = True
for name, query in test_cases:
    try:
        ast = parse(query)
        print(f'✅ {name}: syntactically valid')
        # Print the query for inspection
        print(f'   Query: {query[:80]}{"..." if len(query) > 80 else ""}')
    except Exception as e:
        print(f'❌ {name}: PARSE ERROR')
        print(f'   Error: {e}')
        print(f'   Query: {query}')
        all_valid = False
    print()

if all_valid:
    print('✅ All queries are syntactically valid GraphQL!')
else:
    print('❌ Some queries have syntax errors')
