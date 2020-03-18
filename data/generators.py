# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import os
import yaml
import json

from pelican.generators import CachingGenerator


from .contents import Collection, Data
from .signals import (data_generator_init, data_generator_context, data_generator_preread,
                      data_generator_finalized)

logger = logging.getLogger(__name__)


SUPPORTED_FORMATS = 'json yaml yml'.split()


class DataGenerator(CachingGenerator):
    '''
    Load data into context and optionnaly render pages for them
    '''

    def __init__(self, *args, **kwargs):
        self.data = {}
        super(DataGenerator, self).__init__(*args, **kwargs)
        data_generator_init.send(self)

    def is_supported(self, name):
        paths = self.settings.setdefault('DATA_PATHS', [])
        paths = [os.path.join(p, name) for p in paths]
        extensions = SUPPORTED_FORMATS + list(self.readers.extensions)
        return any(map(os.path.isdir,paths)) or any(name.endswith(ext) for ext in extensions)

    def generate_context(self):
        for name in self.settings['DATA']:
            if not self.is_supported(name):
                logger.warning('Unsupported file format: %s', name)
                continue
            data = None
            for root in self.settings.setdefault('DATA_PATHS', []):
                path = os.path.join(root, name)
                if os.path.isdir(path):
                    data = self.context_for_dir(name, path)
                elif os.path.exists(path):
                    name, ext = os.path.splitext(name)
                    if ext in ('.yaml', '.yml'):
                        data = self.context_for_yaml(name, path)
                    elif ext == '.json':
                        data = self.context_for_json(name, path)
                    else:
                        data = self.context_for_reader(name, path)
                    break
                else:
                    continue

            if not data:
                logger.warning('Missing data: %s', name)
                continue

            self.data[name] = data

        self.context['data'] = self.data

        self.save_cache()
        self.readers.save_cache()
        data_generator_finalized.send(self)

    def context_for_dir(self, name, path):
        collection = Collection(name, path)

        for f in self.get_files(collection.path):
            item = self.get_cached_data(f, None)
            if item is None:
                try:
                    item = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Data,
                        context=self.context,
                        preread_signal=data_generator_preread,
                        preread_sender=self,
                        context_signal=data_generator_context,
                        context_sender=self)
                except Exception as e:
                    logger.error('Could not process %s\n%s', f, e,
                                 exc_info=self.settings.get('DEBUG', False))
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, item)

            self.add_source_path(item)
            collection.append(item)
        return collection

    def context_for_yaml(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                with open(path) as f:
                    data = yaml.full_load(f)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)
        return data

    def context_for_json(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                with open(path) as f:
                    data = json.load(f)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)
        return data

    def context_for_reader(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                data = self.readers.read_file(
                    base_path=self.path, path=path, content_class=Data,
                    context=self.context,
                    preread_signal=data_generator_preread,
                    preread_sender=self,
                    context_signal=data_generator_context,
                    context_sender=self)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)

        self.add_source_path(data)
        return data

    #
    # def generate_output(self, writer):
    #     for page in chain(self.translations, self.pages,
    #                       self.hidden_translations, self.hidden_pages):
    #         writer.write_file(
    #             page.save_as, self.get_template(page.template),
    #             self.context, page=page,
    #             relative_urls=self.settings['RELATIVE_URLS'],
    #             override_output=hasattr(page, 'override_save_as'))
    #     data_writer_finalized.send(self, writer=writer)


def get_generators(sender, **kwargs):
    return DataGenerator
