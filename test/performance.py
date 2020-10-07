import os
import sys; sys.path.insert(0, '')
import random
import string
import timeit

ENTITIES_IN_DICTIONARY = 50000
WORDS_IN_TEXT = 100000

MIN_LABELS_PER_ENTITY = 1
MAX_LABELS_PER_ENTITY = 5
MIN_WORDS_PER_LABEL = 1
MAX_WORDS_PER_LABEL = 4
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 10

def random_label(
    min_words,
    max_words,
    min_word_length,
    max_word_length
):
    number_of_words = random.randint(min_words, max_words)
    words = []
    greek = ['qalphaz', 'qbetaz', 'qgammaz']
    for _ in range(number_of_words):
        words.append(''.join(random.choice(string.ascii_letters) for i in range(random.randint(min_word_length, max_word_length))))
    words[0] += greek[random.randint(0, 2)]
    label = ' '.join(words)
    return label

def random_label_list(
    min_labels,
    max_labels,
    min_words,
    max_words,
    min_word_length,
    max_word_length
):
    number_of_labels = random.randint(min_labels, max_labels)
    labels = [random_label(min_words, max_words, min_word_length, max_word_length) for _ in range(number_of_labels)]
    label_attrs = [','.join([random_label(1, 1, 3, 5) for _ in range(random.randint(1,3))]) for _ in range(number_of_labels)]
    return labels, label_attrs

def create_labels(
    dictionary_size,
    min_labels_per_entity,
    max_labels_per_entity,
    min_words_per_label,
    max_words_per_label,
    min_word_length,
    max_word_length
):
    labels = {}
    label_attrs = {}
    for i in range(dictionary_size):
        labels[i+1], label_attrs[i+1] = random_label_list(
            min_labels=min_labels_per_entity,
            max_labels=max_labels_per_entity,
            min_words=min_words_per_label,
            max_words=max_words_per_label,
            min_word_length=min_word_length,
            max_word_length=max_word_length
        )
    return labels, label_attrs

def create_entity_attrs(
    dictionary_size
):
    attrs = {}
    for i in range(dictionary_size):
        attrs[i+1] = random_label(1, 1, 3, 5)
    return attrs

def create_test_dictionary(
    dictionary_size,
    min_labels_per_entity,
    max_labels_per_entity,
    min_words_per_label,
    max_words_per_label,
    min_word_length,
    max_word_length
):
    labels, label_attrs = create_labels(
        dictionary_size=dictionary_size,
        min_labels_per_entity=min_labels_per_entity,
        max_labels_per_entity=max_labels_per_entity,
        min_words_per_label=min_words_per_label,
        max_words_per_label=max_words_per_label,
        min_word_length=min_word_length,
        max_word_length=max_word_length
    )
    entity_attrs = create_entity_attrs(dictionary_size)
    with open('.test-dict.txt', mode='w', encoding='utf8') as f:
        for entity_id in entity_attrs:
            for i in range(len(labels[entity_id])):
                f.write('%d\t%s\t%s\t%s\n' % (entity_id, labels[entity_id][i], label_attrs[entity_id][i], entity_attrs[entity_id]))
    selected_entities = [random.randint(1, dictionary_size) for _ in range(10)]
    with open('.test-labels.txt', mode='w', encoding='utf8') as f:
        for entity_id in selected_entities:
            f.write('%s\n' % (labels[entity_id][random.randint(1, len(labels[entity_id]))-1]))

def create_test_text(number_of_words):
    labels = []
    with open('.test-labels.txt', mode='r', encoding='utf8') as f:
        for line in f:
            labels.append(line.strip())
    t = []
    for _ in range(number_of_words):
        t.append(random_label(1, 1, 3, 10))
    for label in labels:
        t.insert(random.randint(1, len(t))-1, label)
    text = ' '.join(t)
    with open('.test-text.txt', mode='w', encoding='utf8') as f:
        f.write(text)

