import os
import logging
import random
import string
import sqlite3
import sic
import pickle
import shutil

class Model(dict):
    """This class is a dict that stores tries and metadata, and provides functions and methods associated with the storage."""

    def __init__(self, filename='', storage_location='', debug_mode=False, verbose_mode=False):
        """Creates Model instance.

        Args:
            str *filename*: if provided, loads model from disk, see load() method
            str *storage_location*:
        """
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

    def destroy(self):
        """Closes connection, removes temporary database."""
        self.connection.close()
        if os.path.exists(self.DEFAULT_DATASOURCE):
            os.remove(self.DEFAULT_DATASOURCE)

    def __del__(self):
        """Desctructor."""
        try:
            self.destroy()
        except:
            pass

    def __enter__(self):
        """Enter `with`."""
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """Exit `with`."""
        self.destroy()

    def save(self, filename):
        """Saves model to disk.
        Note: this will throw exception if temporary database is stored in memory.

        Args:
            str *filename*: path and filename prefix for names of files that will be written.

        Example: model.save('filename') will write the following files:
            filename.normalizers
            filename.*.dictionary (can be multiple files, depends on model settings)
            filename.keywords
            filename.attributes
        """
        try:
            assert os.path.exists(self[self.DATASOURCE_KEY]), 'Cannot find temporary database on disk'
            assert len(self[self.DICTIONARY_KEY]) > 0, 'Model is empty, nothing to save'
        except Exception as e:
            self.destroy()
            raise e
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
        """Loads model from disk.

        Args:
            str *filename*: path and filename prefix for names of files that represent the model on disk.

        Example: model.load('filename') will attempt reading following files:
            filename.normalizers
            filename.*.dictionary
            filename.keywords
            filename.attributes
        """
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
        """Adds normalization unit to the model.

        Args:
            str *normalizer_name*: name of normalization unit
            str *filename*: path and name of configuration file
            bool *default*: if True, model will use this normalization unit by default
        """
        logging.debug('Adding normalizer "%s" from "%s"' % (normalizer_name, filename))
        normalizer = self.sic_builder.build_normalizer(filename)
        self[self.NORMALIZER_KEY][normalizer_name] = normalizer
        self.normalizer_map[normalizer_name] = normalizer_name
        if len(self[self.NORMALIZER_KEY]) == 1 or default:
            self[self.DEFAULT_NORMALIZER_KEY] = normalizer_name
        logging.debug('Added normalizer "%s" from "%s"' % (normalizer_name, filename))
        return True

    def create_recognizer_schema(self, cursor):
        """Creates tables in the database that stores attributes of entities.

        Args:
            sqlite3.connect.cursor *cursor*: cursor to use for throwing queries
        """
        logging.debug('Creating schema for permanent storage')
        cursor.execute('create table attrs (n integer, iid integer, attr_name text, attr_value text);')
        logging.debug('Created schema for permanent storage')
        return True

    def pack_subtrie(self, trie, compressed, prefix):
        """Recursively compresses a trie.
        Returns tuple (dict compressed_trie, str prefix).

        Args:
            dict *trie*: object representing a trie
            bool *compressed*: whether a given trie must be compressed
            str *prefix*: compressed prefix of a branch
        """
        if not compressed:
            return trie, prefix
        # if type(trie) != dict:
        #     return trie, prefix
        if prefix == self.ENTITY_KEY:
            return trie, prefix
        children = trie
        child_count = int(len(children))
        if child_count == 1:
            for key in children:
                if key == self.ENTITY_KEY:
                    if len(prefix) > 1:
                        return {prefix[1:]: trie}, prefix[0]
                    return trie, prefix
                next_prefix = prefix + key
                if not isinstance(children[key], dict):
                    return children[key], next_prefix
                comp_child, comp_key = self.pack_subtrie(children[key], compressed, next_prefix)
                if prefix == '':
                    comp_children = {comp_key: comp_child}
                else:
                    comp_children = comp_child
                return comp_children, comp_key
        else:
            comp_children = {}
            for key in children:
                comp_child, comp_key = self.pack_subtrie(children[key], compressed, key)
                comp_children[comp_key] = comp_child
            if len(prefix) > 1:
                comp_children = {prefix[0]: {prefix[1:]: comp_children}}
                return comp_children[prefix[0]], prefix[0]
            return comp_children, prefix
        
    def pack_trie(self, trie, compressed):
        """Compresses all tries in a model.
        Returns dict that contains all compressed tries.

        Args:
            dict *trie*: part of model that contains tries
            bool *compressed*: whether tries in a given structure must be compressed
        """
        ret = {k: trie[k] for k in trie if k != self.CONTENT_KEY}
        ret[self.CONTENT_KEY] = {}
        for normalizer_name in trie[self.CONTENT_KEY]:
            packed = self.pack_subtrie(trie[self.CONTENT_KEY][normalizer_name], compressed, '')[0]
            ret[self.CONTENT_KEY][normalizer_name] = packed
        return ret

    def store_attributes(self, line_number, internal_id, subtrie, specs, columns):
        """Flags terminus of a trie and writes attributes of an entry to the temporary database.

        Args:
            int *line_number*: number of line in a file that is supposed to be being read
            int *internal_id*: internally assigned ID of an entity
            dict *subtrie*: subtrie that is being constructed
            dict *specs*: specs for columns in a file that is supposed to be being read
            list *columns*: values in columns (attributes) in a file that is supposed to be being read
        """
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
        """Extracts values of columns in a file and associates them with internal entity ID.
        Returns tuple (list *column_values*, int *internal_id*).

        Args:
            dict *specs*: specs for columns in a file that is supposed to be being read
            dict *entity_ids*: map between real entity IDs and internally generated entity IDs
            dict *line_numbers*: map between line numbers and internally generated entity IDs
            int *line_number*: number of line that is being parsed
            str *line*: line that is being parsed
            str *column_separator*: delimiter to split columns
            str *column_enclosure*: any string that columns are supposed to be trimmed of
        """
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
        """Extracts normalized synonym from list of column values.
        Returns tuple (str *normalized_synonym*, str *normalization_unit_name*).

        Args:
            list *columns*: list of columns in a file that is supposed to be being read
            dict *specs*: specs for columns in a file that is supposed to be being read
            str *word_separator*: word separator to use for tokenization
            int *tokenizer_option*: tokenizer mode (see documentation for normalization for details)
        """
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
        """Creates and returns dict that contains empty trie and metadata.

        Args:
            dict *specs*: specs for columns in a file that is supposed to be being read for trie construction
            bool *compressed*: whether constructed trie(s) must be compressed
            int *tokenizer_option*: tokenizer mode (see documentation for normalization for details)
            str *word_separator*: word separator to use for tokenization
        """
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
