"""
Description of My Plugin.
"""

import os
import urllib2
import urlparse

from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list
from tiddlyweb.serializer import Serializer
from html5lib import HTMLParser, treebuilders

ACCEPTED_RECIPE_TYPES = ['tiddler', 'plugin', 'recipe']
ACCEPTED_TIDDLER_TYPES = ['js', 'tid', 'tiddler']

# add twimport in here when ready
#def init(config):
#    pass


def recipe_to_urls(url):
    """
    Provided a url or path to a recipe, explode the recipe to
    a list of URLs of tiddlers (of various types).
    """
    try:
        handle = urllib2.urlopen(url)
    except ValueError:
        # If ValueError happens again we want it to raise
        url = 'file:' + os.path.abspath(url)
        handle = urllib2.urlopen(url)

    urls = []
    for line in handle.readlines():
        line = line.lstrip().rstrip()
        target_type, target = line.split(':', 1)
        if target_type in ACCEPTED_RECIPE_TYPES:
            target = target.lstrip().rstrip()
            # Check to see if the target is a URL (has a scheme)
            # if not we want to join it to the current url before
            # carrying on.
            scheme, _ = urllib2.splittype(target)
            if not scheme:
                target = urlparse.urljoin(url, target)
            if target_type == 'recipe':
                urls.extend(recipe_to_urls(target))
            else:
                urls.append(target)
    return urls


def url_to_tiddler(url):
    """
    Given a url to a tiddlers of some form,
    return a Tiddler object.
    """
    # XXX dupes with above for the moment
    try:
        handle = urllib2.urlopen(url)
    except ValueError:
        # If ValueError happens again we want it to raise
        url = 'file:' + os.path.abspath(url)
        handle = urllib2.urlopen(url)

    if url.endswith('.js'):
        tiddler = from_plugin(url, handle)
    elif url.endswith('.tid'):
        tiddler = from_tid(url, handle)
    elif url.endswith('.tiddler'):
        tiddler = from_tiddler(url, handle)
    else:
        # binary tiddler
        tiddler = from_special(url, handle)
    return tiddler


def from_plugin(uri, handle):
    """
    generates Tiddler from a JavaScript (and accompanying meta) file
    If there is no .meta file, title and tags assume default values.
    """
    default_title = _get_title_from_uri(uri)
    default_tags = "systemConfig"

    meta_uri = "%s.meta" % uri
    try:
        meta_content = _get_url(meta_uri)
    except (urllib2.HTTPError, urllib2.URLError, IOError, OSError):
        meta_content = "title: %s\ntags: %s\n" % (default_title, default_tags)
    try:
        title = [line for line in meta_content.split("\n")
                if line.startswith("title:")][0]
        title = title.split(":", 1)[1].strip()
    except IndexError:
        title = default_title
    tiddler_meta = "\n".join(line for line in meta_content.split("\n")
            if not line.startswith("title:")).rstrip()

    plugin_content = handle.read()
    tiddler_text = "%s\n\n%s" % (tiddler_meta, plugin_content)

    return _from_text(title, tiddler_text)


def from_special(uri, handle):
    """
    This is borrowed from ben G's bimport.
    """
    title = _get_title_from_uri(uri)
    # XXX: will mime type guessing always work?
    content_type = handle.headers.type
    data = handle.read()

    tiddler = Tiddler(title)
    tiddler.type = content_type
    tiddler.text = data

    return tiddler


def from_tid(uri, handle):
    """
    generates Tiddler from a TiddlyWeb-style .tid file
    """
    title = _get_title_from_uri(uri)
    return _from_text(title, handle.read())


def from_tiddler(uri, handle):
    """
    generates Tiddler from a Cook-style .tiddler file
    """
    content = handle.read()

    parser = HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
    content = _escape_brackets(content)
    doc = parser.parse(content)
    node = doc.find("div")

    return _get_tiddler_from_div(node)


def _escape_brackets(content):
    """
    escapes angle brackets in tiddler's HTML representation
    """
    open_pre = content.index("<pre>")
    close_pre = content.rindex("</pre>")
    start = content[0:open_pre + 5]
    middle = content[open_pre + 5:close_pre]
    end = content[close_pre:]
    middle = middle.replace(">", "&gt;").replace("<", "&lt;")
    return start + middle + end


def _get_title_from_uri(uri):
    """
    Turn a uri of tiddler into the title of a tiddler,
    by looking at the final segment of the path.
    """
    title = uri.split("/")[-1]
    title = _strip_extension(title)
    title = urllib2.unquote(title)
    if not type(title) == unicode:
        title = unicode(title, "utf-8")
    return title


def _strip_extension(title):
    """
    If the title ends with a tiddler extension, then strip
    it off. Otherwise, leave it.
    """
    name, extension = title.rsplit('.', 1)
    if extension in ACCEPTED_TIDDLER_TYPES:
        return name
    else:
        return title


def _get_url(url):
    """
    Load a URL and decode it to unicode.
    """
    content = urllib2.urlopen(url).read()
    content = unicode(content, "utf-8")
    return content.replace("\r", "")


def _from_text(title, content):
    """
    generates Tiddler from an RFC822-style string

    This corresponds to TiddlyWeb's text serialization of TiddlerS.
    """
    tiddler = Tiddler(title)
    serializer = Serializer("text")
    serializer.object = tiddler
    serializer.from_string(content)
    return tiddler


def _get_tiddler_from_div(node):
    """
    Create a Tiddler from an HTML div element.
    """
    tiddler = Tiddler(node['title'])
    try:
        tiddler.text = _html_decode(node.find('pre').contents[0])
    except IndexError:
        # there are no contents in the tiddler
        tiddler.text = ''

    for attr, _ in node.attrs:
        data = node.get(attr, None)
        if data and attr != 'tags':
            if attr in (['modifier', 'created', 'modified']):
                tiddler.__setattr__(attr, data)
            elif (attr not in ['title', 'changecount'] and
                    not attr.startswith('server.')):
                tiddler.fields[attr] = data
    if not node.get('modified', None) and tiddler.created:
        tiddler.modified = tiddler.created
    tiddler.tags = string_to_tags_list(node.get('tags', ''))

    return tiddler


def _html_decode(text):
    """
    Decode HTML entities used in TiddlyWiki content into the 'real' things.
    """
    return text.replace('&gt;', '>').replace('&lt;', '<').replace(
            '&amp;', '&').replace('&quot;', '"')