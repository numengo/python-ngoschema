# *- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import deque, OrderedDict
from collections.abc import Mapping, Sequence

from ..exceptions import ValidationError, ConversionError
from ..utils import ReadOnlyChainMap as ChainMap
from ..utils.utils import to_list
from ..decorators import log_exceptions
from ..managers.type_builder import register_type
from ..protocols.serializer import Serializer
from .type import Type
from .constants import _True
from .collection import CollectionDeserializer, CollectionSerializer, Collection
from .strings import String


class ArrayDeserializer(CollectionDeserializer):
    _collType = list
    _minItems = 0
    _maxItems = None
    _uniqueItems = False
    _asString = False
    _strDelimiter = ','

    def __init__(self, minItems=None, maxItems=None, uniqueItems=None, asString=None, strDelimiter=None, **opts):
        self._minItems = minItems or self._minItems
        self._maxItems = maxItems or self._maxItems
        self._uniqueItems = uniqueItems or self._uniqueItems
        self._asString = asString or self._asString
        self._strDelimiter = strDelimiter or self._strDelimiter
        CollectionDeserializer.__init__(self, **opts)

    @staticmethod
    def _convert(self, value, **opts):
        value = self._collType([value[k] for k in self._call_order(self, value, **opts)])
        return CollectionDeserializer._convert(self, value, **opts)

    @staticmethod
    def _deserialize(self, value, **opts):
        value = CollectionDeserializer._deserialize(self, value, **opts)
        #split_string = self._asString if split_string is None else split_string
        #str_del = self._strDelimiter if str_del is None else str_del
        #if String.check(value, convert=False):
        # String.check has triggers unexpected evaluations for unused error printing
        if isinstance(value, str):
            split_string = opts.get('split_string', self._asString)
            str_del = opts.get('strDelimiter', self._strDelimiter)
            value = [s.strip() for s in value.split(str_del)] if split_string else [value]
        else:
            value = list(value) if isinstance(value, (Sequence, deque)) else [value]
        many = opts.get('many', self._many)
        lv = len(value)
        if lv > 1 and not many:
            raise ConversionError("Only one value is expected (%i): %s" % (lv, value))
        value += [None] * max(0, self._minItems - lv)
        return self._collType(value)

    @staticmethod
    def _validate(self, value, **opts):
        value = CollectionDeserializer._validate(self, value, **opts)
        if self._uniqueItems:
            hashes = set([hash(v) for v in value])
            if len(hashes) != len(value):
                ValidationError('Duplicate items in %s.' % value)
        return value

    @staticmethod
    def _call_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))


class ArraySerializer(CollectionSerializer, ArrayDeserializer):
    _deserializer = ArrayDeserializer

    def __init__(self, **opts):
        CollectionSerializer.__init__(self, **opts)

    @staticmethod
    def _print_order(self, value, **opts):
        # better later including dependencies
        return range(len(value))

    @staticmethod
    def _serialize(self, value, **opts):
        as_string = opts.get('as_string', self._asString)
        value = CollectionSerializer._serialize(self, value, **opts)
        value = self._collType([value[k] for k in self._print_order(self, value, **opts)])
        if as_string:
            value = self._strDelimiter.join([String.serialize(v, **opts) for v in value])
        return value


