# Either install pilsner package to the environment first,
# or run this from project's root

import sys; sys.path.insert(0, '')

# Import pilsner
import pilsner

# Initialize Model class
m = pilsner.Model()

# Add normalization units
m.add_normalizer('default', 'misc/example/default_normalizer.xml')
m.add_normalizer('custom', 'misc/example/custom_normalizer.xml')

# Map names of normalization units to some string values
m.normalizer_map = {
    'animal': 'default',
    'plant': 'custom'
}

# Initialize Utility class
r = pilsner.Utility()

# Provide table definition for misc/example/living_fileds.txt file
fields = [
    {
        'name': 'type',             # attribute name is 'type'
        'include': True,            # include this column
        'delimiter': None,          # no delimiter (single value per row)
        'id_flag': False,           # entity IDs are not in this column
        'normalizer_flag': True,    # tags for normalization units are in this column
        'value_flag': False         # string labels (synonyms) are not in this column
    },
    {
        'name': 'id',               # attribute name is 'id'
        'include': True,
        'delimiter': None,
        'id_flag': True,            # entity IDs are in this column
        'normalizer_flag': False,
        'value_flag': False
    },
    {
        'name': 'label',            # attribute name is 'label'
        'include': True,
        'delimiter': None,
        'id_flag': False,
        'normalizer_flag': False,
        'value_flag': True          # string labels (synonyms) are in this column
    },
    {
        'name': 'habitat',          # attribute name is 'habitat'
        'include': True,
        'delimiter': ',',           # multiple values delimited with ',' can be stored in a single row
        'id_flag': False,
        'normalizer_flag': False,
        'value_flag': False
    }
]

# Populate Model instance with data from misc/example/living_things.txt file
r.compile_model(
    model=m,
    filename='misc/example/living_things.txt',
    fields=fields,
    word_separator=' ',
    column_separator='\t',
    column_enclosure='\n',
    include_keywords=True
)

# Save Model instance to disk
m.save('misc/example/living_things')

# Load Model instance from disk
m = pilsner.Model('misc/example/living_things')

# Parse string
text_to_parse = '''
Little mouse is not recognized and is not frightened by big scary eagle.
Daniorerio also does not care much about water lilies, though both are recognized.
'''
parsed = r.parse(
    model=m,
    source_string=text_to_parse,
    attrs_where={
        '+': {'habitat': {'air', 'ocean'}} # only consider items with these values in 'habitat' column
    },
    attrs_out=['type'] # for each spotted entity, only output 'type' attribute
)

# Print out the result: recognized are 'big eagle', 'danio rerio', 'water lily'.
print(parsed)
