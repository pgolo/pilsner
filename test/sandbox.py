import sys; sys.path.insert(0, '')
import pilsner # pylint: disable=E0611,F0401

_messages = []
_status = []

def callback_update_mesage(message):
    _messages.append(message)

def callback_update_status(status):
    _status.append(status)

def save_it():
    m = pilsner.Model()
    m.add_normalizer('tokenizer1', 'test/assets/tokenizer1.xml')
    m.add_normalizer('tokenizer2', 'test/assets/tokenizer2.xml')
    m.normalizer_map = {
        'tokenizer1': 'tokenizer1',
        'tokenizer2': 'tokenizer2'
    }
    r = pilsner.Recognizer(callback_status=callback_update_status, callback_progress=callback_update_mesage)
    specs = {'DType': (0, None, True, False), 'MSID': (1, None, False, False), 'value': (2, None, False, True)}
    fields = [
        {'name': 'DType', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': True, 'value_flag': False},
        {'name': 'MSID', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
        {'name': 'Value', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
        {'name': 'smth', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False},
    ]
    specs = r.compile_dict_specs(fields)
    r.compile_model(m, 'test/assets/sample_dictionary.txt', specs, ' ', '\t', '\n', item_limit=2, include_keywords=True)
    s = 'this is afinic cell carcinoma o carcinoma, damn it'
    q = r.parse(m, s)
    print(q)
    m.save('.test_model')

def load_it():
    rrr = pilsner.Recognizer(callback_status=callback_update_status, callback_progress=callback_update_mesage)
    m = pilsner.Model('.test_model')
    s = 'this is acinic cell carcinomas o carcinoma, damn it'
    s *= 10
    q = rrr.parse(m, s, attrs_where={'+': {'smth': {'D', 'A'}}}, attrs_out=['MSID', 'smth'])
    print(q)

save_it()
load_it()

#segments = [tuple([1, 2]), tuple([3, 8]), tuple([1, 6]), tuple([2, 3])]
#r = Recognizer()
#red = r.reduce(segments)
#print(red)

print(_messages)
print(_status)
