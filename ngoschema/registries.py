# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .utils.utils import GenericClassRegistry


transformers_registry = GenericClassRegistry()

deserializers_registry = GenericClassRegistry()

serializers_registry = GenericClassRegistry()

repositories_registry = GenericClassRegistry()