@register_type('array')
class Array(Collection, ArraySerializer):
    _many = True
    _serializer = ArraySerializer
    _deserializer = ArrayDeserializer
    _pyType = list
    _itemsIsList = False
    _default = []

    @classmethod
    def is_array(cls):
        return True

    def __init__(self, items=None, **opts):
        # split the schema to isolate items schema and object schema
        from ..managers.type_builder import type_builder
        cls_name = f'{self.__class__.__name__}_{id(self)}'
        if isinstance(items, Mapping):
            self._items = type_builder.build(f'{cls_name}/items', items)
        elif isinstance(items, Sequence):
            self._itemsIsList = True
            self._items = [type_builder.build(f'{cls_name}/items/{i}', item)
                               for i, item in enumerate(items)]
        else:
            self._items = items or _True()
        Collection.__init__(self, **opts)

    def __call__(self, value=None, *values, **opts):
        value = value or list(values)  # to allow initialization by varargs
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        return Type.__call__(self, value, **opts)

    def __add__(self, add):
        if isinstance(add, Sequence):
            return list(self) + list(add)
        else:
            raise ValueError('impossible to add not a sequence to an array (%s)' % (add))

    @staticmethod
    def _items_types(self, value, **opts):
        value = self._items[:len(value)] if self._itemsIsList else [self._items] * len(value)
        return [(i, v) for i, v in enumerate(value)]

    @staticmethod
    def _items_type(self, item):
        from ..protocols.type_proxy import TypeProxy
        t = self._items[item] if self._itemsIsList else self._items
        return t.proxy_type() if getattr(t, '_proxyUri', None) else t

    @staticmethod
    def _repr_schema(self):
        rs = Type._repr_schema(self)
        if self._items:
            if self._itemsIsList:
                rsi = [i._repr_schema(i) if isinstance(i, Type) else i for i in self._items]
            else:
                i = self._items
                rsi = self._items._repr_schema(i) if isinstance(i, Type) else i
            rs['items'] = rsi
        if self._minItems:
            rs['minItems'] = self._minItems
        if self._maxItems:
            rs['maxItems'] = self._maxItems
        if self._uniqueItems:
            rs['uniqueItems'] = self._uniqueItems
        if self._asString:
            rs['asString'] = self._asString
            rs['strDelimiter'] = self._strDelimiter
        return rs

    @staticmethod
    def _has_default(self, value=None, **opts):
        return True

    def default(self, value=None, **opts):
        value = value or self._default
        ret = [None] * len(value)
        for k, t in self._items_types(self, value):
            ret[k] = t.default(value[k], **opts) if t.has_default(value[k]) else None
        return self._serialize(self, ret, items=False, **opts)

    @staticmethod
    def _null(self, value, **opts):
        return self._collType([None for k in self.call_order(value, **opts)])

    @staticmethod
    def _check(self, value, split_string=True, **opts):
        if String.check(value):
            if not split_string:
                raise TypeError('%s is a string and is not allowed in this array. Use split_string.')
            value = Array._convert(self, value)
        if not isinstance(value, Sequence):
            raise TypeError('%s is not a sequence or array.')
        return Collection._check(self, value, **opts)

    @staticmethod
    def _validate(self, value, items=True, excludes=[], **opts):
        excludes = list(excludes) + ['minItems', 'maxItems', 'uniqueItems', 'items']
        # TODO add validate size, uniqueness as separate validation methods
        #value = self._deserializer._validate(self, value, excludes=excludes, **opts)
        value = Collection._validate(self, value, items=items, excludes=excludes, **opts)
        return value

    @staticmethod
    def _inputs(self, value, items=False, **opts):
        inputs = set()
        if String.check(value):
            value = Array._convert(self, value or [], convert=False)
        if items:
            for k, t in self._items_types(self, value):
                if self._is_included(k, value, **opts):
                    inputs.update(ChainMap(*[set([f'{k}.{i}' for i in t._inputs(t, value[k], **opts)])]))
            #return inputs.union(*[Array._inputs(self, value, i, items=False, **opts) for i, v in enumerate(value)])
        return inputs

    @classmethod
    def is_array_primitive(cls):
        if cls._itemsIsList:
            return all([it.is_primitive() for it in cls._items])
        else:
            return cls._items.is_primitive()


@register_type('tuple')
class Tuple(Array):
    _pyType = tuple
    #_collType = list


@register_type('set')
class Set(Array):
    _pyType = set
    #_collType = list


ArrayString = Array.extend_type('ArrayString', items=String)


