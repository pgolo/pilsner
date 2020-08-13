import sys; sys.path.insert(0, '')
import unittest
import pilsner # pylint: disable=E0611,F0401

class TestModel(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        r = pilsner.Recognizer()
        assert 'r' in locals(), 'Instance of Recognizer class has not been created'
        assert type(r) == pilsner.Recognizer, 'Utility is supposed to have pilsner.Recognizer type, but has %s instead' % (str(type(r)))

    def test_del(self):
        r = pilsner.Recognizer()
        del(r)
        assert 'r' not in locals(), 'Instance of Recognizer class has not been destroyed'

    def test_push_message(self):
        pass

    def test_compile_dict_specs(self):
        pass

    def test_make_recognizer(self):
        pass

    def test_make_keywords(self):
        pass

    def test_compile_model(self):
        pass

    def test_verify_keywords(self):
        pass

    def test_unpack_trie(self):
        pass

    def test_check_attrs(self):
        pass

    def test_attribute_unpacker(self):
        pass

    def test_spot_entities(self):
        pass

    def test_flatten_spans(self):
        pass

    def test_reduce_spans(self):
        pass

    def test_parse(self):
        pass

if __name__ == '__main__':
    unittest.main()
