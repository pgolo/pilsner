import os
import logging
import random
import string
import sqlite3
import sic
import pickle
import shutil

class Model(dict):

    def __init__(self, filename='', storage_location='', debug_mode=False, verbose_mode=False):

        self.CONTENT_KEY = '~content'
        self.SPECS_KEY = '~specs'
        self.COMPRESSED_KEY = '~compressed'
        self.TOKENIZER_OPTION_KEY = '~tokenizer_option'
        self.WORD_SEPARATOR_KEY = '~word_separator'
        self.ENTITY_KEY = '~i'
        self.ATTRS_KEY = '~p'
        self.INTERNAL_ID_KEY = '~iid'
        self.DICTIONARY_KEY = '~dictionary'
        self.KEYWORDS_KEY = '~keywords'
        self.NORMALIZER_KEY = '~normalization'
        self.DEFAULT_NORMALIZER_KEY = '~default_normalizer'
        self.DATASOURCE_KEY = '~datasource'

        self.DEFAULT_DATASOURCE_PATH = '.'
        self.DEFAULT_DATASOURCE_FILENAME = ''
        self.DEFAULT_DATASOURCE = ''

        self.DEFAULT_WORD_SEPARATOR = ' '
        self.DEFAULT_TOKENIZER_OPTION = 0

        self.DEFAULT_DATASOURCE_FILENAME = storage_location
        if self.DEFAULT_DATASOURCE_FILENAME.lower() != ':memory:':
            while self.DEFAULT_DATASOURCE_FILENAME == '' or os.path.exists(self.DEFAULT_DATASOURCE):
                self.DEFAULT_DATASOURCE_FILENAME = '.%s' % (''.join(random.choice(string.ascii_letters) for i in range(7)))
                self.DEFAULT_DATASOURCE = '%s/%s' % (self.DEFAULT_DATASOURCE_PATH, self.DEFAULT_DATASOURCE_FILENAME)
        else:
            self.DEFAULT_DATASOURCE = ':memory:'
        self[self.NORMALIZER_KEY] = {}
        self[self.DEFAULT_NORMALIZER_KEY] = ''
        self[self.DICTIONARY_KEY] = []
        self[self.KEYWORDS_KEY] = {}
        self[self.DATASOURCE_KEY] = self.DEFAULT_DATASOURCE
        self[self.WORD_SEPARATOR_KEY] = self.DEFAULT_WORD_SEPARATOR
        self[self.TOKENIZER_OPTION_KEY] = self.DEFAULT_TOKENIZER_OPTION
        self.connection = sqlite3.connect(self[self.DATASOURCE_KEY])
        self.cursor = self.connection.cursor()
        self.normalizer_map = {}
        self.sic_builder = sic.Builder(debug_mode=debug_mode, verbose_mode=verbose_mode)
        if filename != '':
            self.load(filename)

    def __del__(self):
        # remove all temporary resources
        self.connection.close()
        if os.path.exists(self.DEFAULT_DATASOURCE):
            os.remove(self.DEFAULT_DATASOURCE)

    def save(self, filename):
        assert os.path.exists(self[self.DATASOURCE_KEY]), 'Cannot find temporary database on disk'
        logging.debug('Saving model "%s"' % (filename))
        self.cursor.close()
        self.connection.close()
        normalizers = {
            self.DEFAULT_NORMALIZER_KEY: self[self.DEFAULT_NORMALIZER_KEY],
            self.WORD_SEPARATOR_KEY: self[self.WORD_SEPARATOR_KEY],
            self.TOKENIZER_OPTION_KEY: self[self.TOKENIZER_OPTION_KEY],
            self.NORMALIZER_KEY: {normalizer_name: self[self.NORMALIZER_KEY][normalizer_name].data for normalizer_name in self[self.NORMALIZER_KEY]}
        }
        with open('%s.normalizers' % (filename), mode='wb') as f:
            pickle.dump(normalizers, f)
        logging.debug('Saved "%s"' % ('%s.normalizers' % (filename)))
        for dictionary_number in range(len(self[self.DICTIONARY_KEY])):
            with open('%s.%d.dictionary' % (filename, dictionary_number), mode='wb') as f:
                pickle.dump(self[self.DICTIONARY_KEY][dictionary_number], f)
                logging.debug('Saved "%s"' % ('%s.%d.dictionary' % (filename, dictionary_number)))
        with open('%s.keywords' % (filename), mode='wb') as f:
            pickle.dump(self[self.KEYWORDS_KEY], f)
            logging.debug('Saved "%s"' % ('%s.keywords' % (filename)))
        shutil.copyfile(self[self.DATASOURCE_KEY], '%s.attributes' % (filename))
        logging.debug('Saved "%s"' % ('%s.attributes' % (filename)))
        self.connection = sqlite3.connect(self[self.DATASOURCE_KEY])
        self.cursor = self.connection.cursor()
        logging.debug('Saved "%s"' % (filename))
        return True

    def load(self, filename):
        logging.debug('Loading model "%s"' % (filename))
        self[self.DATASOURCE_KEY] = '%s.attributes' % (filename)
        self.cursor.close()
        self.connection.close()
        with open('%s.normalizers' % (filename), mode='rb') as f:
            normalizers = pickle.load(f)
        for normalizer_name in normalizers[self.NORMALIZER_KEY]:
            self[self.NORMALIZER_KEY][normalizer_name] = self.sic_builder.build_normalizer()
            self[self.NORMALIZER_KEY][normalizer_name].data = normalizers[self.NORMALIZER_KEY][normalizer_name]
            self[self.WORD_SEPARATOR_KEY] = normalizers[self.WORD_SEPARATOR_KEY]
            self[self.TOKENIZER_OPTION_KEY] = normalizers[self.TOKENIZER_OPTION_KEY]
        self[self.DEFAULT_NORMALIZER_KEY] = normalizers[self.DEFAULT_NORMALIZER_KEY]
        logging.debug('Loaded "%s"' % ('%s.normalizers' % (filename)))
        for _filename in sorted(os.listdir(os.path.dirname(filename))) if os.path.dirname(filename) != '' else sorted(os.listdir()):
            if _filename.startswith(os.path.basename(filename) + '.') and _filename.endswith('.dictionary'):
                with open('%s/%s' % (os.path.dirname(filename), _filename) if os.path.dirname(filename) != '' else _filename, mode='rb') as f:
                    dictionary = pickle.load(f)
                    self[self.DICTIONARY_KEY].append(dictionary)
                    logging.debug('Loaded "%s"' % ('%s/%s' % (os.path.dirname(filename), _filename) if os.path.dirname(filename) != '' else _filename))
        with open('%s.keywords' % (filename), mode='rb') as f:
            keywords = pickle.load(f)
            self[self.KEYWORDS_KEY] = keywords
        logging.debug('Loaded "%s"' % ('%s.keywords' % (filename)))
        self[self.DATASOURCE_KEY] = '%s.attributes' % (filename)
        self.connection = sqlite3.connect(self[self.DATASOURCE_KEY])
        self.cursor = self.connection.cursor()
        return True

    def add_normalizer(self, normalizer_name, filename, default=False):
        logging.debug('Adding normalizer "%s" from "%s"' % (normalizer_name, filename))
        normalizer = self.sic_builder.build_normalizer(filename)
        self[self.NORMALIZER_KEY][normalizer_name] = normalizer
        self.normalizer_map[normalizer_name] = normalizer_name
        if len(self[self.NORMALIZER_KEY]) == 1 or default:
            self[self.DEFAULT_NORMALIZER_KEY] = normalizer_name
        logging.debug('Added normalizer "%s" from "%s"' % (normalizer_name, filename))
        return True

    def create_recognizer_schema(self, cursor):
        logging.debug('Creating schema for permanent storage')
        cursor.execute('create table attrs (n integer, iid integer, attr_name text, attr_value text);')
        logging.debug('Created schema for permanent storage')
        return True

    def pack_subtrie(self, trie, compressed, prefix):
        if not compressed:
            return trie, prefix
        if type(trie) != dict:
            return trie, prefix
        if prefix == self.ENTITY_KEY:
            return trie, prefix
        children = trie
        child_count = int(len(children))
        if child_count == 1:
            for key, child in children.items():
                if key == self.ENTITY_KEY:
                    if len(prefix) > 1:
                        return {prefix[1:]: trie}, prefix[0]
                    return trie, prefix
                next_prefix = prefix + key
                comp_child, comp_key = self.pack_subtrie(child, compressed, next_prefix)
                if prefix == '':
                    comp_children = {comp_key: comp_child}
                else:
                    comp_children = comp_child
                return comp_children, comp_key
        else:
            comp_children = {}
            for key, child in children.items():
                comp_child, comp_key = self.pack_subtrie(child, compressed, key)
                comp_children[comp_key] = comp_child
            if len(prefix) > 1:
                comp_children = {prefix[0]: {prefix[1:]: comp_children}}
                return comp_children[prefix[0]], prefix[0]
            return comp_children, prefix
        
    def pack_trie(self, trie, compressed):
        ret = {k: trie[k] for k in trie if k != self.CONTENT_KEY}
        ret[self.CONTENT_KEY] = {}
        for normalizer_name in trie[self.CONTENT_KEY]:
            packed = self.pack_subtrie(trie[self.CONTENT_KEY][normalizer_name], compressed, '')[0]
            ret[self.CONTENT_KEY][normalizer_name] = packed
        return ret

    def store_attributes(self, line_number, internal_id, subtrie, specs, columns):
        if self.ENTITY_KEY not in subtrie:
            subtrie[self.ENTITY_KEY] = []
        subtrie[self.ENTITY_KEY].append(line_number)
        for k in specs['fields']:
            if specs['fields'][k][3]:
                continue
            if not specs['fields'][k][1]:
                self.cursor.execute('insert into attrs (n, iid, attr_name, attr_value) select ?, ?, ?, ?;', (line_number, internal_id, k, columns[specs['fields'][k][0]]))
            else:
                _ = [self.cursor.execute('insert into attrs (n, iid, attr_name, attr_value) select ?, ?, ?, ?;', (line_number, internal_id, k, s)) for s in set(columns[specs['fields'][k][0]].split(specs['fields'][k][1]))]

    def get_dictionary_line(self, specs, entity_ids, line_numbers, line_number, line, column_separator, column_enclosure):
        columns = [x.strip(column_enclosure) for x in line.strip('\n').split(column_separator)]
        if line_number in line_numbers:
            internal_id = line_numbers[line_number]
        else:
            entity_id = columns[specs['id'][0]]
            if entity_id not in entity_ids:
                entity_ids[entity_id] = len(entity_ids)
            internal_id = entity_ids[entity_id]
            line_numbers[line_number] = internal_id
        return columns, internal_id

    def get_dictionary_synonym(self, columns, specs, word_separator, tokenizer_option=0):
        synonym, normalizer_name = columns[specs['value'][0]], None
        if self[self.NORMALIZER_KEY]:
            if specs['tokenizer']:
                if columns[specs['tokenizer'][0]] not in self.normalizer_map:
                    normalizer_name = self[self.DEFAULT_NORMALIZER_KEY]
                elif columns[specs['tokenizer'][0]] in self.normalizer_map and self.normalizer_map[columns[specs['tokenizer'][0]]] in self[self.NORMALIZER_KEY]:
                    normalizer_name = self.normalizer_map[columns[specs['tokenizer'][0]]]
            else:
                normalizer_name = self[self.DEFAULT_NORMALIZER_KEY]
        if normalizer_name is not None:
            synonym = self[self.NORMALIZER_KEY][normalizer_name].normalize(synonym, word_separator, tokenizer_option)
        return synonym, normalizer_name

    def next_trie(self, specs, compressed, tokenizer_option, word_separator):
        if len(self[self.NORMALIZER_KEY]) == 0:
            self.add_normalizer('bypass', '%s/normalizer.bypass.xml' % (os.path.abspath(os.path.dirname(__file__))))
        new_trie = {
            self.CONTENT_KEY: {normalizer_name: {} for normalizer_name in self[self.NORMALIZER_KEY]},
            self.SPECS_KEY: specs,
            self.COMPRESSED_KEY: int(compressed),
            self.TOKENIZER_OPTION_KEY: tokenizer_option,
            self.WORD_SEPARATOR_KEY: word_separator
        }
        return new_trie