def create_test_dataset():
    create_test_dictionary(
        dictionary_size=ENTITIES_IN_DICTIONARY,
        min_labels_per_entity=MIN_LABELS_PER_ENTITY,
        max_labels_per_entity=MAX_LABELS_PER_ENTITY,
        min_words_per_label=MIN_WORDS_PER_LABEL,
        max_words_per_label=MAX_WORDS_PER_LABEL,
        min_word_length=MIN_WORD_LENGTH,
        max_word_length=MAX_WORD_LENGTH
    )
    create_test_text(
        number_of_words=WORDS_IN_TEXT
    )

def perf_compile_model_save_model(modules_to_test):
    n = 1
    for x in modules_to_test:
        print(
            '%s: compiled model with %d entities from .test-dict.txt in %f seconds' % (
                x,
                ENTITIES_IN_DICTIONARY,
                timeit.timeit(
                    setup = """
import %s as pilsner
model = pilsner.Model()
model.add_normalizer('standard', None)
utility = pilsner.Utility()
fields = [
    {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
    {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
    {'name': 'label_attr', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False},
    {'name': 'entity_attr', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
]
""" % (x),
                    stmt="""
utility.compile_model(model, '.test-dict.txt', fields, ' ', '\\t', '\\n', include_keywords=True)
model.destroy()
""",
                    number=n
                )
            )
        )
        print(
            '%s: saved model with %d entities in %f seconds' % (
                x,
                ENTITIES_IN_DICTIONARY,
                timeit.timeit(
                    setup = """
import %s as pilsner
model = pilsner.Model()
model.add_normalizer('standard', None)
utility = pilsner.Utility()
fields = [
    {'name': 'entity_id', 'include': True, 'delimiter': None, 'id_flag': True, 'normalizer_flag': False, 'value_flag': False},
    {'name': 'label', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': True},
    {'name': 'label_attr', 'include': True, 'delimiter': ',', 'id_flag': False, 'normalizer_flag': False, 'value_flag': False},
    {'name': 'entity_attr', 'include': True, 'delimiter': None, 'id_flag': False, 'normalizer_flag': False, 'value_flag': False}
]
utility.compile_model(model, '.test-dict.txt', fields, ' ', '\\t', '\\n', include_keywords=True)
""" % (x),
                    stmt="""
model.save('.test-model')
model.destroy()
""",
                    number=n
                )
            )
        )
def perf_load_model_parse_test(modules_to_test):
    n = 1
    for x in modules_to_test:
        print(
            '%s: loaded model with %d entities from .test-model in %f seconds' % (
                x,
                ENTITIES_IN_DICTIONARY,
                timeit.timeit(
                    setup = """
import %s as pilsner
model = pilsner.Model()
""" % (x),
                    stmt="""
model.load('.test-model')
model.destroy()
""",
                    number=n
                )
            )
        )
        print(
            '%s: parsed text with %d words in .test-text.txt using model with %d entities in %f seconds' % (
                x,
                WORDS_IN_TEXT,
                ENTITIES_IN_DICTIONARY,
                timeit.timeit(
                    setup = """
import %s as pilsner
model = pilsner.Model()
model.load('.test-model')
utility = pilsner.Utility()
with open('.test-text.txt', mode='r', encoding='utf8') as f:
    test_text = f.read()
""" % (x),
                    stmt="""
found = utility.parse(model, test_text)
model.destroy()
""",
                    number=n
                )
            )
        )

def cleanup():
    for filename in [
        '.test-dict.txt',
        '.test-labels.txt',
        '.test-text.txt',
        '.test-model.0.dictionary',
        '.test-model.attributes',
        '.test-model.keywords',
        '.test-model.normalizers'
    ]:
        os.remove(filename)

if __name__ == '__main__':
    create_test_dataset()
    perf_compile_model_save_model(['pilsner', 'bin'])
    perf_load_model_parse_test(['pilsner', 'bin'])
    cleanup()
