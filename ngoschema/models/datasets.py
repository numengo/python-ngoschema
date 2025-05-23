# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd

from ngoschema.protocols import with_metaclass, SchemaMetaclass, ObjectProtocol
from ngoschema.models.instances import Instance


class Enum(with_metaclass(SchemaMetaclass)):
    #_id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/Enum"

    def __init__(self, name=None, context=None, *args, **kwargs):
        if kwargs:
            names = kwargs.keys()
            values = kwargs.values()
        else:
            names = list(args) if args else kwargs.pop('names', [])
            values = range(len(names))
        as_dict = {n: v for n, v in zip(names, values)}
        as_dict['name'] = name
        as_dict['names'] = names
        as_dict['values'] = values
        Instance.__init__(self, value=as_dict, context=context)


class Series(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/Series"


class Dataframe(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/Dataframe"


class HasDataframe(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/HasDataframe"


class HasSeries(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/HasSeries"
    _lazyLoading = True

    def get_series(self):
        index = self.index
        ret = self._data['series']
        if ret is None and index:
            ret = pd.Series([self[k] for k in index], index)
        return ret


class DataframeSubset(with_metaclass(SchemaMetaclass)):
    _id = r"https://numengo.org/ngoschema#/$defs/datasets/$defs/DataframeSubset"
    _lazyLoading = True

    def get_subset(self):
        df = self.dataframe
        if df is not None:
            if self.ids:
                for k, v in list(zip(self.subkeys, self.ids)):
                    df = df[df[k] == v]
            else:
                df = df.copy()
            return df
