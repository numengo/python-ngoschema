# *- coding: utf-8 -*-
"""
Json de/serializer wrapper using standard json library

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import gettext
import json
import logging
from builtins import object
from builtins import str

from python_jsonschema_objects.util as ProtocolJSONEncoder

from ._de_serializer import De_Serializer

_ = gettext.gettext

class Json(De_Serializer):
    logger = logging.getLogger(__name__)

    def loads(self, stream, **opts):
        data = json.load(stream, **opts)
        return data

    def dumps(self, data, **opts):
        enc = ProtocolJSONEncoder(**opts)
        return enc.encode(data)

