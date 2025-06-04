# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd
from collections import OrderedDict
from collections.abc import Sequence
import gettext

from ..protocols.loader import Loader, Saver
from ..protocols.repository import Repository
from ..registries import repositories_registry
from ..serializers.csv_serializer import CsvSerializer
from ..protocols import SchemaMetaclass, with_metaclass, ObjectProtocol, ArrayProtocol
from ..models.datasets import Dataframe

_ = gettext.gettext


class MemoryRepository(with_metaclass(SchemaMetaclass, Repository)):
    _id = 'https://numengo.org/ngoschema#/$defs/repositories/$defs/MemoryRepository'
    # catalog is used for o(1) access rather than o(n) if we got through the array
    _catalog = OrderedDict
    _many = True

    def __init__(self, value=None, meta_opts=None, many=None, **opts):
        from ..datatypes import Array
        #from ..protocols.array_protocol import ArrayProtocol
        # hack to initialize ObjectProtocol with _many value (if repo not defined with a schema like MapRepository)
        many = many if many is not None else self._many
        # items=False to avoid validation at this point (_content not initialized)
        ObjectProtocol.__init__(self, value=None, items=False, many=many, **opts)
        meta_opts = meta_opts or {}
        meta_opts.setdefault('filepath', self.filepath)
        meta_opts.setdefault('instanceClass', self.instanceClass)
        meta_opts.setdefault('saver', self.saver)
        meta_opts.setdefault('loader', self.loader)
        meta_opts.setdefault('serializer', self.serializer)
        meta_opts.setdefault('deserializer', self.deserializer)
        meta_opts.setdefault('validator', self.validator)
        meta_opts.setdefault('session', self.session)
        meta_opts.setdefault('many', self.many)
        Repository.__init__(self, **(meta_opts or {}))
        self._content = Array(items=self.instanceClass, maxItems=1 if not many else None)(value)
        self._catalog = self._catalog({self._get_idk(self, v): v for v in self._content})

    # overload this methods to avoid conflicts with inherited Serializers basis
    @staticmethod
    def _deserialize(self, value, **opts):
        return ObjectProtocol._deserialize(self, value, **opts)

    @staticmethod
    def _serialize(self, value, **opts):
        return ObjectProtocol._serialize(self, value, **opts)

    @staticmethod
    def _load_file(self, filepath, **opts):
        Repository._load_file(self, filepath, **opts)
        if self._many:
            self._catalog.update({self._get_idk(self, v): v for v in self._content})
            self._logger.info(f'LOAD %s items', len(self._content))
        self._items_touch('content')
        return self._content

    def get_content(self):
        return self._content

    def get_index(self):
        #unique_pk = len(self.instanceClass._primaryKeys) == 1
        #return [e.identityKeys[0] if unique_pk else tuple(e.identityKeys) for e in self._content]
        # deals with key modifiers
        return list(self._catalog.keys())

    def __repr__(self):
        #return f'{self.qualname()}[{len(self._content)}]'
        return f'{self.qualname()}[{len(self._catalog)}]'

    def __str__(self):
        #return f'{self.qualname()}[{len(self._content)}]'
        return f'{self.qualname()}[{len(self._catalog)}]'

    def __contains__(self, item):
        # o(1) with dict access, o(n) is going through content
        # also deals with possible key modifiers in catalog class
        #return item in [e.identityKeys for e in self._content]
        if isinstance(item, Sequence) and not isinstance(item, str):
            item = tuple(item)
            if len(item) == 1:
                item = item[0]
        return item in self._catalog

    def get_by_id(self, *identity_keys):
        # o(1) with dict access, o(n) is going through content
        #for e in self._content:
        #    if e.identityKeys == identity_keys:
        #        return e
        pkc = identity_keys if len(identity_keys) > 1 else identity_keys[0]
        ret = self._catalog[pkc]
        # instanciate object if not done already
        if ret is not None and not isinstance(ret, self._instanceClass):
            ret = self._instanceClass(ret)
        return ret

    @staticmethod
    def _get_idk(self, value):
        if isinstance(value, self._instanceClass):
            idk = value.identityKeys
        else:
            idk = [value.get(pk) for pk in self._instanceClass._primaryKeys]
        return idk[0] if idk and len(idk) == 1 else idk

    @staticmethod
    def _commit(self, value, save=False, **opts):
        """Optionally load the value (at least validate it) and add it to content """
        from ngoschema.models.instances import Entity
        many = opts.get('many', False)
        opts.setdefault('pyType', self._instanceClass)
        value = self._saver._save(self, value, **opts) if save else value
        if self._many:
            values = [value] if not many else value
            for value in values:
                if not isinstance(value, Entity):
                    self._content.append(value)
                    pkc = self._get_idk(self, value)
                    assert pkc, 'no primary key in value ' + str(value)
                    self._catalog[pkc] = value
                else:
                    # check/set identity keys
                    pk = value.identityKeys
                    for i, k in enumerate(pk):
                        pkn = self._instanceClass._primaryKeys[i]
                        t = self._instanceClass._get_primaryKeysType(self._instanceClass)[i]
                        if k is None:
                            if t._auto:
                                iks = [c.identityKeys[i] for c in self._content]
                                k = max([-1] + iks) + 1
                                value._set_data(pkn, k)
                            else:
                                raise Exception("missing primary key '%s' in object %s" % (pkn, value))
                    # identityKeys might have changed if auto, but pk is same size
                    pkc = self._get_idk(self, value)
                    if pkc in self._catalog:
                        self._logger.info('overwriting existing object (%s) in repository.' %  pk)
                        v = self._catalog[pkc]
                        i = self._content.index(v)
                        self._content[i] = value
                    else:
                        self._content.append(value)
                    self._catalog[pkc] = value
        else:
            self._content = value
            if isinstance(value, Entity):
                pkc = self._get_idk(self, value)
                if pkc is not None:
                    self._catalog[pkc] = value
        self._items_touch('content')
        return self._content


class DataframeRepository(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/repositories/$defs/DataframeRepository"
    _lazyLoading = True

    def __init__(self, value=None, meta_opts=None, **opts):
        MemoryRepository.__init__(self, value=value, meta_opts=meta_opts, **opts)

    #@property
    def get_index(self):
        return self.dataframe.index.to_list()

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
