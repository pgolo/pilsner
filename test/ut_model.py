import os
import sys
import unittest

class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = pilsner.Model()

    def tearDown(self):
        self.model.destroy()
        del(self.model)

    def test_init(self):
        m = pilsner.Model()
        assert 'm' in locals(), 'Instance of Model class has not been created'
        assert type(m) == pilsner.Model, 'Model is expected to have pilsner.Model type, but has %s instead' % (str(type(m)))
        storage = m.DEFAULT_DATASOURCE
        assert storage.lower() == ':memory:' or os.path.exists(storage), 'Model storage is not where it is supposed to be'
        m.destroy()

    def test_del(self):
        m = pilsner.Model()
        storage = m.DEFAULT_DATASOURCE
        m.destroy()
        del(m)
        assert 'm' not in locals(), 'Instance of Model class has not been destroyed'
        assert storage.lower() == ':memory:' or not os.path.exists(storage), 'Model storage is supposed to be removed once class has been destroyed'

    def test_save(self):
        self.model[self.model.DICTIONARY_KEY].append({})
        self.model.save('./.test_save')
        assert os.path.exists('./.test_save.0.dictionary'), 'Dictionary file was not saved'
        assert os.path.exists('./.test_save.attributes'), 'Attributes file was not saved'
        assert os.path.exists('./.test_save.keywords'), 'Keywords file was not saved'
        assert os.path.exists('./.test_save.normalizers'), 'Normalizers file was not saved'
        os.remove('./.test_save.0.dictionary')
        os.remove('./.test_save.attributes')
        os.remove('./.test_save.keywords')
        os.remove('./.test_save.normalizers')

    def test_load(self):
        self.model[self.model.DICTIONARY_KEY].append({'a': {'b': {'c': 'def'}}})
        self.model[self.model.DICTIONARY_KEY].append({'g': {'h': {'i': 'jkl'}}})
        self.model.save('./.test_load')
        expected = self.model[self.model.DICTIONARY_KEY]
        another_model = pilsner.Model()
        another_model.load('./.test_load')
        assert another_model[another_model.DICTIONARY_KEY] == expected, 'Loaded model %s != saved model %s' % (str(another_model[another_model.DICTIONARY_KEY]), str(expected))
        another_model.destroy()
        del(another_model)
        os.remove('./.test_load.0.dictionary')
        os.remove('./.test_load.1.dictionary')
        os.remove('./.test_load.attributes')
        os.remove('./.test_load.keywords')
        os.remove('./.test_load.normalizers')

    def test_add_normalizer(self):
        self.model.add_normalizer('t1', 'test/assets/tokenizer1.xml')
        normalization_units_count = len(self.model[self.model.NORMALIZER_KEY])
        assert normalization_units_count == 1, 'Model is expected to have 1 normalization unit (it has %d instead)' % (normalization_units_count)

    def test_create_recognizer_schema(self):
        self.model.create_recognizer_schema(self.model.cursor)
        rows = self.model.cursor.execute('select name from sqlite_master where type = \'table\' and name = \'attrs\';')
        assert len(list(rows)) == 1, 'Created schema does not contain table \'attrs\''
        rows = self.model.cursor.execute('select * from attrs;')
        assert len(list(rows)) == 0, 'Table \'attrs\' in newly created schema is not empty'

    def test_pack_subtrie(self):
        # radiology, radiotelescope
        subtrie = {'r': {'a': {'d': {'i': {'o': {'l': {'o': {'g': {'y': {self.model.ENTITY_KEY: [1]}}}}, 't': {'e': {'l': {'e': {'s': {'c': {'o': {'p': {'e': {self.model.ENTITY_KEY: [2]}}}}}}}}}}}}}}}
        initial_path = ''
        packed = self.model.pack_subtrie(subtrie, False, initial_path)
        assert packed[0] == subtrie, '%s != %s' % (str(packed), str(subtrie))
        assert packed[1] == '', 'pack_subtrie() function is supposed to return \'%s\' as path (it returned \'%s\')' % (initial_path, packed[1])
        packed = self.model.pack_subtrie(subtrie, True, initial_path)
        expected = {'r': {'adio': {'l': {'ogy': {self.model.ENTITY_KEY: [1]}}, 't': {'elescope': {self.model.ENTITY_KEY: [2]}}}}}
        assert packed[0] == expected, '%s != %s' % (str(packed), str(expected))

    def test_pack_trie(self):
        # radiology, radiotelescope
        tries = {self.model.CONTENT_KEY: {'t1': {'r': {'a': {'d': {'i': {'o': {'l': {'o': {'g': {'y': {self.model.ENTITY_KEY: [1]}}}}, 't': {'e': {'l': {'e': {'s': {'c': {'o': {'p': {'e': {self.model.ENTITY_KEY: [2]}}}}}}}}}}}}}}}, 't2': {'r': {'a': {'d': {'i': {'o': {'l': {'o': {'g': {'y': {self.model.ENTITY_KEY: [1]}}}}, 't': {'e': {'l': {'e': {'s': {'c': {'o': {'p': {'e': {self.model.ENTITY_KEY: [2]}}}}}}}}}}}}}}}}}
        packed = self.model.pack_trie(tries, False)
        assert packed == tries, '%s != %s' % (str(packed), str(tries))
        packed = self.model.pack_trie(tries, True)
        expected = {self.model.CONTENT_KEY: {'t1': {'r': {'adio': {'l': {'ogy': {self.model.ENTITY_KEY: [1]}}, 't': {'elescope': {self.model.ENTITY_KEY: [2]}}}}}, 't2': {'r': {'adio': {'l': {'ogy': {self.model.ENTITY_KEY: [1]}}, 't': {'elescope': {self.model.ENTITY_KEY: [2]}}}}}}}
        assert packed == expected, '%s != %s' % (str(packed), str(expected))

    def test_store_attributes(self):
        line_number = 123
        internal_id = 456
        subtrie = {}
        specs = {'fields': {'attr1': (0, None, False, False), 'attr2': (1, None, False, True), 'attr3': (2, None, True, False), 'attr4': (3, ',', False, False)}}
        columns = ['attr1_value', 'attr2_value', 'attr3_value', 'attr4_value_1,attr4_value_2,attr4_value_3']
        self.model.create_recognizer_schema(self.model.cursor)
        self.model.store_attributes(line_number, internal_id, subtrie, specs, columns)
        rows = self.model.cursor.execute('select * from attrs;')
        stored = set()
        for row in rows:
            stored.add(tuple(row))
        expected = {
            (123, 456, 'attr1', 'attr1_value'),
            (123, 456, 'attr3', 'attr3_value'),
            (123, 456, 'attr4', 'attr4_value_1'),
            (123, 456, 'attr4', 'attr4_value_2'),
            (123, 456, 'attr4', 'attr4_value_3')
        }
        assert len(stored) == len(expected), 'Expected to store %d rows (got %d instead)' % (len(expected), len(stored))
        for entry in expected:
            assert entry in stored, 'Entry %s was not stored' % str(entry)

    def test_get_dictionary_line(self):
        specs = {
            'fields': {
                'normalizer': (0, None, True, False),
                'entity_id': (1, None, False, False),
                'entity_value': (2, None, False, True),
                'something_else': (3, ',', False, False)
            },
            'id': (1, None, False, False),
            'tokenizer': (0, None, True, False),
            'value': (2, None, False, True)
        }
        entity_ids = {}
        line_numbers = {}
        line_number = 1
        line = 't1\tentity_id\tstring_value\tsome_attr,another_attr\n'
        column_separator = '\t'
        column_enclosure = ''
        got_line = self.model.get_dictionary_line(specs, entity_ids, line_numbers, line_number, line, column_separator, column_enclosure)
        expected = (['t1', 'entity_id', 'string_value', 'some_attr,another_attr'], 0)
        assert got_line == expected, 'Expected %s, got %s' % (str(expected), str(got_line))

    def test_get_dictionary_synonym(self):
        columns = ['t1', 'entity_id', 'string_value', 'some_attr,another_attr']
        specs = {
            'fields': {
                'normalizer': (0, None, True, False),
                'entity_id': (1, None, False, False),
                'entity_value': (2, None, False, True),
                'something_else': (3, ',', False, False)
            },
            'id': (1, None, False, False),
            'tokenizer': (0, None, True, False),
            'value': (2, None, False, True)
        }
        word_separator = ' '
        tokenizer_option = 0
        self.model.add_normalizer('t1', 'test/assets/tokenizer1.xml')
        self.model.add_normalizer('t2', 'test/assets/tokenizer2.xml')
        got_synonym = self.model.get_dictionary_synonym(columns, specs, word_separator, tokenizer_option)
        expected = ('string _ value', 't1')
        assert got_synonym == expected, 'Expected %s, got %s' % (str(expected), str(got_synonym))

    def test_next_trie(self):
        specs = {'specs': ('are', 'here')}
        compressed = True
        tokenizer_option = 0
        word_separator = ' '
        self.model.add_normalizer('t1', 'test/assets/tokenizer1.xml')
        self.model.add_normalizer('t2', 'test/assets/tokenizer2.xml')
        got_trie = self.model.next_trie(specs, compressed, tokenizer_option, word_separator)
        expected = {
            self.model.CONTENT_KEY: {'t1': {}, 't2': {}},
            self.model.SPECS_KEY: specs,
            self.model.COMPRESSED_KEY: int(compressed),
            self.model.TOKENIZER_OPTION_KEY: tokenizer_option,
            self.model.WORD_SEPARATOR_KEY: word_separator
        }
        assert got_trie == expected, 'Expected %s, got %s' % (str(expected), str(got_trie))

if __name__ == '__main__':
    sys.path.insert(0, '')
    import pilsner # pylint: disable=E0611,F0401
    unittest.main(exit=False)
    try:
        import bin as pilsner # pylint: disable=E0611,F0401
        unittest.main()
    except ModuleNotFoundError:
        print('Could not import module from /bin, test skipped.')
