# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd
from collections import OrderedDict
import gettext

from ..protocols.loader import Loader, Saver
from ..protocols.repository import Repository
from ..registries import repositories_registry
from ..serializers.csv_serializer import CsvSerializer
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol
from ..models.datasets import Dataframe
from .file_repositories import FileRepository

_ = gettext.gettext


class MemoryRepository(with_metaclass(SchemaMetaclass, Repository)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/MemoryRepository'
    #_catalog = None
    many = True

    def __init__(self, value=None, meta_opts=None, **opts):
        from ..datatypes import Array
        #from ..protocols.array_protocol import ArrayProtocol
        # items=False to avoid validation at this point (_content not initialized)
        ObjectProtocol.__init__(self, items=False, **opts)
        meta_opts = meta_opts or {}
        meta_opts.setdefault('instanceClass', self.instanceClass)
        meta_opts.setdefault('saver', self.saver)
        meta_opts.setdefault('loader', self.loader)
        meta_opts.setdefault('serializer', self.serializer)
        meta_opts.setdefault('deserializer', self.deserializer)
        meta_opts.setdefault('validator', self.validator)
        meta_opts.setdefault('session', self.session)
        meta_opts.setdefault('many', self.many)
        Repository.__init__(self, **(meta_opts or {}))
        self._content = Array(items=self.instanceClass, maxItems=1 if not self._many else None)(value)
        #self._catalog = OrderedDict({v.identityKeys: v for v in content})

    def get_content(self):
        return self._content

    def get_index(self):
        unique_pk = len(self.instanceClass._primaryKeys) == 1
        return [e.identityKeys[0] if unique_pk else tuple(e.identityKeys) for e in self._content]

    def __repr__(self):
        return f'{self.qualname()}[{len(self._content)}]'
        #return f'{self.qualname()}[{len(self._catalog)}]'

    def __str__(self):
        return f'{self.qualname()}[{len(self._content)}]'
        #return f'{self.qualname()}[{len(self._catalog)}]'

    #def __contains__(self, item):
    #    return item in [e.identityKeys for e in self._content]
#        return item in self._catalog

    def resolve_fkey(self, identity_keys):
        for e in self._content:
            if e.identityKeys == identity_keys:
                return e
        #return self._catalog[identity_keys]

    @staticmethod
    def _commit(self, value, save=False, **opts):
        _("""Optionally load the value (at least validate it) and add it to content """)
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            # check/set identity keys
            pk = value.identityKeys
            for i, k in enumerate(pk):
                iks = [c.identityKeys[i] for c in self._content]
                if k is None:
                    k = max([-1] + iks) + 1
                    value._set_data(value.primaryKeys[i], k)
            #pk = value.identityKeys
            #self._catalog[value._identityKeys] = value
            for i, c in enumerate(self._content):
                if pk == c.identityKeys:
                    self._content[i] = value
                    break
            else:
                self._content.append(value)
        else:
            self._content = value
        self._items_touch('content')
        return self._content


class DataframeRepository(with_metaclass(SchemaMetaclass, Repository)):
    _id = r"https://numengo.org/ngoschema#/$defs/repositories/$defs/DataframeRepository"
    _lazyLoading = True

    def __init__(self, value=None, meta_opts=None, **opts):
        ObjectProtocol.__init__(self, **opts)
        Repository.__init__(self, **(meta_opts or {}))

    #@property
    #def index(self):
    #    return self.dataframe.index.to_list()

    def get_by_id(self, *identity_keys):
        row = self.dataframe.loc[identity_keys]
        ic = self.instanceClass
        if ic:
            pks = {pk: ik for pk, ik in zip(ic._primaryKeys, identity_keys)}
            return ic(**pks, **row, session=self.session)
        return row

    def query(self, *attrs, **attrs_value):
        # we are going to filter the df not by its index. put back the index in df data
        df = self.df.reset_index()
        for k, v in attrs_value.items():
            df = df[df[k] == v]
        ic = self.instanceClass
        return [ic(**row, session=self.session) for _, row in df.iterrows()]


class CsvFileRepository(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/repositories/$defs/CsvFileRepository"
    #_loader = pd.read_csv

    @staticmethod
    def _serialize(self, value, **opts):
        return ObjectProtocol._serialize(self, value, **opts)
        #return CsvSerializer._serialize_csv(self, value, **opts)

    @staticmethod
    def _deserialize(self, value, **opts):
        return ObjectProtocol._deserialize(self, value, **opts)
        #return CsvSerializer._serialize_csv(self, value, **opts)

    def get_dataframe(self):
        return pd.read_csv(str(self.csv))

    def get_by_id(self, *identity_keys):
        return DataframeRepository.get_by_id(self, *identity_keys)