@register_type('tokens')
class TokenizedString(Array):
    _rawLiterals = False
    _strDelimiter = '\n'
    _tokDelimiter = ' '
    _indentation = '\t'

    def __init__(self, strDelimiter='\n', tokDelimiter=' ', indentation= '\t', **opts):
        self._strDelimiter = opts.get('strDelimiter') or self._strDelimiter
        self._tokDelimiter = opts.get('tokDelimiter') or self._tokDelimiter
        self._indentation = opts.get('indentation') or self._indentation
        items = type(f'{self._id}/items', (ArrayString, ), dict(_strDelimiter=self._tokDelimiter))
        Array.__init__(self, items=items, **opts)

    def __call__(self, value=None, *values, **opts):
        opts['context'] = opts['context'] if 'context' in opts else self._create_context(self, **opts)
        lines = TokenizedString._convert(self, value, **opts)
        return Type.__call__(self, lines, convert=False, **opts)

    @staticmethod
    def _convert(self, value, split_string=False, **opts):
        from .strings import Pattern, Expr
        strDelimiter = opts.get('strDelimiter') or self._strDelimiter
        tokDelimiter = opts.get('tokDelimiter') or self._tokDelimiter
        indentation = opts.get('indentation') or self._indentation

        def convert_token(tok):
            if Expr.check(tok):
                return Expr.convert(tok, check=False, **opts)
            elif Pattern.check(tok):
                return Pattern.convert(tok, check=False, **opts)
            return tok

        def convert_collection(coll, *s, indent_level=1, split=False):
            lines = []
            if split:
                s = sum([ss.split(strDelimiter) for ss in s])
                s = sum([ss.split(tokDelimiter) for ss in s])
            if isinstance(coll, str):
                coll = convert_token(coll)
                line = list(s) + (coll.split(tokDelimiter) if split else [coll])
                lines.append(tuple(line))
            elif isinstance(coll, Sequence):
                if s:
                    lines.append(tuple(s))
                s2 = [indentation] * indent_level
                for c in coll:
                    lines.extend(convert_collection(c, *s2, indent_level=indent_level + 1, split=split))
            elif isinstance(coll, Mapping):
                if len(coll) == 1:
                    s1, d1 = list(coll.items())[0]
                    s1 = convert_token(s1)
                    s2 = s1.split(tokDelimiter) if split else [s1]
                    lines.extend(convert_collection(d1, *s, *s2, indent_level=indent_level, split=split))
                else:
                    if s:
                        lines.append(tuple(s))
                    for s1, d1 in coll.items():
                        s1 = convert_token(s1)
                        if split:
                            s2 = [indentation] * (indent_level - 1) + s1.split(tokDelimiter)
                        else:
                            s2 = [indentation] * (indent_level - 1) + [s1]
                        lines.extend(convert_collection(d1, *s2, indent_level=indent_level + 1, split=split))
            elif s:
                lines.append(tuple(s))
            return lines
        if isinstance(value, Sequence) and not isinstance(value, str):
            lines = [tuple([convert_token(tok) for tok in to_list(l)]) for l in value]
        else:
            lines = convert_collection(value, split=split_string)
        return CollectionSerializer._convert(self, lines, **opts)

    @staticmethod
    def _serialize(self, value, **opts):
        as_string = opts.pop('as_string', self._asString)
        strDelimiter = opts.get('strDelimiter') or self._strDelimiter
        tokDelimiter = opts.get('tokDelimiter') or self._tokDelimiter
        indentation = opts.get('indentation') or self._indentation

        if isinstance(value, str):
            # could convert value in case of string formating at this stage?
            value = [(value, )]
        lines = Array._serialize(self, value, as_string=False, **opts)
        for i, line in enumerate(lines):
            lines[i] = list(lines[i])
            for j, tok in enumerate(line):
                lines[i][j] = String._serialize(self._items, tok, **opts)
            lines[i] = tuple(lines[i])
        if as_string:
            lines = [tokDelimiter.join(line) for line in lines]
            return strDelimiter.join(lines)
        return lines

    def __str__(self):
        lines = Array._serialize(self, self, as_string=False)
        lines = [self._tokDelimiter.join(line) for line in lines]
        return self._strDelimiter.join(lines)

    @classmethod
    def is_primitive(cls):
        return True

    def default(self, value=None, **opts):
        ret = value or self._default
        if isinstance(ret, str):
            ret = [(l, ) for l in ret.split(self._strDelimiter) if l]
        return self._serialize(self, ret, items=False, **opts)

    @staticmethod
    def _inputs(self, value, **opts):
        from ngoschema.utils.jinja2 import get_jinja2_variables
        return set(get_jinja2_variables(str(value)))


@register_type('python_tokens')
class TokenizedPython(TokenizedString):
    _rawLiterals = False
    _strDelimiter = '\n'
    _tokDelimiter = ' '
    _indentation = '    '
