import logging
import os

from pelican import signals
from pelican.contents import Content, Page
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import slugify,  copy, posixize_path


logger = logging.getLogger(__name__)


class Data(object):
    '''
    Represents a single data item from a collection.

    :param content: the string to parse, containing the original content.
    :param metadata: the metadata associated to this page (optional).
    :param settings: the settings dictionary (optional).
    :param source_path: The location of the source of this content (if any).
    :param context: The shared context between generators.
    '''

    def __init__(self, content, metadata=None, settings=None,
                 source_path=None, context=None):

        if metadata is None:
            metadata = {}
        if settings is None:
            settings = copy.deepcopy(DEFAULT_CONFIG)

        self.settings = settings
        self._content = content
        if context is None:
            context = {}
        self._context = context
        self.translations = []

        local_metadata = dict()
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            # if key in ('save_as', 'url'):
            #     key = 'override_' + key
            setattr(self, key.lower(), value)

        # also keep track of the metadata attributes available
        self.metadata = local_metadata

        #default template if it's not defined in page
        # self.template = self._get_template()

        # First, read the authors from "authors", if not, fallback to "author"
        # and if not use the settings defined one, if any.
        # if not hasattr(self, 'author'):
        #     if hasattr(self, 'authors'):
        #         self.author = self.authors[0]
        #     elif 'AUTHOR' in settings:
        #         self.author = Author(settings['AUTHOR'], settings)
        #
        # if not hasattr(self, 'authors') and hasattr(self, 'author'):
        #     self.authors = [self.author]

        # XXX Split all the following code into pieces, there is too much here.

        # manage languages
        # self.in_default_lang = True
        # if 'DEFAULT_LANG' in settings:
        #     default_lang = settings['DEFAULT_LANG'].lower()
        #     if not hasattr(self, 'lang'):
        #         self.lang = default_lang
        #
        #     self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing,
        # generate slug according to the filename
        if not hasattr(self, 'slug'):
            basename = os.path.basename(os.path.splitext(source_path)[0])
            self.slug = slugify(basename, settings.get('SLUG_SUBSTITUTIONS', ()))

        self.source_path = source_path

        # manage the date format
        # if not hasattr(self, 'date_format'):
        #     if hasattr(self, 'lang') and self.lang in settings['DATE_FORMATS']:
        #         self.date_format = settings['DATE_FORMATS'][self.lang]
        #     else:
        #         self.date_format = settings['DEFAULT_DATE_FORMAT']
        #
        # if isinstance(self.date_format, tuple):
        #     locale_string = self.date_format[0]
        #     if sys.version_info < (3, ) and isinstance(locale_string,
        #                                                six.text_type):
        #         locale_string = locale_string.encode('ascii')
        #     locale.setlocale(locale.LC_ALL, locale_string)
        #     self.date_format = self.date_format[1]
        #
        # # manage timezone
        # default_timezone = settings.get('TIMEZONE', 'UTC')
        # timezone = getattr(self, 'timezone', default_timezone)
        #
        # if hasattr(self, 'date'):
        #     self.date = set_date_tzinfo(self.date, timezone)
        #     self.locale_date = strftime(self.date, self.date_format)
        #
        # if hasattr(self, 'modified'):
        #     self.modified = set_date_tzinfo(self.modified, timezone)
        #     self.locale_modified = strftime(self.modified, self.date_format)
        #
        # # manage status
        # if not hasattr(self, 'status'):
        #     self.status = settings['DEFAULT_STATUS']
        #     if not settings['WITH_FUTURE_DATES'] and hasattr(self, 'date'):
        #         if self.date.tzinfo is None:
        #             now = SafeDatetime.now()
        #         else:
        #             now = SafeDatetime.utcnow().replace(tzinfo=pytz.utc)
        #         if self.date > now:
        #             self.status = 'draft'
        #
        # # store the summary metadata if it is set
        # if 'summary' in metadata:
        #     self._summary = metadata['summary']

        signals.content_object_init.send(self)

    def __str__(self):
        return self.source_path or repr(self)

    @property
    def content(self):
        return self._content

    def get_relative_source_path(self, source_path=None):
        """Return the relative path (from the content path) to the given
        source_path.

        If no source path is specified, use the source path of this
        content object.
        """
        if not source_path:
            source_path = self.source_path
        if source_path is None:
            return None

        return posixize_path(
            os.path.relpath(
                os.path.abspath(os.path.join(self.settings['PATH'], source_path)),
                os.path.abspath(self.settings['PATH'])
            ))


class Collection(list):
    '''An augmented list to act as Data storage'''
    def __init__(self, name, path, *args):
        self.name = name
        self.path = path
        super(Collection, self).__init__(*args)
