"""
Whoosh based index/search system for TiddlyWeb.
"""
import os, sys

import logging

from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.qparser import MultifieldParser, QueryParser

from tiddlywebplugins import get_store, replace_handler

from tiddlyweb.manage import make_command
from tiddlyweb.stores import StorageInterface
from tiddlyweb.web.sendtiddlers import send_tiddlers

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

IGNORE_PARAMS = []

SEARCH_DEFAULTS = {
        'wsearch.schema': dict(title=TEXT, id=ID(stored=True, unique=True),
            bag=TEXT, text=TEXT, modified=ID, modifier=ID, created=ID,
            tags=TEXT, field_1=TEXT, field_2=TEXT),
        'wsearch.indexdir': 'indexdir',
        'wsearch.default_fields': ['text', 'title'],
        }

INDEX = None
WRITER = None
SEARCHER = None
PARSER = None

def init(config_in):
    if 'selector' in config_in:
        replace_handler(config_in['selector'], '/search', dict(GET=whoosh_search))
    else:
        # twanager
        global config
        config = config_in

def whoosh_search(environ, start_response):
    """
    Handle incoming /search?q=<query> and
    return the found tiddlers.
    """
    search_query = query_dict_to_search_string(
            environ['tiddlyweb.query']) or ''

    filters = environ['tiddlyweb.filters']
    store = environ['tiddlyweb.store']
    usersign = environ['tiddlyweb.usersign']

    tmp_bag = Bag('tmp_bag', tmpbag=True, searchbag=True)
    bag_readable = {}

    tiddlers = []
    if search_query:
        logging.debug('search query is %s' % search_query)
        results = search(environ['tiddlyweb.config'], search_query)
        logging.debug('got search results from store')

    for result in results:
        bag, title = result['id'].split(':', 1)
        tiddler = Tiddler(title, bag)
        try:
            if bag_readable[tiddler.bag]:
                tmp_bag.add_tiddler(store.get(tiddler))
        except KeyError:
            bag = Bag(tiddler.bag)
            bag.skinny = True
            bag = store.get(bag)
            try:
                bag.policy.allows(usersign, 'read')
                tmp_bag.add_tiddler(store.get(tiddler))
                bag_readable[tiddler.bag] = True
            except(ForbiddenError, UserRequiredError):
                bag_readable[tiddler.bag] = False

    if len(filters):
        tiddlers = control.filter_tiddlers_from_bag(tmp_bag, filters)
        tmp_bag = Bag('tmp_bag', tmpbag=True, searchbag=True)
        tmp_bag.add_tiddlers(tiddlers)

    return send_tiddlers(environ, start_response, tmp_bag)


@make_command()
def wsearch(args):
    """Search the whoosh index for provided terms."""
    query = ' '.join(args)
    ids = search(config, query)
    print ids
    for result in ids:
        bag, title = result['id'].split(':')
        print "%s:%s" % (bag, title)


@make_command()
def wreindex(args):
    """ Rebuild the entire whoosh index."""
    store = get_store(config)
    writer = get_writer(config)
    schema = config.get('wsearch.schema', SEARCH_DEFAULTS['wsearch.schema'])
    for bag in store.list_bags():
        bag = store.get(bag)
        for tiddler in bag.list_tiddlers():
            tiddler = store.get(tiddler)
            index_tiddler(tiddler, schema, writer)
    writer.commit()


def get_index(config):
    """
    Return the current index object if there is one.
    If not attempt to open the index in wsearch.indexdir.
    If there isn't one in the dir, create one. If there is 
    not dir, create the dir.
    """
    global INDEX
    if INDEX:
        return INDEX
    index_dir = config.get('wsearch.indexdir', SEARCH_DEFAULTS['wsearch.indexdir'])
    try:
        index = open_dir(index_dir)
    except (IOError, EmptyIndexError):
        try:
            os.mkdir(index_dir)
        except OSError:
            pass
        schema = config.get('wsearch.schema', SEARCH_DEFAULTS['wsearch.schema'])
        index = create_in(index_dir, Schema(**schema))
    INDEX = index
    return INDEX


def get_writer(config):
    """
    Return a writer based on config insructions.
    """
    global WRITER
    if WRITER:
        return WRITER
    WRITER = get_index(config).writer()
    return WRITER


def get_searcher(config):
    """
    Return a searcher based on config instructions.
    """
    global SEARCHER
    if SEARCHER:
        return SEARCHER
    SEARCHER = get_index(config).searcher()
    return SEARCHER

def get_parser(config):
    global PARSER
    if PARSER:
        return PARSER
    schema = config.get('wsearch.schema', SEARCH_DEFAULTS['wsearch.schema'])
    default_fields = config.get('wsearch.default_fields',
            SEARCH_DEFAULTS['wsearch.default_fields'])
    PARSER = MultifieldParser(default_fields, schema=Schema(**schema))
    return PARSER


def query_parse(config, query):
    parser = get_parser(config)
    return parser.parse(query)


def search(config, query):
    """
    Perform a search, returning a whoosh result
    set.
    """
    searcher = get_searcher(config)
    query = query_parse(config, unicode(query))
    print query
    print searcher
    return searcher.search(query)


def index_tiddler(tiddler, schema, writer):
    """
    Index the given tiddler with the given schema using
    the provided writer.

    The schema dict is read to find attributes and fields
    on the tiddler.
    """
    print 'indexing tiddler: %s' % tiddler.title
    data = {}
    for key in schema:
        try:
            try:
                value = getattr(tiddler, key)
            except AttributeError:
                value = tiddler.fields[key]
            try:
                data[key] = unicode(value.lower())
            except AttributeError:
                value = ' '.join(value)
                data[key] = unicode(value.lower())
        except KeyError:
            pass
    data['id'] = _tiddler_id(tiddler)
    print data
    writer.update_document(**data)


def _tiddler_id(tiddler):
    return '%s:%s' % (tiddler.bag, tiddler.title)


def _tiddler_written_handler(self, tiddler):
    schema = self.environ['tiddlyweb.config'].get('wsearch.schema',
            SEARCH_DEFAULTS['wsearch.schema'])
    writer = get_writer(self.environ['tiddlyweb.config'])
    index_tiddler(tiddler, schema, writer)
    writer.commit()


StorageInterface.tiddler_written = _tiddler_written_handler


def query_dict_to_search_string(query_dict):
    terms = []
    while query_dict:
        keys = query_dict.keys()
        key = keys.pop()
        values = query_dict[key]
        del query_dict[key]
        if key in IGNORE_PARAMS:
            continue

        if key == 'q':
            terms.extend(values)
        else:
            if key.endswith('_field'):
                prefix = key.rsplit('_', 1)[0]
                value_key = '%s_value' % prefix
                key = values[0].lower().replace(' ', '_')
                try:
                    values = query_dict[value_key]
                    del query_dict[value_key]
                except KeyError:
                    values = []
                if not values:
                    continue
            elif key.endswith('_value'):
                prefix = key.rsplit('_', 1)[0]
                field_key = '%s_field' % prefix
                try:
                    key = query_dict[field_key][0].lower().replace(' ', '_')
                    del query_dict[field_key]
                except KeyError:
                    key = ''
                if not key:
                    continue

            if key == 'avid' and not values[0].isdigit():
                continue

            for value in values:
                if ' ' in key or ' ' in value:
                    terms.append('"%s:%s"' % (key, value))
                else:
                    terms.append('%s:%s' % (key, value))
    return ' '.join(terms)
