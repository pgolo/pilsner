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
        pass

    def test_load(self):
        pass

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
