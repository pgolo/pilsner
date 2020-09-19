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
        {'name': 'smth', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
    ]
    specs = r.compile_dict_specs(fields)
    _messages.clear()
    r.compile_model(m, 'test/assets/sample_dictionary.txt', specs, ' ', '\t', '\n', item_limit=3, include_keywords=True)
    print(m['~keywords'])
    #s = 'this is awwsome white refrigerator o refrigerator, is it tors not conflicting refrigerator hey'
    s = 'this is awwsome white refrigerator , and it is awesome white refrigerator'
    _messages.clear()
    #q = r.parse(m, s)
    #print(q)
    m.save('.test_model')

def load_it():
    rrr = pilsner.Recognizer(callback_status=callback_update_status, callback_progress=callback_update_mesage)
    m = pilsner.Model('.test_model')
    s = 'this is awesome white refrigerators o refrigerator, is it not'
    s *= 10
    _messages.clear()
    q = rrr.parse(m, s, attrs_where={'+': {'smth': {'D', 'A'}}}, attrs_out=['MSID', 'smth'])
    #print(q)

save_it()
load_it()

#segments = [tuple([1, 2]), tuple([3, 8]), tuple([1, 6]), tuple([2, 3])]
#r = Recognizer()
#red = r.reduce(segments)
#print(red)

print(_messages)
print(_status)

#layers = [([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 30, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48, 49, 50], [([0], {0: {'MSID': ['entity2'], 'smth': ['C', 'D', 'E']}}, 'acinic cell carcino mas', 8, 31)]), ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48, 49, 50], [([2], {2: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'acinic carcinomas', 8, 25), ([5], {5: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'it', 45, 46), ([6], {6: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'o', 26, 27)])]
#layers = [([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 30, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48, 49, 50], [([0], {0: {'MSID': ['entity2'], 'smth': ['C', 'D', 'E']}}, 'acinic cell carcino mas', 8, 31)]), ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48, 49, 50], [([2], {2: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'acinic carcinomas', 8, 26), ([5], {5: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'it', 45, 46), ([6], {6: {'MSID': ['entity1'], 'smth': ['A', 'B', 'C']}}, 'o', 26, 27)])]

#rrr = pilsner.Recognizer(callback_status=callback_update_status, callback_progress=callback_update_mesage)
#x = rrr.flatten(layers)
#print(x)


