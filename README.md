# pilsner

Python implemented library servicing named entity recognition

[![pypi][pypi-img]][pypi-url]

[pypi-img]: https://img.shields.io/pypi/v/pilsner?style=plastic
[pypi-url]: https://pypi.org/project/pilsner/

## 1. Purpose

This library is Python implementation of toolkit for dictionary based named
entity recognition. It is intended to store any thesaurus in a trie-like
structure and identify any of stored synonyms in a string.

## 2. Installation and dependencies

```bash
pip install pilsner
```

`pilsner` is tested in Python 3.6, 3.7, and 3.8.

The only dependency is `sic` package. While it can be automatically installed
at the time of `pilsner` installation, manual installation of `sic` beforehand
might also be considered (see benchmark of cythonized vs pure Python
implementation in `sic` docimentation,
[https://pypi.org/project/sic/](https://pypi.org/project/sic/)).

## 3. Diagram

`pilsner` consists of two major components: `Model` and `Utility`. `Model`
class provides storage for the dictionary and string normalization rules, as
well as low-level methods for populating this storage. `Utility` class provides
high-level methods for storing and retrieving data to/from `Model` instance.

![Diagram](https://github.com/pgolo/pilsner/blob/master/misc/pilsner-diagram.svg)

## 4. Usage

```python
import pilsner
```

### 4.1. Initialize model

- To initialize empty model:

```python
m = pilsner.Model()
```

- To specify path to temporary database for empty model:

```python
m = pilsner.Model(storage_location='path/to/database.file')
```

- To create empty model that uses database created in memory rather than on
disk:

```python
m = pilsner.Model(storage_location=':memory:')
```

> If database is created in memory, the model cannot be later saved on disk
(can only be used instantly).

- To load model from disk:

```python
m = pilsner.Model(filename='path/to/model')
```

> More on how model is saved to and loaded from disk - see
[4.6. Save model](#46-save-model) and [4.7. Load model](#47-load-model).

### 4.2. Add string normalization units

- Depending on the dictionary and nature of the text supposed to be parsed,
string normalization might not be required at all, and nothing specific is to
be done here in such case.
- Without string normalization, synonyms from the dictionary will be stored as
they are and looked up by recognizer case-sensitively.
- To add a single normalization unit:

```python
# Assuming m is pilsner.Model instance:
m.add_normalizer(
    normalizer_name='normalizer_tag',
    filename='path/to/normalizer_config.xml'
)
```

> String normalization is technically done by `sic` component. See
> documentation for `sic` at
> [https://pypi.org/project/sic/](https://pypi.org/project/sic/) to learn how
> to design normalizer config.

- Model can embed more than one normalization unit.
- Default normalization unit for the model is the one added first or the last
one added with parameter `default` set to `True`.
- Having multiple normalization units in one model makes perfect sense when the
stored dictionary contains synonyms of different nature that should be
normalized in different ways (for example, abbreviations probably should not
get normalized at all, while other synonyms might include tokens or punctuation
marks that should not affect entity recognition). For that purpose, Model class
includes `normalizer_map` dict that is supposed to map names of added
normalization units to values in specific field in a dictionary designating the
way a synonym should be normalized (tokenizer field, or tokenizer column):

```python
# Assuming m is pilsner.Model instance:
m.normalizer_map = {
    'synonym_type_1': 'normalizer_1',
    'synonym_type_2': 'normalizer_2'
}
```

> The snippet above instructs `pilsner` to normalize synonyms that have
> `synonym_type_1` value in `tokenizer` column with `normalizer_1`
> normalization unit, and normalize synonyms that have `synonym_type_2` value
> in `tokenizer` column with `normalizer_2` normalization unit. For more about
> fields in a dictionary, see [4.4. Define dictionary](#44-define-dictionary).

### 4.3. Initialize utility

- To load dictionary into `Model` instance, as well as to parse text, the
`Utility` instance is required:

```python
r = pilsner.Utility()
```

### 4.4. Define dictionary

- Source dictionary for `pilsner` must be delimited text file.
- Along with the source dictionary, specifications of the columns (fields) must
be provided as list where each item corresponds to a column (from left to
right). Each item in this list must be a dict object with string keys `name`,
`include`, `delimiter`, `id_flag`, `normalizer_flag`, and `value_flag`, so
that:
  - `field['name']` is a string for column title;
  - `field['include']` is a boolean that must be set to `True` for the column
  to be included in the model, otherwise `False`;
  - `field['delimiter']` is a string that is supposed to split single cell into
  list of values if the column holds concatenated lists rather than individual
  values;
  - `field['id_flag]` is a boolean that must be set to `True` if the column is
  supposed to be used for grouping synonyms (generally, entity ID is such
  column), otherwise `False`;
  - `field['normalizer_flag']` is a boolean that must be set to `True` if the
  column holds indication on what normalization unit must be applied to this
  particular synonym, otherwise `False`;
  - `field['value_flag']` is a boolean that must be set to `True` if the column
  holds synonyms that are supposed to be looked up when parsing a text,
  otherwise `False`.

> If dictionary has a column flagged with `normalizer_flag`, synonym in each
> row will be normalized with string normalization unit which name is mapped on
> value in this column using `pilsner.Model.normalizer_map` dict. If value is
> not among `pilsner.Model.normalizer_map` keys, default normalization unit
> will be used.

### 4.5. Compile model

- To store dictionary in `Model` instance, method `compile_model` of `Utility`
instance must be called with the following required parameters:
  - `model`: pointer to initilized `Model` instance;
  - `filename`: string with path and filename of source dictionary;
  - `fields`: dict object with definitions of columns (see
  [4.4. Define dictionary](#44-define-dictionary));
  - `word_separator`: string defining what is to be considered word separator
  (generally, it should be whitespace);
  - `column_separator`: string defining what is to be considered column
  separator (e.g. `\t` for tab-delimited file);
  - `column_enclosure`: string defining what is to be stripped away from cell
  after row has been split into columns (typically, it should be `\n` for new
  line character to be trimmed from the rightmost column).

```python
# Assuming m is pilsner.Model instance and r is pilsner.Utility instance:
r.compile_model(
    model=m,
    filename='path/to/dictionary_in_a_text_file.txt',
    fields=fields,
    word_separator=' ',
    column_separator='\t',
    column_enclosure='\n'
)
```

- To review optional parameters, see comments in the code.

### 4.6. Save model

- If `Model` instance has compiled dictionary, and if database location for the
`Model` instance is not explicitly set to `':memory:'`, the data such instance
is holding can be saved to disk:

```python
# Assuming m is pilsner.Model instance
m.save('path/to/model_name')
```

- The snippet above will write the following files:
  - `path/to/model_name.attributes`: database with attributes (fields from the
  dictionary that are not synonyms);
  - `path/to/model_name.keywords`: keywords used for disambiguation;
  - `path/to/model_name.normalizers`: string normalization units;
  - `path/to/model_name.0.dictionary`: trie with synonyms;
  - `path/to/model_name.<N>.dictionary`: additional tries with synonyms (`<N>`
  being integer number of a trie) in case more than one trie was created (see
  comments in the code - `pilsner.Utility.compile_model` method, `item_limit`
  parameter).

### 4.7. Load model

- To initialize new `Model` instance using previously saved data:

```python
m = pilsner.Model(filename='path/to/model_name')
```

- Alternatively, data can be loaded to previously initialized `Model` instance:

```python
m = pilsner.Model()
m.load('path/to/model_name')
```

- In both cases, the program will look for the following files:
  - `path/to/model_name.attributes`: database with attributes (fields from the dictionary that are not synonyms);
  - `path/to/model_name.keywords`: keywords used for disambiguation;
  - `path/to/model_name.normalizers`: string normalization units;
  - `path/to/model_name.<N>.dictionary`: tries with synonyms (`<N>` being
  integer).

### 4.8. Parse string

- To parse a string without filtering out any synonyms and output all
attributes of spotted entities:

```python
# Assuming m is pilsner.Model instance, r is pilsner.Utility instance,
# and text_to_parse is string to parse
parsed = r.parse(
    model=m,
    source_string=text_to_parse
)
```

- The output will be dict object where keys are tuples for location of spotted
entity in a string (begin, end) and values are dicts for attributes that are
associated with identified entity (`{'attribute_name': {attribute_values}}`).
- To ignore entity by its label rather than some of its attributes, compiled
model can be adjusted using `pilsnet.Utility.ignore_node()` method:

```python
# Assuming m is pilsner.Model instance, r is pilsner.Utility instance
r.ignore_node(
  model=m,
  label='irrelevant substring'
)
# substring 'irrelevant substring' will not be found by pilsner.Utility.parse()
# even if it is present in the model
```

- For details about optional parameters, see comments in the code -
`pilsner.Utility.parse()` function.

## 5. Example

Everything written above is put together in example code,
see **/misc/example/** directory in the project's repository.
