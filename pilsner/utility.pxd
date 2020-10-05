import cython

cdef class Utility():

    cdef public bint debug
    cdef public bint verbose
    cdef public logger
    cdef public callback_status
    cdef public callback_progress

    cpdef push_message(
        self,
        message,
        callback_function
    )

    @cython.locals(
        specs=cython.dict,
        i=cython.int,
        field=cython.dict
    )
    cpdef dict compile_dict_specs(
        self,
        list fields
    )

    @cython.locals(
        character=cython.str
    )
    cpdef insert_node(
        self,
        str label,
        int label_id,
        int entity_id,
        dict subtrie,
        dict specs,
        list columns,
        model
    )

    @cython.locals(
        head=cython.str,
        tail=cython.str,
        current_length=cython.int,
        next_length=cython.int,
        bottom=cython.bint
    )
    cpdef tuple remove_node(
        self,
        model,
        str label,
        dict subtrie,
        int prev_length=*
    )

    @cython.locals(
        entity_ids=cython.dict,
        line_numbers=cython.dict,
        total_bytes=cython.int,
        increment_bytes=cython.int,
        this_progress_position=cython.int,
        last_progress_position=cython.int,
        ret=cython.list,
        line_count=cython.int,
        line_number=cython.int,
        chars_read=cython.int,
        trie=cython.dict,
        line=cython.str,
        packed=cython.dict,
        columns=cython.list,
        internal_id=cython.int,
        synonym=cython.str,
        subtrie=cython.dict
    )
    cpdef tuple make_recognizer(
        self,
        model,
        str filename,
        dict specs,
        str word_separator,
        int item_limit,
        bint compressed,
        str column_separator,
        str column_enclosure,
        int tokenizer_option
    )

    @cython.locals(
        total_bytes=cython.int,
        increment_bytes=cython.int,
        this_progress_position=cython.int,
        last_progress_position=cython.int,
        entity_ids=cython.dict,
        internal_id_map=cython.dict,
        synonyms=cython.dict,
        line_count=cython.int,
        chars_read=cython.int,
        line=cython.str,
        columns=cython.list,
        internal_id=cython.int,
        synonym=cython.str,
        overlapping_ids=cython.dict,
        s=cython.str,
        tokens=cython.list,
        keywords=cython.dict
    )
    cpdef dict make_keywords(
        self,
        model,
        str filename,
        dict specs,
        dict line_numbers,
        str word_separator,
        bint disambiguate_all,
        str column_separator,
        str column_enclosure,
        int tokenizer_option
    )

    @cython.locals(
        tries=cython.list,
        line_numbers=cython.dict,
        keywords=cython.dict
    )
    cpdef bint compile_model(
        self,
        model,
        str filename,
        dict specs,
        str word_separator,
        str column_separator,
        str column_enclosure,
        bint compressed=*,
        int item_limit=*,
        int tokenizer_option=*,
        bint include_keywords=*,
        bint disambiguate_all=*
    )

    @cython.locals(
        branches=cython.list,
        radix=cython.str,
        unpacked_trie=cython.dict,
        character=cython.str,
        unpacked_trie_pointer=cython.dict
    )
    cpdef dict unpack_trie(
        self,
        model,
        dict packed_trie,
        bint compressed
    )

    @cython.locals(
        attributes=cython.dict,
        include_attrs=cython.set,
        exclude_attrs=cython.set,
        n=cython.int,
        ns=cython.set,
        attr_name=cython.str,
        attr_value=cython.str
    )
    cpdef dict unpack_attributes(
        self,
        cur,
        list lead_ids,
        str include_query,
        str exclude_query,
        bint process_exclude,
        str attrs_out_query
    )

    cpdef dict check_attrs(
        self,
        model,
        dict trie_leaf,
        cur,
        str include_query,
        str exclude_query,
        bint process_exclude,
        str attrs_out_query
    )

    @cython.locals(
        rets=cython.list,
        this_progress_position=cython.int,
        last_progress_position=cython.int,
        total_tries=cython.int,
        progress_share=cython.int,
        trie_increment=cython.int,
        current_trie_index=cython.int,
        trie=cython.dict,
        ret=cython.list,
        word_separator=cython.str,
        start_index=cython.int,
        end_index=cython.int,
        string_so_far=cython.str,
        reading_entity=cython.bint,
        trie_is_compressed=cython.bint,
        subtrie=cython.dict,
        shorter_alternative=cython.tuple,
        current_index=cython.int,
        temporary_index=cython.int,
        total_length=cython.int,
        increment_chars=cython.int,
        character=cython.str,
        found_object=cython.dict,
        identified=cython.tuple
    )
    cpdef list spot_entities(
        self,
        model,
        str source_string,
        str normalizer_name,
        str include_query=*,
        str exclude_query=*,
        bint process_exclude=*,
        str attrs_out_query=*,
        int progress_from=*,
        int progress_to=*
    )

    @cython.locals(
        _recognized=cython.list,
        id_list=cython.list,
        k=cython.int,
        ids=cython.list,
        si=cython.dict,
        src=cython.dict,
        ei=cython.dict,
        tokens=cython.dict,
        s_tokens=cython.dict,
        j=cython.int,
        tmp=cython.dict,
        kwd=cython.dict,
        winner_score=cython.int,
        winner_id=cython.set,
        kwd_score=cython.dict,
        i=cython.int
    )
    cpdef list disambiguate(
        self,
        model,
        list recognized,
        list srcs,
        str word_separator
    )

    @cython.locals(
        spans=cython.dict,
        srcs=cython.list,
        i=cython.int,
        layer=cython.tuple,
        _map=cython.list,
        _r_map=cython.list,
        _recognized=cython.list,
        _src=cython.str,
        span=cython.tuple,
        location=cython.tuple,
        new_layers=cython.list,
        new_left=cython.int,
        new_right=cython.int,
        new_ids=cython.list,
        new_attrs=cython.dict,
        new_srcids=cython.list,
        new_locations=cython.list,
        new_map=cython.dict,
        new_r_map=cython.dict,
        item=cython.tuple,
        ret=cython.list
    )
    cpdef list flatten_layers(
        self,
        model,
        list layers
    )

    @cython.locals(
        ret=cython.dict,
        all_entries=cython.list,
        span=cython.tuple,
        _ids=cython.list,
        _content=cython.dict,
        _left=cython.int,
        _right=cython.int,
        _id=cython.int,
        _attrs=cython.dict,
        _attr_name=cython.str,
        _attr_value=cython.str,
        filtered_entries=cython.list,
        i=cython.int,
        q=cython.tuple,
        entry=cython.tuple,
        _location=cython.tuple
    )
    cpdef dict flatten_spans(
        self,
        list spans
    )

    @cython.locals(
        sorted_segments=cython.list,
        i=cython.int,
        j=cython.int,
        recovered=cython.bint,
        ret=cython.list
    )
    cpdef list reduce_spans(
        self,
        set segments
    )

    @cython.locals(
        attributes=cython.dict,
        action=cython.str,
        process_exclude=cython.bint,
        include_set=cython.set,
        include_query=cython.str,
        attr_name=cython.str,
        attr_value=cython.str,
        exclude_set=cython.set,
        exclude_query=cython.str,
        attrs_out_query=cython.str,
        rets=cython.list,
        total_normalizers=cython.int,
        spot_progress_share=cython.int,
        current_normalizer_index=cython.int,
        normalizer_name=cython.str,
        normalized_string=cython.str,
        character_map=cython.list,
        r_character_map=cython.list,
        progress_from=cython.int,
        progress_to=cython.int,
        parsed=cython.list,
        layers=cython.list,
        spans=cython.dict,
        locations=cython.list,
        ret=cython.dict
    )
    cpdef dict parse(
        self,
        model,
        str source_string,
        dict attrs_where=*,
        list attrs_out=*
    )
