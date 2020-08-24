import sys; sys.path.insert(0, '')
import unittest
import pilsner # pylint: disable=E0611,F0401

class TestUtility(unittest.TestCase):

    def setUp(self):
        self.recognizer = pilsner.Recognizer()

    def tearDown(self):
        del(self.recognizer)

    def compile_test_model(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.recognizer.compile_dict_specs(fields)
        model = pilsner.Model()
        model.add_normalizer('t1', 'test/assets/tokenizer1.xml')
        model.add_normalizer('t2', 'test/assets/tokenizer2.xml')
        model.normalizer_map = {
            'tokenizer1': 't1',
            'tokenizer2': 't2'
        }
        compiled = self.recognizer.compile_model(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, word_separator=' ', column_separator='\t', column_enclosure='', include_keywords=True)
        return compiled, model

    def test_init(self):
        r = pilsner.Recognizer()
        assert 'r' in locals(), 'Instance of Recognizer class has not been created'
        assert type(r) == pilsner.Recognizer, 'Utility is supposed to have pilsner.Recognizer type, but has %s instead' % (str(type(r)))

    def test_del(self):
        r = pilsner.Recognizer()
        del(r)
        assert 'r' not in locals(), 'Instance of Recognizer class has not been destroyed'

    def test_push_message(self):
        messages = []
        def callback_function(message):
            messages.append(message)
        self.recognizer.push_message('message 1', callback_function)
        self.recognizer.push_message('message 2', callback_function)
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
        specs = self.recognizer.compile_dict_specs(fields)
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

    def test_make_recognizer(self):
        fields = [
            {'name': 'normalizer', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
            {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
            {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
            {'name': 'some_attribute', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
        ]
        specs = self.recognizer.compile_dict_specs(fields)
        model = pilsner.Model()
        got_recognizer, got_line_numbers = self.recognizer.make_recognizer(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, word_separator=' ', item_limit=0, compressed=True, column_separator='\t', column_enclosure='', tokenizer_option=0)
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
            6: 1,
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
        specs = self.recognizer.compile_dict_specs(fields)
        model = pilsner.Model()
        _, got_line_numbers = self.recognizer.make_recognizer(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, word_separator=' ', item_limit=0, compressed=True, column_separator='\t', column_enclosure='', tokenizer_option=0)
        keywords = self.recognizer.make_keywords(model=model, filename='test/assets/sample_dictionary.txt', specs=specs, line_numbers=got_line_numbers, word_separator=' ', disambiguate_all=False, column_separator='\t', column_enclosure='', tokenizer_option=0)
        expected = {
            model.CONTENT_KEY: {
                0: {'refrigerator', 'white', 'awesome', 'conflicting', 'refrigerators', 'refrigeratorx'},
                1: {'o', 'white', 'conflicting', 'refrigerators', 'awwsome', 'it', 'refrigerator', 'awesome', 'refrigerator'}
            },
            model.INTERNAL_ID_KEY: {
                0: 0,
                1: 0,
                2: 0,
                3: 1,
                4: 1,
                5: 1,
                6: 1,
                7: 1,
                8: 1
            }
        }
        assert keywords == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(keywords))

    def test_compile_model(self):
        compiled, model = self.compile_test_model()
        assert compiled == True, 'pilsner.Recognizer.compile_model() returned False which is not expected'
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
                model.CONTENT_KEY: {'t1': {'a': {'wesome white refrigera': {' ': {'tors': {model.ENTITY_KEY: [0]}}, 't': {'or': {'x': {model.ENTITY_KEY: [1]}, model.ENTITY_KEY: [4]}}}}, 'c': {'onflicting refrigerator': {model.ENTITY_KEY: [8]}}}, 't2': {'c': {'onflicting refrigerator': {model.ENTITY_KEY: [2]}}, 'a': {'w': {'e': {'some refrigerators': {model.ENTITY_KEY: [3]}}, 'w': {'some refrigerator': {model.ENTITY_KEY: [5]}}}}, 'i': {'t': {model.ENTITY_KEY: [6]}}, 'o': {model.ENTITY_KEY: [7]}}}
            }
        ]
        expected_keywords = {model.CONTENT_KEY: {0: {'refrigera', 'refrigeratorx', 'tors', 'refrigerator', 'white', 'awesome', 'conflicting'}, 1: {'it', 'o', 'awwsome', 'white', 'refrigerator', 'refrigerator', 'conflicting', 'refrigerators', 'awesome'}}, model.INTERNAL_ID_KEY: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1}}
        assert model[model.DICTIONARY_KEY] == expected_dictionary, '\nExpected\n%s\nGot\n%s' % (str(expected_dictionary), str(model[model.DICTIONARY_KEY]))
        assert model[model.KEYWORDS_KEY] == expected_keywords, '\nExpected\n%s\nGot\n%s' % (str(expected_keywords), str(model[model.KEYWORDS_KEY]))

    def test_unpack_trie(self):
        _, model = self.compile_test_model()
        packed_trie = {'wesome white refrigera': {' ': {'tors': {model.ENTITY_KEY: [0]}}, 't': {'or': {'x': {model.ENTITY_KEY: [1]}, model.ENTITY_KEY: [4]}}}}
        expected = {'w': {'e': {'s': {'o': {'m': {'e': {' ': {'w': {'h': {'i': {'t': {'e': {' ': {'r': {'e': {'f': {'r': {'i': {'g': {'e': {'r': {'a': {' ': {'tors': {'~i': [0]}}, 't': {'or': {'x': {'~i': [1]}, '~i': [4]}}}}}}}}}}}}}}}}}}}}}}}}}
        unpacked_trie = self.recognizer.unpack_trie(model=model, packed_trie=packed_trie, compressed=True)
        assert unpacked_trie == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(unpacked_trie))

    def test_unpack_attributes(self):
        _, model = self.compile_test_model()
        cur = model.cursor
        leaf_ids = [8]
        include_query  = ''
        exclude_query = ''
        process_exclude = False
        attrs_out_query = ''
        expected = {8: {'entity_id': ['entity1'], 'normalizer': ['tokenizer1'], 'some_attribute': ['A', 'B', 'C']}}
        attributes = self.recognizer.unpack_attributes(cur, leaf_ids, include_query, exclude_query, process_exclude, attrs_out_query)
        assert attributes == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(attributes))

    def test_check_attrs(self):
        _, model = self.compile_test_model()
        trie_leaf = {model.ENTITY_KEY: [8]}
        cur = model.cursor
        include_query  = ''
        exclude_query = ''
        process_exclude = False
        attrs_out_query = ''
        expected = {model.ENTITY_KEY: [8], model.ATTRS_KEY: {8: {'entity_id': ['entity1'], 'normalizer': ['tokenizer1'], 'some_attribute': ['A', 'B', 'C']}}}
        got_leaf = self.recognizer.check_attrs(model, trie_leaf, cur, include_query, exclude_query, process_exclude, attrs_out_query)
        assert got_leaf == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(got_leaf))

    def test_spot_entities(self):
        _, model = self.compile_test_model()
        source_string = 'this is awesome white refrigerator , and this is not'
        normalizer_name = 't1'
        expected = [([4], {4: {'entity_id': ['entity1'], 'normalizer': ['tokenizer1'], 'some_attribute': ['A', 'B', 'C']}}, 'awesome white refrigerator', 8, 34)]
        spotted = self.recognizer.spot_entities(model, source_string, normalizer_name)
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
        disambiguated = self.recognizer.disambiguate(model, spotted, srcs, word_separator)
        assert disambiguated == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(disambiguated))

    def test_flatten_layers(self):
        _, model = self.compile_test_model()
        # two normalization layers; first has one span; second has two spans
        layers = [
            (
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
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
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
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
        flattened = self.recognizer.flatten_layers(model, layers)
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
        flattened = self.recognizer.flatten_spans(spans)
        assert flattened == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(flattened))

    def test_reduce_spans(self):
        segments = [tuple([1, 2]), tuple([3, 8]), tuple([1, 6]), tuple([2, 3])]
        expected = [tuple([1, 6])]
        reduced = self.recognizer.reduce_spans(segments)
        assert reduced == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(reduced))

    def test_parse(self):
        _, model = self.compile_test_model()
        source_string = 'this is awwsome white refrigerator o refrigerator, is it tors not conflicting refrigerator hey'
        expected = {
            (8, 34): {'entity_id': {'entity1'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (35, 36): {'entity_id': {'entity1'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (54, 56): {'entity_id': {'entity1'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'C', 'B', 'A'}},
            (66, 90): {'entity_id': {'entity2'}, 'normalizer': {'tokenizer2'}, 'some_attribute': {'D', 'E'}}
        }
        output = self.recognizer.parse(model, source_string)
        assert output == expected, '\nExpected\n%s\nGot\n%s' % (str(expected), str(output))

if __name__ == '__main__':
    unittest.main()
