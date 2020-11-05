import cython

cdef class Model(dict):
    
    cdef public str CONTENT_KEY
    cdef public str SPECS_KEY
    cdef public str COMPRESSED_KEY
    cdef public str TOKENIZER_OPTION_KEY
    cdef public str WORD_SEPARATOR_KEY
    cdef public str IGNORE_KEY
    cdef public str ENTITY_KEY
    cdef public str ATTRS_KEY
    cdef public str INTERNAL_ID_KEY
    cdef public str DICTIONARY_KEY
    cdef public str KEYWORDS_KEY
    cdef public str NORMALIZER_KEY
    cdef public str DEFAULT_NORMALIZER_KEY
    cdef public str DATASOURCE_KEY
    cdef public str DEFAULT_DATASOURCE_PATH
    cdef public str DEFAULT_DATASOURCE_FILENAME
    cdef public str DEFAULT_DATASOURCE
    cdef public str DEFAULT_WORD_SEPARATOR
    cdef public int DEFAULT_TOKENIZER_OPTION
    cdef public connection
    cdef public cursor
    cdef public normalizer_map
    cdef public sic_builder

    @cython.locals(
        normalizers=cython.dict,
        dictionary_number=cython.int
    )
    cpdef bint save(
        self,
        str filename
    )

    @cython.locals(
        normalizers=cython.dict,
        _filename=cython.str,
        dictionary=cython.dict,
        keywords=cython.dict
    )
    cpdef bint load(
        self,
        str filename
    )

    cpdef bint add_normalizer(
        self,
        str normalizer_name,
        str filename,
        bint default=*
    )

    cpdef bint create_recognizer_schema(
        self,
        cursor
    )

    @cython.locals(
        children=cython.dict,
        child_count=cython.int,
        key=cython.str,
        next_prefix=cython.str,
        comp_key=cython.str,
        comp_children=cython.dict
    )
    cpdef tuple pack_subtrie(
        self,
        trie,
        bint compressed,
        str prefix
    )

    @cython.locals(
        ret=cython.dict,
        normalizer_name=cython.str,
        packed=cython.dict
    )
    cpdef dict pack_trie(
        self,
        dict trie,
        bint compressed
    )

    @cython.locals(
        k=cython.str
    )
    cpdef store_attributes(
        self,
        int line_number,
        int internal_id,
        dict subtrie,
        dict specs,
        list columns
    )

    @cython.locals(
        columns=cython.list,
        internal_id=cython.int,
        entity_id=cython.str
    )
    cpdef tuple get_dictionary_line(
        self,
        dict specs,
        dict entity_ids,
        dict line_numbers,
        int line_number,
        str line,
        str column_separator,
        str column_enclosure
    )

    @cython.locals(
        synonym=cython.str,
        normalizer_name=cython.str
    )
    cpdef tuple get_dictionary_synonym(
        self,
        list columns,
        dict specs,
        str word_separator,
        int tokenizer_option=*
    )

    @cython.locals(
        new_trie=cython.dict
    )
    cpdef dict next_trie(
        self,
        dict specs,
        bint compressed,
        int tokenizer_option,
        str word_separator
    )
