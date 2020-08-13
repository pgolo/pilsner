import os
import sys; sys.path.insert(0, '')
import unittest
import pilsner # pylint: disable=E0611,F0401

class TestModel(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        m = pilsner.Model()
        assert 'm' in locals(), 'Instance of Model class has not been created'
        assert type(m) == pilsner.Model, 'Model is expected to have pilsner.Model type, but has %s instead' % (str(type(m)))
        storage = m.DEFAULT_DATASOURCE
        assert storage.lower() == ':memory:' or os.path.exists(storage), 'Model storage is not where it is supposed to be'

    def test_del(self):
        m = pilsner.Model()
        storage = m.DEFAULT_DATASOURCE
        del(m)
        assert 'm' not in locals(), 'Instance of Model class has not been destroyed'
        assert storage.lower() == ':memory:' or not os.path.exists(storage), 'Model storage is supposed to be removed once class has been destroyed'

    def test_save(self):
        m = pilsner.Model()
        m[m.DICTIONARY_KEY].append({})
        m.save('./.test_save')
        del(m)
        assert os.path.exists('./.test_save.0.dictionary'), 'Dictionary file was not saved'
        assert os.path.exists('./.test_save.attributes'), 'Attributes file was not saved'
        assert os.path.exists('./.test_save.keywords'), 'Keywords file was not saved'
        assert os.path.exists('./.test_save.normalizers'), 'Normalizers file was not saved'
        os.remove('./.test_save.0.dictionary')
        os.remove('./.test_save.attributes')
        os.remove('./.test_save.keywords')
        os.remove('./.test_save.normalizers')

    def test_load(self):
        m1 = pilsner.Model()
        m1[m1.DICTIONARY_KEY].append({'a': {'b': {'c': 'def'}}})
        m1[m1.DICTIONARY_KEY].append({'g': {'h': {'i': 'jkl'}}})
        m1.save('./.test_load')
        expected = m1[m1.DICTIONARY_KEY]
        del(m1)
        m2 = pilsner.Model()
        m2.load('./.test_load')
        assert m2[m2.DICTIONARY_KEY] == expected, 'Loaded model %s != saved model %s' % (str(m2[m2.DICTIONARY_KEY]), str(expected))
        del(m2)
        os.remove('./.test_load.0.dictionary')
        os.remove('./.test_load.1.dictionary')
        os.remove('./.test_load.attributes')
        os.remove('./.test_load.keywords')
        os.remove('./.test_load.normalizers')

    def test_add_normalizer(self):
        pass

    def test_create_recognizer_schema(self):
        pass

    def test_pack_subtrie(self):
        pass

    def test_pack_trie(self):
        pass

    def test_attribute_wrapper(self):
        pass

    def test_get_dictionary_line(self):
        pass

    def test_get_dictionary_synonym(self):
        pass

    def test_next_trie(self):
        pass

if __name__ == '__main__':
    unittest.main()
