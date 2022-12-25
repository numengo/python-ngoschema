# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pandas as pd
import geopandas as gpd
import numpy as np

from ngoschema.protocols import with_metaclass, SchemaMetaclass, ObjectProtocol


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
