import sys
import unittest

class TestUtility(unittest.TestCase):

    def setUp(self):
        self.utility = pilsner.Utility()
        self.model = pilsner.Model()

    def tearDown(self):
        del(self.utility)
        self.model.destroy()
        del(self.model)

    def compile_test_model(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        model = self.model
        model.add_normalizer('t1', 'test/assets/tokenizer1.xml')
        model.add_normalizer('t2', 'test/assets/tokenizer2.xml')
        model.normalizer_map = {
            'tokenizer1': 't1',
            'tokenizer2': 't2'
        }
        compiled = self.utility.compile_model(model=model, filename='test/assets/sample_dictionary.txt', fields=fields, word_separator=' ', column_separator='\t', column_enclosure='', include_keywords=True)
        return compiled, model

    def test_init(self):
        r = pilsner.Utility()
        assert 'r' in locals(), 'Instance of Utility class has not been created'
        assert type(r) == pilsner.Utility, 'Utility is supposed to have pilsner.Utility type, but has %s instead' % (str(type(r)))

    def test_del(self):
        r = pilsner.Utility()
        del(r)
        assert 'r' not in locals(), 'Instance of Utility class has not been destroyed'

    def test_push_message(self):
        messages = []
        def callback_function(message):
            messages.append(message)
        self.utility.push_message('message 1', callback_function)
        self.utility.push_message('message 2', callback_function)
        expected = ['message 1', 'message 2']
        assert messages == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(messages))

    def test_compile_dict_specs(self):
        fields = [
            {'name': 'column 1', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'column 2', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'column 3', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'column 4', 'include': False, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'column 5', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.utility.compile_dict_specs(fields)
        expected = {
            'fields': {
                'column 1': (0, None, True, False),
                'column 2': (1, None, False, False),
                'column 3': (2, None, False, True),
                'column 5': (4, ',', False, False)
            },
            'id': (1, None, False, False),
            'tokenizer': (0, None, True, False),
            'value': (2, None, False, True)
        }
        assert specs == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(specs))

    def test_insert_node(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.utility.compile_dict_specs(fields)
        model = self.model
        model.create_recognizer_schema(model.cursor)
        test_trie = {}
        self.utility.insert_node(label='the synonym', label_id=1, entity_id=10, subtrie=test_trie, specs=specs, columns=['', '', '', ''], model=model)
        self.utility.insert_node('the synthesis', 2, 20, test_trie, specs, ['', '', '', ''], model)
        expected = {'t': {'h': {'e': {' ': {'s': {'y': {'n': {'o': {'n': {'y': {'m': {'~i': [1]}}}}, 't': {'h': {'e': {'s': {'i': {'s': {'~i': [2]}}}}}}}}}}}}}}
        assert test_trie == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(test_trie))

    def test_remove_node(self):
        test_trie = {'t': {'h': {'e': {' ': {'s': {'y': {'n': {'o': {'n': {'y': {'m': {'~i': [1]}}}}, 't': {'h': {'e': {'s': {'i': {'s': {'~i': [1]}}}}}}}}}}}}}}
        model = self.model
        self.utility.remove_node(model=model, label='the synonym', subtrie=test_trie)
        expected = {'t': {'h': {'e': {' ': {'s': {'y': {'n': {'t': {'h': {'e': {'s': {'i': {'s': {'~i': [1]}}}}}}}}}}}}}}
        assert test_trie == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(test_trie))

    def test_make_recognizer(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.utility.compile_dict_specs(fields)
        model = self.model
        got_recognizer, got_line_numbers = self.utility.make_recognizer(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, word_separator=' ', item_limit=0, compressed=True, column_separator='\t', column_enclosure='', tokenizer_option=0)
        expected_recognizer = [
            {
                model.SPECS_KEY: {
                    'fields': {
                        'normalizer': (0, None, True, False),
                        'entity_id': (1, None, False, False),
                        'label': (2, None, False, True),
                        'some_attribute': (3, ',', False, False)
                    },
                    'id': (1, None, False, False),
                    'tokenizer': (0, None, True, False),
                    'value': (2, None, False, True)
                },
                model.COMPRESSED_KEY: 1,
                model.TOKENIZER_OPTION_KEY: 0,
                model.WORD_SEPARATOR_KEY: ' ',
                model.CONTENT_KEY: {
                    'bypass': {'a': {'w': {'e': {'some white refrigerator': {'s': {model.ENTITY_KEY: [0, 3]}, 'x': {model.ENTITY_KEY: [1]}, model.ENTITY_KEY: [4]}}, 'w': {'some white refrigerator': {model.ENTITY_KEY: [5]}}}}, 'c': {'onflicting refrigerator': {model.ENTITY_KEY: [2, 8]}}, 'i': {'t': {model.ENTITY_KEY: [6]}}, 'o': {model.ENTITY_KEY: [7]}}
                }
            }
        ]
        expected_line_numbers = {
            0: 0,
            1: 0,
            2: 0,
            3: 1,
            4: 1,
            5: 1,
            6: 0,
            7: 1,
            8: 1
        }
        assert got_recognizer == expected_recognizer, '\nExpected\n%s\nGot\n%s' % (str(expected_recognizer), str(got_recognizer))
        assert got_line_numbers == expected_line_numbers, '\nExpected\n%s\nGot\n%s' % (str(expected_line_numbers), str(got_line_numbers))

    def test_make_keywords(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.utility.compile_dict_specs(fields)
        model = self.model
        _, got_line_numbers = self.utility.make_recognizer(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, word_separator=' ', item_limit=0, compressed=True, column_separator='\t', column_enclosure='', tokenizer_option=0)
        keywords = self.utility.make_keywords(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, line_numbers=got_line_numbers, word_separator=' ', disambiguate_all=False, column_separator='\t', column_enclosure='', tokenizer_option=0)
        expected = {
            model.CONTENT_KEY: {
                0: {'it', 'refrigeratorx', 'white', 'awesome', 'refrigerator', 'conflicting', 'refrigerators'},
                1: {'conflicting', 'white', 'awesome', 'refrigerator', 'o', 'refrigerators', 'awwsome'}
            },
            model.INTERNAL_ID_KEY: {
                0: 0,
                1: 0,
                2: 0,
                3: 1,
                4: 1,
                5: 1,
                6: 0,
                7: 1,
                8: 1
            }
        }
        assert keywords == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(keywords))

    def test_compile_model(self):
        compiled, model = self.compile_test_model()
        assert compiled == True, 'pilsner.Utility.compile_model() returned False which is not expected'
        assert model.NORMALIZER_KEY in model, 'Model does not have model.NORMALIZER_KEY which is not expected'
        assert model.DEFAULT_NORMALIZER_KEY in model, 'Model does not have model.DEFAULT_NORMALIZER_KEY which is not expected'
        assert model.DICTIONARY_KEY in model, 'Model does not have model.DICTIONARY_KEY which is not expected'
        assert model.KEYWORDS_KEY in model, 'Model does not have model.KEYWORDS_KEY which is not expected'
        assert model.DATASOURCE_KEY in model, 'Model does not have model.DATASOURCE_KEY which is not expected'
        assert model.WORD_SEPARATOR_KEY in model, 'Model does not have model.WORD_SEPARATOR_KEY which is not expected'
        assert model.TOKENIZER_OPTION_KEY in model, 'Model does not have model.TOKENIZER_OPTION_KEY which is not expected'
        assert 't1' in model[model.NORMALIZER_KEY], 'Normalizers do not include "t1"'
        assert 't2' in model[model.NORMALIZER_KEY], 'Normalizers do not include "t2"'
        expected_dictionary = [
            {
                model.SPECS_KEY: {
                    'fields': {
                        'normalizer': (0, None, True, False),
                        'entity_id': (1, None, False, False),
                        'label': (2, None, False, True),
                        'some_attribute': (3, ',', False, False)
                    },
                    'id': (1, None, False, False),
                    'tokenizer': (0, None, True, False),
                    'value': (2, None, False, True)
                },
                model.COMPRESSED_KEY: 1,
                model.TOKENIZER_OPTION_KEY: 0,
                model.WORD_SEPARATOR_KEY: ' ',
                model.CONTENT_KEY: {'t1': {'a': {'wesome white refrigera': {' ': {'tors': {'~i': [0]}}, 't': {'or': {'x': {'~i': [1]}, '~i': [4]}}}}}, 't2': {'c': {'onflicting refrigerator': {'~i': [2, 8]}}, 'a': {'w': {'e': {'some refrigerators': {'~i': [3]}}, 'w': {'some refrigerator': {'~i': [5]}}}}, 'i': {'t': {'~i': [6]}}, 'o': {'~i': [7]}}}
            }
        ]
        expected_keywords = {model.CONTENT_KEY: {0: {'refrigerator', 'tors', 'it', 'refrigera', 'white', 'conflicting', 'awesome', 'refrigeratorx'}, 1: {'refrigerator', 'refrigerators', 'white', 'o', 'conflicting', 'awwsome', 'awesome'}}, model.INTERNAL_ID_KEY: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 0, 7: 1, 8: 1}}
        assert model[model.DICTIONARY_KEY] == expected_dictionary, '\nExpected\n%s\nGot\n%s' % (str(expected_dictionary), str(model[model.DICTIONARY_KEY]))
        assert model[model.KEYWORDS_KEY] == expected_keywords, '\nExpected\n%s\nGot\n%s' % (str(expected_keywords), str(model[model.KEYWORDS_KEY]))

    def test_unpack_trie(self):
        _, model = self.compile_test_model()
        packed_trie = {'wesome white refrigera': {' ': {'tors': {model.ENTITY_KEY: [0]}}, 't': {'or': {'x': {model.ENTITY_KEY: [1]}, model.ENTITY_KEY: [4]}}}}
        expected = {'w': {'e': {'s': {'o': {'m': {'e': {' ': {'w': {'h': {'i': {'t': {'e': {' ': {'r': {'e': {'f': {'r': {'i': {'g': {'e': {'r': {'a': {' ': {'tors': {'~i': [0]}}, 't': {'or': {'x': {'~i': [1]}, '~i': [4]}}}}}}}}}}}}}}}}}}}}}}}}}
        unpacked_trie = self.utility.unpack_trie(model=model, packed_trie=packed_trie, compressed=True)
        assert unpacked_trie == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(unpacked_trie))

    def test_unpack_attributes(self):
        _, model = self.compile_test_model()
        cur = model.cursor
        leaf_ids = [8]
        include_query  = ''
        exclude_query = ''
        process_exclude = False
        attrs_out_query = ''
        expected = {8: {'entity_id': ['entity1'], 'normalizer': ['tokenizer2'], 'some_attribute': ['A', 'B', 'C']}}
        attributes = self.utility.unpack_attributes(cur, leaf_ids, include_query, exclude_query, process_exclude, attrs_out_query)
        assert attributes == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(attributes))

    def test_check_attrs(self):
        _, model = self.compile_test_model()
        trie_leaf = {model.ENTITY_KEY: [8]}
        cur = model.cursor
        include_query  = ''
        exclude_query = ''
        process_exclude = False
        attrs_out_query = ''
        expected = {model.ENTITY_KEY: [8], model.ATTRS_KEY: {8: {'entity_id': ['entity1'], 'normalizer': ['tokenizer2'], 'some_attribute': ['A', 'B', 'C']}}}
        got_leaf = self.utility.check_attrs(model, trie_leaf, cur, include_query, exclude_query, process_exclude, attrs_out_query)
        assert got_leaf == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(got_leaf))

    def test_spot_entities(self):
        _, model = self.compile_test_model()
        source_string = 'this is awesome white refrigerator , and this is not'
        normalizer_name = 't1'
        expected = [([4], {4: {'entity_id': ['entity1'], 'normalizer': ['tokenizer1'], 'some_attribute': ['A', 'B', 'C']}}, 'awesome white refrigerator', 8, 34)]
        spotted = self.utility.spot_entities(model, source_string, normalizer_name)
        assert spotted == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(spotted))

    def test_disambiguate(self):
        _, model = self.compile_test_model()
        # source string: this is awwsome and conflicting refrigerator, hey
        # spotted span
        spotted = [
            (
                [8, 2], # internal IDs
                {
                    8: {'DType': ['tokenizer1'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}, # attrs for each internal ID
                    2: {'DType': ['tokenizer2'], 'MSID': ['entity2'], 'smth': ['D', 'E']} # attrs for each internal ID
                },
                20, 44, # location (mapped)
                [0, 1], # indexes of items in srcs (normalized source strings)
                [
                    (20, 44), # location[0] (unmapped)
                    (20, 44)  # location[1] (unmapped)
                ]
            )
        ]
        # normalized source strings
        srcs =  [
            'this is awwsome and conflicting refrigerator , hey',
            'this is awwsome and conflicting refrigerator , hey'
        ]
        word_separator = ' '
        # given a sample model, we expect internal ID == 2 to be removed
        expected = [
            (
                [8],
                {
                    8: {'DType': ['tokenizer1'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}
                },
                20, 44,
                [0, 1],
                [
                    (20, 44),
                    (20, 44)
                ]
            )
        ]
        disambiguated = self.utility.disambiguate(model, spotted, srcs, word_separator)
        assert disambiguated == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(disambiguated))

    def test_flatten_layers(self):
        _, model = self.compile_test_model()
        # two normalization layers; first has one span; second has two spans
        layers = [
            (
                (
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
                    [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], [47, 47], [48, 48], [49, 49], [50, 50], [51, 51], [52, 52], [53, 53], [54, 54], [55, 55], [56, 56], [57, 57], [58, 58], [59, 59], [60, 60], [61, 61], [62, 62], [63, 63], [64, 64], [65, 65], [66, 66], [67, 67], [68, 68], [69, 69], [70, 70], [71, 71], [72, 72]]
                ),
                [
                    (
                        [4],
                        {4: {'DType': ['tokenizer1'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                        'awesome white refrigerator',
                        47, 72
                    )
                ],
                'this is awwsome white refrigerator , and it is awesome white refrigerator'
            ),
            (
                (
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
                    [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [14, 14], [14, 14], [14, 14], [14, 14], [14, 14], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], [47, 47], [47, 47], [47, 47], [47, 47], [47, 47], [47, 47], [47, 47], [48, 48], [49, 49], [50, 50], [51, 51], [52, 52], [53, 53], [54, 54], [55, 55], [56, 56], [57, 57], [58, 58], [59, 59], [60, 60]]
                ),
                [
                    (
                        [5],
                        {5: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                        'awwsome refrigerator',
                        8, 28
                    ),
                    (
                        [6],
                        {6: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                        'it',
                        35, 37
                    )
                ],
                'this is awwsome refrigerator , and it is awesome refrigerator'
            )
        ]
        # we expect all three spans to get stacked in one list (without strings themselves, and with mapped locations)
        expected = [
            (
                [5],
                {5: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                8, 34
            ),
            (
                [6],
                {6: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                40, 42
            ),
            (
                [4],
                {4: {'DType': ['tokenizer1'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                46, 71
            )
        ]
        flattened = self.utility.flatten_layers(model, layers)
        assert flattened == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(flattened))

    def test_flatten_spans(self):
        spans = [
            (
                [5],
                {5: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                8, 34
            ),
            (
                [6],
                {6: {'DType': ['tokenizer2'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                40, 42
            ),
            (
                [4],
                {4: {'DType': ['tokenizer1'], 'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}},
                46, 71
            )
        ]
        expected = {
            (8, 34): {'DType': {'tokenizer2'}, 'MSID': {'entity1'}, 'smth': {'C', 'B', 'A'}},
            (40, 42): {'DType': {'tokenizer2'}, 'MSID': {'entity1'}, 'smth': {'C', 'B', 'A'}},
            (46, 71): {'DType': {'tokenizer1'}, 'MSID': {'entity1'}, 'smth': {'C', 'B', 'A'}}
        }
        flattened = self.utility.flatten_spans(spans)
        assert flattened == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(flattened))

    def test_reduce_spans(self):
        segments = set([tuple([1, 2]), tuple([3, 8]), tuple([1, 6]), tuple([2, 3])])
        expected = [tuple([1, 6])]
        reduced = self.utility.reduce_spans(segments)
        assert reduced == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(reduced))

    def test_parse(self):
        _, model = self.compile_test_model()
        source_string = 'this is awwsome white refrigerator o refrigerator, is it tors not conflicting refrigerator hey'
        expected = {
            (8, 34): {'entity_id': {'entity1'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (35, 36): {'entity_id': {'entity1'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (54, 56): {'entity_id': {'entity2'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (66, 90): {'entity_id': {'entity2'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'D', 'E'}}
        }
        output = self.utility.parse(model, source_string)
        assert output == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(output))

if __name__ == '__main__':
    sys.path.insert(0, '')
    import pilsner # pylint: disable=E0611,F0401
    unittest.main(exit=False)
    try:
        import bin as pilsner # pylint: disable=E0611,F0401
        unittest.main()
        # x = TestUtility()
        # x.setUp()
        # x.compile_test_model()
        # x.tearDown()
    except ModuleNotFoundError:
        print('Could not import module from /bin, test skipped.')
