# pilsner

Python implemented library servicing named entity recognition

[![pypi][pypi-img]][pypi-url]

[pypi-img]: https://img.shields.io/pypi/v/pilsner?style=plastic
[pypi-url]: https://pypi.org/project/pilsner/

## 1. Purpose

This library is Python implementation of toolkit for dictionary based named entity recognition. It is intended to store any thesaurus in a trie-like structure and identify any of stored synonyms in a string.

## 2. Installation and dependencies

```bash
pip install pilsner
```

`pilsner` is tested in Python 3.6, 3.7, and 3.8.

The only dependency is `sic` package. While it can be automatically installed at the time of `pilsner` installation, manual installation of `sic` beforehand might also be considered (see benchmark of cythonized vs pure Python implementation in `sic` docimentation, [https://pypi.org/project/sic/](https://pypi.org/project/sic/)).

## 3. Diagram

Image

## 4. Usage

```python
import pilsner
```

### 4.1. Initialize model

```python
m = pilsner.Model()
```

### 4.2. Add string normalization units

String normalization is done by `sic` component.

### 4.3. Add dictionary

Blah

### 4.4. Initialize utility

```python
r = pilsner.Recognizer()
```

### 4.5. Compile model

Blah

### 4.6. Save model

Blah

### 4.7. Load model

Blah

### 4.8. Parse string

Blah

## 5. Example

Blah
