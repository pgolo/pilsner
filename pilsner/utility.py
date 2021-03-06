import logging
import os

class Utility():
    """This class is the utility for named entity recognition."""

    def __init__(self, debug_mode=False, verbose_mode=False, callback_status=None, callback_progress=None):
        """Creates Utility instance.

        Args:
            bool *debug_mode*: toggle logger level to INFO
            bool *verbose_mode*: toggle logger level to DEBUG
            function *callback_status*: callback function that message about status can be passed to
            function *callback_progress*: callback function that message about progress can be passed to
        """
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
        self.debug = debug_mode
        self.verbose = verbose_mode
        self.logger = logging.info if self.verbose else logging.debug
        if self.verbose:
            logging.root.setLevel(logging.INFO)
        if self.debug:
            logging.root.setLevel(logging.DEBUG)
            self.logger('Debug mode is on')
        self.callback_status = callback_status
        self.callback_progress = callback_progress
        logging.debug('Utility class has been initialized')

    def __del__(self):
        """Destructor."""
        pass

    def __enter__(self):
        """Enter `with`."""
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """Exit `with`."""
        pass

    def push_message(self, message, callback_function):
        """Passes message to callback_function.

        Args:
            str *message*: message to pass
            function *callback_function*: function to take *message* as an argument
        """
        if callback_function is not None:
            callback_function(message)

    def compile_dict_specs(self, fields):
        """Reshapes list of fields' specifications into dict used by other members of Utility class.
        Returns new dict with specifications.

        Args:
            list *fields*: list of fields (columns)

        Each member of *fields* list must be a dict as follows: {
            'name': 'str name of attribute',
            'include': bool True for including this column else False,
            'delimiter': 'str delimiter in case column stores concatenated lists',
            'id_flag': bool True if column stores entity ID else False,
            'normalizer_flag': bool True if column stores string normalizer tag else False,
            'value_flag': bool True if column stores string label to recognize else False
        }
        """
        logging.debug('Compiling specs')
        specs = {'fields': {}, 'id': None, 'tokenizer': None, 'value': None}
        for i in range(0, len(fields)):
            field = fields[i]
            if not field['include']:
                continue
            specs['fields'][field['name']] = (i, field['delimiter'], field['normalizer_flag'], field['value_flag'])
            if field['id_flag']:
                specs['id'] = specs['fields'][field['name']]
            if field['normalizer_flag']:
                specs['tokenizer'] = specs['fields'][field['name']]
            if field['value_flag']:
                specs['value'] = specs['fields'][field['name']]
        logging.debug('Done compiling specs')
        return specs

    def insert_node(self, label, label_id, entity_id, subtrie, specs, columns, model):
        """Inserts string into trie structure represented by dict object.

        Args:
            str *label*: string to insert
            int *label_id*: ID of the label
            int *entity_id*: ID of the entity given label belongs to
            dict *subtrie*: object representing the trie
            dict *specs*: dictionary specifications
            list *columns*: list of values associated with the entity
            *model*: instance of Model class handling the trie and metadata

        NB: only works with uncompressed trie.
        """
        for character in label:
            if character not in subtrie:
                subtrie[character] = {}
            subtrie = subtrie[character]
        model.store_attributes(label_id, entity_id, subtrie, specs, columns)

    def remove_node(self, model, label, subtrie, prev_length=0):
        """Removes string from trie structure represented by dict object.

        Args:
            Model *model*: instance of Model class handling the trie and metadata
            str *label*: string to remove
            dict *subtrie*: object representing the trie
            int *pref_length*: length of substring found in the trie (used with recursion)

        NB: only works with uncompressed trie.
        """
        if label:
            head, tail = label[0], label[1:]
            current_length = int(len(subtrie))
            next_length, bottom = self.remove_node(model, tail, subtrie=subtrie[head], prev_length=current_length)
            if bottom and next_length > 1:
                bottom = False
            elif bottom and (current_length > 1 or not prev_length):
                del subtrie[head]
                bottom = False
            return current_length, bottom
        else:
            del subtrie[model.ENTITY_KEY]
            return len(subtrie) + 1, True

    def ignore_node(self, model, label):
        """Looks up *label* in a given *model* and hooks a special tag to the leaf in case *label* is found.
        Tagged label will not be racognized by Utility.spot_entities() function.

        Args:
            Model *model*: Model instance to look up
            str *label*: string to tag
        """
        label_length = int(len(label))
        string_so_far = ''
        character_index = 0
        for section in model[model.DICTIONARY_KEY]:
            content = section[model.CONTENT_KEY]
            for tokenizer_key in content:
                trie = content[tokenizer_key]
                for character_index in range(0, label_length):
                    string_so_far += label[character_index]
                    if string_so_far in trie:
                        trie = trie[string_so_far]
                        string_so_far = ''
                if character_index == label_length - 1 and model.ENTITY_KEY in trie and string_so_far == '':
                    trie[model.IGNORE_KEY] = []

    def make_recognizer(self, model, filename, specs, word_separator, item_limit, compressed, column_separator, column_enclosure, tokenizer_option):
        """Reads tab-delimited text file, populates dict objects representing tries, and fills database associated with a given Model instance according to provided specs.
        Returns tuple(list *tries*, dict *line_numbers*) where *tries* are populated dicts representing tries, *line_numbers* is dict that maps line numbers from the text file to internally generated entity IDs.

        Args:
            Model *model*: Model instance to populate
            str *filename*: path and name of tab-delimited text file with the content
            dict *specs*: specifications for columns in the text file
            str *word_separator*: string considered to be the word delimiter
            int *item_limit*: maximum number of rows to stuff in a single trie of a model
            bool *compressed*: whether given tries must be compressed
            str *column_separator*: delimiter to split columns
            str *column_enclosure*: any string that columns are supposed to be trimmed of
            int *tokenizer_option*: tokenizer mode (see documentation for normalization for details)
        """
        # TODO: review for refactoring
        self.logger('Making recognizer using %s' % (filename))
        self.push_message('Making recognizer using %s' % (filename), self.callback_status)
        entity_ids = {}
        line_numbers = {}
        total_bytes = os.path.getsize(filename) + 1
        increment_bytes = int(total_bytes / 100) if total_bytes > 100 else total_bytes
        this_progress_position = 0
        last_progress_position = 0
        if model.connection is not None:
            rows = model.cursor.execute('select 0 where not exists (select name from sqlite_master where type = \'table\' and name = \'attrs\');')
            for _ in rows:
                model.create_recognizer_schema(model.cursor)
                break
        with open(filename, mode='r', encoding='utf8') as f:
            ret = []
            line_count = 0
            line_number = 0
            chars_read = 0
            trie = model.next_trie(specs, compressed, tokenizer_option, word_separator)
            for line in f:
                chars_read += int(len(line))
                this_progress_position = int(chars_read / increment_bytes)
                if this_progress_position != last_progress_position:
                    last_progress_position = this_progress_position
                    self.push_message(int(100 * chars_read / total_bytes), self.callback_progress)
                if item_limit > 0 and line_count == item_limit:
                    packed = model.pack_trie(trie, compressed)
                    ret.append(packed)
                    trie = model.next_trie(specs, compressed, tokenizer_option, word_separator)
                    self.logger('Lines read: %d' % (line_count))
                    line_count = 0
                columns, internal_id = model.get_dictionary_line(specs, entity_ids, line_numbers, line_number, line, column_separator, column_enclosure)
                synonym, normalizer_name = model.get_dictionary_synonym(columns, specs, word_separator, tokenizer_option)
                subtrie = trie[model.CONTENT_KEY][normalizer_name]
                self.insert_node(synonym, line_number, internal_id, subtrie, specs, columns, model)
                line_count += 1
                line_number += 1
        if line_count > 0 and len(trie) > 3:
            packed = model.pack_trie(trie, compressed)
            ret.append(packed)
            self.logger('Lines read: %d' % (line_count))
        if model.connection is not None:
            model.connection.commit()
            model.cursor.execute('create index ix_attrs_n_attr_name_attr_value on attrs (n asc, attr_name asc, attr_value asc);')
        self.logger('Recognizer completed.')
        return ret, line_numbers

    def make_keywords(self, model, filename, specs, line_numbers, word_separator, disambiguate_all, column_separator, column_enclosure, tokenizer_option):
        """Generates dictionary of keywords for a given model using tab-delimited text file that contains entity IDs and synonyms. Typically, for a given model it is the same file `make_recognizer()` function is processing.
        Returns dict object can be plugged into model.

        Args:
            Model *model*: Model instance to use
            str *filename*: path and name of tab-delimited text file with the content
            dict *specs*: specifications for columns in the text file
            dict *line_numbers*: dict that maps line numbers from the text file to internally generated entity IDs
            str *word_separator*: string considered to be the word delimiter
            bool *disambiguate_all*: whether generate keywords for all entities or only for those having conflicting synonyms
            str *column_separator*: delimiter to split columns
            str *column_enclosure*: any string that columns are supposed to be trimmed of
            int *tokenizer_option*: tokenizer mode (see documentation for normalization for details)
        """
        self.logger('Making keywords using %s... ' % (filename))
        self.push_message('Making keywords from {0}'.format(filename), self.callback_status)
        total_bytes = os.path.getsize(filename) + 1
        increment_bytes = int(total_bytes / 100) if total_bytes > 100 else total_bytes
        this_progress_position = 0
        last_progress_position = 0
        entity_ids = {}
        internal_id_map = {}
        synonyms = {}
        with open(filename, mode='r', encoding='utf8') as f:
            line_count = 0
            chars_read = 0
            for line in f:
                chars_read += int(len(line))
                this_progress_position = int(chars_read / increment_bytes)
                if this_progress_position != last_progress_position:
                    last_progress_position = this_progress_position
                    self.push_message(int(100 * chars_read / total_bytes), self.callback_progress)
                columns, internal_id = model.get_dictionary_line(specs, entity_ids, line_numbers, line_count, line, column_separator, column_enclosure)
                internal_id_map[line_count] = internal_id
                synonym = model.get_dictionary_synonym(columns, specs, word_separator, tokenizer_option)[0]
                if synonym not in synonyms:
                    synonyms[synonym] = set()
                synonyms[synonym].add(internal_id)
                line_count += 1
        overlapping_ids = {}
        for s in synonyms:
            if len(synonyms[s]) > 1 or disambiguate_all:
                for internal_id in synonyms[s]:
                    overlapping_ids[internal_id] = set()
        synonyms.clear()
        entity_ids.clear()
        with open(filename, mode='r', encoding='utf8') as f:
            line_count = 0
            for line in f:
                columns, internal_id = model.get_dictionary_line(specs, entity_ids, line_numbers, line_count, line, column_separator, column_enclosure)
                if internal_id in overlapping_ids:
                    synonym = model.get_dictionary_synonym(columns, specs, word_separator, tokenizer_option)[0]
                    tokens = synonym.split(word_separator)
                    overlapping_ids[internal_id] = overlapping_ids[internal_id].union(set(tokens))
                line_count += 1
            # TODO: only leave tokens unique for a given internal_id (?)
        keywords = {model.CONTENT_KEY: overlapping_ids, model.INTERNAL_ID_KEY: internal_id_map}
        self.logger('Done compiling keywords.')
        return keywords

    def compile_model(self, model, filename, fields, word_separator, column_separator, column_enclosure, compressed=True, item_limit=0, tokenizer_option=0, include_keywords=False, disambiguate_all=False):
        """Populates given Model instance with tries and keywords.

        Args:
            Model *model*: Model instance to populate
            str *filename*: path and name of tab-delimited text file with the content
            list *fields*: list of dict objects defining the columns in the text file
            str *word_separator*: string considered to be the word delimiter
            str *column_separator*: delimiter to split columns
            str *column_enclosure*: any string that columns are supposed to be trimmed of
            bool *compressed*: whether given tries must be compressed
            int *item_limit*: maximum number of rows to stuff in a single trie of a model
            int *tokenizer_option*: tokenizer mode (see documentation for normalization for details)
            bool *include_keywords*: whether generate keywords at all or not
            bool *disambiguate_all*: whether generate keywords for all entities or only for those having conflicting synonyms

        Data structure for *fields* argument (also see compile_dict_specs() function):
            [
                {
                    'name': 'str name of attribute',
                    'include': bool True for including this column else False,
                    'delimiter': 'str delimiter in case column stores concatenated lists',
                    'id_flag': bool True if column stores entity ID else False,
                    'normalizer_flag': bool True if column stores string normalizer tag else False,
                    'value_flag': bool True if column stores string label to recognize else False
                }
            ]
        """
        specs = self.compile_dict_specs(fields)
        tries, line_numbers = self.make_recognizer(model, filename, specs, word_separator, item_limit, compressed, column_separator, column_enclosure, tokenizer_option)
        keywords = {model.CONTENT_KEY: {}, model.INTERNAL_ID_KEY: {}}
        if include_keywords:
            keywords = self.make_keywords(model, filename, specs, line_numbers, word_separator, disambiguate_all, column_separator, column_enclosure, tokenizer_option)
        model[model.DICTIONARY_KEY] = tries
        model[model.KEYWORDS_KEY] = keywords
        return True

    def unpack_trie(self, model, packed_trie, compressed):
        """Unpacks compressed trie.
        Returns dict object representing unpacked trie.

        Args:
            Model *model*: Model instance to use
            dict *packed_trie*: trie to process
            bool *compressed*: whether given trie is already compressed
        """
        if not compressed or len(packed_trie) != 1:
            return packed_trie
        branches = [k for k in packed_trie.keys() if k not in [model.ENTITY_KEY]]
        if not branches:
            return packed_trie
        radix = branches[0]
        if len(radix) <= 1:
            return packed_trie
        unpacked_trie = {}
        unpacked_trie_pointer = unpacked_trie
        for character in radix[:-1]:
            unpacked_trie_pointer[character] = {}
            unpacked_trie_pointer = unpacked_trie_pointer[character]
        unpacked_trie_pointer[radix[-1:]] = packed_trie[radix]
        return unpacked_trie

    def unpack_attributes(self, model, cur, leaf_ids, include_query, exclude_query, process_exclude, attrs_out_query):
        """Loads attributes for internal IDs found in a leaf of a trie from a model's database using associated sqlite3.connect.cursor object.
        Returns dict object that maps internal IDs with attributes.

        Args:
            sqlite3.connect.cursor *cur*: cursor to use for throwing queries
            list *leaf_ids*: internal IDs found in a trie leaf
            str *include_query*: part of SQL query to filter something in
            str *exclude_query*: part of SQL query to filter something out
            bint *process_exclude*: whether use *exclude_query* at all
            str *attrs_out_query*: part of SQL query that specifies which attributes to eventually return
        """
        attributes = {}
        if cur is None:
            for n in leaf_ids:
                if n not in attributes:
                    attributes[n] = {}
                if 'ID' not in attributes[n]:
                    attributes[n]['ID'] = []
                attributes[n]['ID'].append(model[model.INTERNAL_ID_KEY][n])
            return attributes
        include_attrs = set()
        exclude_attrs = set()
        for n in leaf_ids:
            rows = cur.execute('select distinct n from attrs where n = %d %s;' % (n, include_query))
            for row in rows:
                include_attrs.add(int(row[0]))
        if process_exclude:
            for n in leaf_ids:
                rows = cur.execute('select distinct n from attrs where n = %d %s;' % (n, exclude_query))
                for row in rows:
                    exclude_attrs.add(int(row[0]))
        ns = include_attrs - exclude_attrs
        for n in ns:
            rows = cur.execute('select attr_name, attr_value from attrs where n = %d%s;' % (n, attrs_out_query))
            if n not in attributes:
                attributes[n] = {}
            for row in rows:
                attr_name, attr_value = str(row[0]), str(row[1])
                if attr_name not in attributes[n]:
                    attributes[n][attr_name] = []
                attributes[n][attr_name].append(attr_value)
        return attributes

    def check_attrs(self, model, trie_leaf, cur, include_query, exclude_query, process_exclude, attrs_out_query):
        """Attaches attributes to a given trie leaf and returns it.

        Args:
            Model *model*: Model instance to use
            dict *trie_leaf*: terminal node of a trie to attach attributes to
            sqlite3.connect.cursor *cur*: cursor to use for throwing queries
            str *include_query*: part of SQL query to filter something in
            str *exclude_query*: part of SQL query to filter something out
            bint *process_exclude*: whether use *exclude_query* at all
            str *attrs_out_query*: part of SQL query that specifies which attributes to eventually return
        """
        this_trie_leaf = dict(trie_leaf)
        this_trie_leaf[model.ATTRS_KEY] = self.unpack_attributes(model, cur, trie_leaf[model.ENTITY_KEY], include_query, exclude_query, process_exclude, attrs_out_query)
        if int(len(this_trie_leaf[model.ATTRS_KEY])) == 0:
            return {}
        return this_trie_leaf

    def spot_entities(self, model, source_string, normalizer_name, include_query='', exclude_query='', process_exclude=False, attrs_out_query='', progress_from=0, progress_to=100):
        """Zooms through a string, finds boundaries of synonyms stored in model's trie, and pulls associated attributes from the storage.
        Returns list(list(tuple *datapoint*)) where datapoint is tuple(list *ids*, dict *attributes*, str *found_synonym*, int *begin*, int *end*) where *ids* are internal IDs of entities, *attributes* is dict {id_entity: {attribute: [value]}}, *found_synonym* is identified substring, *begin* and *end* are indexes of first and last character of recognized substring.

        Args:
            Model *model*: Model instance to use
            str *source_string*: string to parse
            str *normalizer_name*: name of normalization unit (used to pick the right trie from the model; supposed to match normalization unit applied to *source_string*)
            str *include_query*: part of SQL query to filter something in
            str *exclude_query*: part of SQL query to filter something out
            bint *process_exclude*: whether use *exclude_query* at all
            str *attrs_out_query*: part of SQL query that specifies which attributes to eventually return
            int *progress_from*: initial progress value to report
            int *progress_to*: maximum progress value to report

        Data structure for returned value:
            [
                (
                    [int internal_ids],
                    {
                        int internal_id: {str attribute_name: [str attribute_value]}
                    },
                    str identified_label,
                    int unmapped_begin,
                    int unmapped_end
                )
            ]
        """
        # TODO: review for refactoring
        self.logger('Analyzing "%s"... ' % (source_string))
        rets = []
        this_progress_position = 0
        last_progress_position = 0
        total_tries = int(len(model[model.DICTIONARY_KEY]))
        if total_tries == 0:
            return rets
        progress_share = progress_to - progress_from
        trie_increment = int(progress_share / total_tries)
        current_trie_index = 0
        for trie in model[model.DICTIONARY_KEY]:
            ret = []
            word_separator = trie[model.WORD_SEPARATOR_KEY]
            start_index, end_index, string_so_far = -1, 0, ''
            reading_entity = source_string[0:1] != word_separator
            trie_is_compressed = bool(trie[model.COMPRESSED_KEY])
            subtrie = trie[model.CONTENT_KEY][normalizer_name]
            shorter_alternative = None
            current_index = 0
            temporary_index = -1
            total_length = int(len(source_string))
            increment_chars = int(total_length / progress_share) if total_length > progress_share else total_length - 1
            while current_index < total_length:
                this_progress_position = int(current_index / increment_chars / total_tries)
                if this_progress_position != last_progress_position:
                    last_progress_position = this_progress_position
                    self.push_message(int(progress_share * current_index / total_length / total_tries) + current_trie_index * trie_increment + progress_from, self.callback_progress)
                if len(ret) > 0 and current_index < ret[-1][-1]:
                    current_index = ret[-1][-1]
                if not reading_entity: # wait for word separator
                    character = source_string[current_index]
                    start_index = current_index
                    if character == word_separator:
                        reading_entity = True
                        end_index = start_index
                else: # reading entity
                    end_index = current_index
                    character = source_string[current_index]
                    if character == word_separator and model.ENTITY_KEY in subtrie and model.IGNORE_KEY not in subtrie:
                        found_object = self.check_attrs(model, subtrie, model.cursor, include_query, exclude_query, process_exclude, attrs_out_query)
                        if found_object:
                            identified = found_object[model.ENTITY_KEY], found_object[model.ATTRS_KEY]
                            shorter_alternative = (identified[0], identified[1], string_so_far, start_index + 1, end_index)
                    if character in subtrie:
                        if character == word_separator and temporary_index == -1:
                            temporary_index = current_index
                        string_so_far += character
                        subtrie = self.unpack_trie(model, subtrie[character], trie_is_compressed)
                    else:
                        #if everything_or_nothing and current_index == total_length: return []
                        if character == word_separator or current_index == total_length: # - 1:
                            if model.ENTITY_KEY in subtrie and model.IGNORE_KEY not in subtrie:
                                found_object = self.check_attrs(model, subtrie, model.cursor, include_query, exclude_query, process_exclude, attrs_out_query)
                                if found_object:
                                    identified = found_object[model.ENTITY_KEY], found_object[model.ATTRS_KEY]
                                    ret.append((identified[0], identified[1], string_so_far, start_index + 1, end_index))
                                    shorter_alternative = None
                                else:
                                    if shorter_alternative:
                                        ret.append(shorter_alternative)
                                        shorter_alternative = None
                            else:
                                if shorter_alternative:
                                    ret.append(shorter_alternative)
                                    shorter_alternative = None
                            start_index = current_index
                        else:
                            if shorter_alternative:
                                ret.append(shorter_alternative)
                                shorter_alternative = None
                            if temporary_index == -1:
                                reading_entity = False
                            else:
                                current_index = temporary_index
                                temporary_index = -1
                                reading_entity = True
                        string_so_far = ''
                        start_index = current_index
                        subtrie = trie[model.CONTENT_KEY][normalizer_name]
                current_index += 1
            if model.ENTITY_KEY in subtrie and model.IGNORE_KEY not in subtrie:
                found_object = self.check_attrs(model, subtrie, model.cursor, include_query, exclude_query, process_exclude, attrs_out_query)
                if found_object:
                    identified = found_object[model.ENTITY_KEY], found_object[model.ATTRS_KEY]
                    ret.append((identified[0], identified[1], string_so_far, start_index + 1, current_index - 1))
                elif shorter_alternative:
                    ret.append(shorter_alternative)
            elif shorter_alternative:
                ret.append(shorter_alternative)
            rets += ret
            current_trie_index += 1
        self.push_message(progress_to, self.callback_progress)
        self.logger('Done.')
        return rets

    def disambiguate(self, model, recognized, srcs, word_separator):
        """For a list of identified datapoints, weighs context of identified labels that belong to more than 1 entity and keeps heaviest ones.
        Returns filtered list of identified datapoints.

        Args:
            Model *model*: Model instance to use
            list *recognized*: identified datapoints
            list *srcs*: list of all normalized values of original string (using all normalization units applied)
            str *word_separator*: string to be considered a word separator

        Data structure for *recognized* (input) and for returned value:
            [
                (
                    [int internal_ids],
                    {
                        int intenal_id: {str attribute_name: [str attribute_value]}
                    },
                    int mapped_begin,
                    int mapped_end,
                    [int indexes_in_srcs],
                    [
                        (int unmapped_begin, int unmapped_end)
                    ]
                )
            ]
        """
        _recognized = sorted(recognized, key=lambda x: x[2])
        id_list = [[model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY][x] for x in rec[0] if x in model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY]] for rec in _recognized]
        for k in range(len(id_list)):
            ids = id_list[k]
            if len(ids) < 2:
                continue
            si = {}
            src = {}
            ei = {}
            tokens = {}
            s_tokens = {}
            for j in range(len(ids)):
                si[ids[j]] = 0
                src[ids[j]] = srcs[_recognized[k][4][j]]
                ei[ids[j]] = len(src[ids[j]])
                if k > 0:
                    # take map from normalizer [k-1] and remap location on map of normalizer[k] as a boundary
                    if _recognized[k][7][ids[j]][_recognized[k-1][3]][1] > si[ids[j]]:
                        si[ids[j]] = _recognized[k][7][ids[j]][_recognized[k-1][3]][1]
                if k < len(id_list) - 1:
                    # take map from normalizer [k+1] and remap location on map of normalizer[k] as a boundary
                    if _recognized[k][7][ids[j]][_recognized[k+1][2]][0] < ei[ids[j]]:
                        ei[ids[j]] = _recognized[k][7][ids[j]][_recognized[k+1][2]][0]
                tokens[ids[j]] = src[ids[j]][si[ids[j]]:ei[ids[j]]]
                s_tokens[ids[j]] = set(tokens[ids[j]].split(word_separator))
            tmp = {i: model[model.KEYWORDS_KEY][model.CONTENT_KEY][i] if i in model[model.KEYWORDS_KEY][model.CONTENT_KEY] else set() for i in ids}
            kwd = {i: tmp[i] - tmp[j] for i in tmp for j in tmp if j != i}
            winner_score = 0
            winner_id = set()
            kwd_score = {}
            for i in kwd:
                kwd_score[i] = len(kwd[i].intersection(s_tokens[i]))
                if kwd_score[i] > winner_score:
                    winner_score = kwd_score[i]
                    winner_id.clear()
                if kwd_score[i] == winner_score:
                    winner_id.add(i)
            _recognized[k] = tuple([[x for x in _recognized[k][0] if model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY][x] in winner_id]] + [{x: _recognized[k][1][x] for x in _recognized[k][1] if model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY][x] in winner_id}] + list(_recognized[k])[2:])
        return _recognized

    def flatten_layers(self, model, layers):
        """Flattens list of lists of identified datapoints, invokes disambiguation, remaps label locations to the original string, reshapes the output.
        Returns list(tuple *datapoint*) where *datapoint* is tuple(list *ids*, dict *attributes*, int *begin*, int *end*).

        Args:
            Model *model*: Model instance to use
            list *layers*: list of identified datapoints
        
        Data structure for *layers* (input):
            [
                (
                    (
                        [int normalized_positions], # indexes are original positions
                        [[int min_original_position, int max_original_position]], # indexes are normalized positions
                    ),
                    [
                        (
                            [int internal_ids],
                            {int internal_id: {str attribute_name: [str attribute_value]}},
                            str identified_label,
                            int unmapped_begin,
                            int unmapped_end
                        )
                    ],
                    str parsed_normalized_string
                )
            ]
        
        Returned data structure:
            [
                (
                    [int internal_ids],
                    {int internal_id: {str attribute_name: [str attribute_value]}},
                    int mapped_begin,
                    int mapped_end
                )
            ]
        """
        spans = {}
        srcs = []
        for i in range(0, len(layers)):
            layer = layers[i]
            _map = layer[0][0]
            _r_map = layer[0][1]
            _recognized = layer[1]
            _src = layer[2]
            srcs.append(_src)
            for span in _recognized:
                location = tuple([_map[span[3]], _map[span[4]]])
                if location not in spans:
                    spans[location] = []
                spans[location].append(tuple([span[0], span[1], [i] * len(span[0]), span[3], span[4], _map, _r_map]))
        new_layers = []
        for location in spans:
            new_left = location[0]
            new_right = location[1]
            new_ids = []
            new_attrs = {}
            new_srcids = []
            new_locations = []
            new_map = {}
            new_r_map = {}
            for item in spans[location]:
                new_ids += item[0]
                new_attrs = {**new_attrs, **item[1]}
                if model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY]:
                    new_srcids += item[2]
                    new_locations.append(tuple([item[3], item[4]]))
                    new_map.update({model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY][k]: item[5] for k in item[0]})
                    new_r_map.update({model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY][k]: item[6] for k in item[0]})
            new_layers.append(tuple([new_ids, new_attrs, new_left, new_right, new_srcids, new_locations, new_map, new_r_map]))
        if model[model.KEYWORDS_KEY][model.INTERNAL_ID_KEY]:
            new_layers = self.disambiguate(model, new_layers, srcs, ' ')
            pass
        ret = [x[0:4] for x in new_layers]
        return ret

    def flatten_spans(self, spans):
        """Transforms list of normalized tuples into one dict.
        Returns dict {(int *begin*, int *end*): {str *attribute_name*: {str *attribute_value*}}}.

        Args:
            list *spans*: list of identified datapoints, as returned by flatten_layers() function
        """
        ret = {}
        all_entries = []
        for span in spans:
            _ids, _content, _left, _right = span[0], span[1], span[2], span[3]
            for _id in _ids:
                _attrs = _content[_id]
                for _attr_name in _attrs:
                    for _attr_value in _attrs[_attr_name]:
                        all_entries.append(tuple([_left, _right, _attr_name, _attr_value]))
        if len(all_entries) > 0:
            all_entries = sorted(sorted(all_entries, key=lambda x: -x[1]), key=lambda x: x[0])
            filtered_entries = [all_entries[0]]
            for i in range(1, len(all_entries)):
                q = all_entries[i]
                if (filtered_entries[-1][0] <= q[0] < filtered_entries[-1][1] and filtered_entries[-1][0] < q[1] < filtered_entries[-1][1]) or (filtered_entries[-1][0] < q[0] < filtered_entries[-1][1] and filtered_entries[-1][0] < q[1] <= filtered_entries[-1][1]):
                    continue
                filtered_entries.append(q)
            for entry in filtered_entries:
                _location, _attr_name, _attr_value = tuple([int(entry[0]), int(entry[1])]), str(entry[2]), str(entry[3])
                if _location not in ret:
                    ret[_location] = {}
                if _attr_name not in ret[_location]:
                    ret[_location][_attr_name] = set()
                ret[_location][_attr_name].add(_attr_value)
        return ret

    def reduce_spans(self, segments):
        """Reduces overlapping segments by keeping longer ones or leftmost ones in case of equal length.
        Returnes reduced list of tuples [(int *begin*, int *end*)].

        Args:
            set *segments*: set of tuples(int *begin*, int *end*)
        """
        def intersects(segment1, segment2):
            return segment2[0] >= segment1[0] and segment2[0] <= segment1[1]
        def length(segment):
            return segment[1] - segment[0]
        sorted_segments = [[x] for x in sorted(sorted(segments, key=lambda x: x[1] - x[0]), key=lambda x: x[0])]
        for i in range(len(sorted_segments) - 1):
            if len(sorted_segments[i]) == 0:
                continue
            if intersects(sorted_segments[i][0], sorted_segments[i+1][0]):
                if length(sorted_segments[i][0]) >= length(sorted_segments[i+1][0]):
                    sorted_segments[i+1] = sorted_segments[i]
                    sorted_segments[i] = []
                elif length(sorted_segments[i][0]) < length(sorted_segments[i+1][0]):
                    recovered = False
                    for j in range(1, len(sorted_segments[i])):
                        if not intersects(sorted_segments[i][j], sorted_segments[i+1][0]):
                            sorted_segments[i][0] = sorted_segments[i][j]
                            recovered = True
                            break
                    if not recovered:
                        sorted_segments[i+1] += sorted_segments[i]
                        sorted_segments[i] = []
        ret = [x[0] for x in sorted_segments if len(x) > 0]
        return ret

    def parse(self, model, source_string, attrs_where=None, attrs_out=None):
        """Wraps around all functions that normalize string, spot entities, disambiguate, and post-process the output.
        Returns dict {(int *begin*, int *end*): {str *attribute_name*: {str attribute_value}}}.

        Args:
            Model *model*: Model instance to use
            str *source_string*: source string to parse
            dict *attrs_where*: specifications for filtering model's data used for recognition
            list *attrs_out*: list of attribute names to output

        Data structure for *attrs_where*:
            {
                '+': {str attribute_name: {str attribute_value}}, # if indicated, only entities that have these attributes will be considered
                '-': {str attribute_name: {str attribute_value}} # if indicated, entities that have these attributes will not be considered
            }
        """
        attributes = attrs_where
        if attributes is None:
            attributes = {}
        for action in ['+', '-']:
            if action not in attributes:
                attributes[action] = {}
        process_exclude = False
        include_set, include_query = set(), ''
        for attr_name in attributes['+']:
            for attr_value in attributes['+'][attr_name]:
                include_set.add('(attr_name = \'' + attr_name.replace('\'', '\'\'') + '\' and attr_value = \'' + attr_value.replace('\'', '\'\'') + '\')')
        if len(include_set) > 0:
            include_query = 'and (' + ' or '.join(include_set) + ')'
        exclude_set, exclude_query = set(), ''
        for attr_name in attributes['-']:
            for attr_value in attributes['-'][attr_name]:
                exclude_set.add('(attr_name = \'' + attr_name.replace('\'', '\'\'') + '\' and attr_value = \'' + attr_value.replace('\'', '\'\'') + '\')')
        if len(exclude_set) > 0:
            exclude_query = 'and (' + ' or '.join(exclude_set) + ')'
            process_exclude = True
        attrs_out_query = ''
        if attrs_out is not None and len(attrs_out) > 0:
            attrs_out_query = ' and attr_name in (\'%s\')' % ('\', \''.join([x.replace('\'', '\'\'') for x in attrs_out]))
        self.logger('Parsing text...')
        self.push_message('Parsing text', self.callback_status)
        rets = []
        total_normalizers = int(len(model[model.NORMALIZER_KEY]))
        try:
            assert total_normalizers > 0, 'Model does not have normalization units'
        except Exception as e:
            model.destroy()
            raise e
        spot_progress_share = int(100 / total_normalizers)
        current_normalizer_index = 0
        for normalizer_name in model[model.NORMALIZER_KEY]:
            normalized_string = model[model.NORMALIZER_KEY][normalizer_name].normalize(source_string, model[model.WORD_SEPARATOR_KEY], model[model.TOKENIZER_OPTION_KEY])
            character_map = model[model.NORMALIZER_KEY][normalizer_name].result['map']
            r_character_map = model[model.NORMALIZER_KEY][normalizer_name].result['r_map']
            progress_from = current_normalizer_index * spot_progress_share
            progress_to = (current_normalizer_index + 1) * spot_progress_share
            parsed = self.spot_entities(model, normalized_string, normalizer_name, include_query, exclude_query, process_exclude, attrs_out_query, progress_from=progress_from, progress_to=progress_to)
            rets.append(((character_map, r_character_map), parsed, normalized_string))
            current_normalizer_index += 1
        layers = self.flatten_layers(model, rets)
        spans = self.flatten_spans(layers)
        locations = self.reduce_spans(set(spans.keys()))
        ret = {location: spans[location] for location in locations}
        self.logger('Done parsing text.')
        return ret
