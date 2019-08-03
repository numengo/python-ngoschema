import json


class InvalidTypeError(ValueError):

    def __init__(self, msg):
        super(InvalidTypeError, self).__init__(msg)


def convert(schema, options=None):
    notSupported = [
        'nullable', 'discriminator', #'readOnly',
        'writeOnly', 'xml', 'externalDocs',
        'example', 'deprecated',
    ]

    options = options or {}
    options['dateToDateTime'] = options.get('dateToDateTime', False)
    options['cloneSchema'] = options.get('cloneSchema', True)
    options['supportPatternProperties'] = options.get(
        'supportPatternProperties', False
    )
    options['keepNotSupported'] = options.get('keepNotSupported', [])

    if not callable(options.get('patternPropertiesHandler')):
        options['patternPropertiesHandler'] = patternPropertiesHandler

    options['_removeProps'] = []

    if options.get('removeReadOnly'):
        options['_removeProps'].append('readOnly')
    if options.get('removeWriteOnly'):
        options['_removeProps'].append('writeOnly')

    options['_structs'] = [
        'allOf', 'anyOf', 'oneOf', 'not', 'items', 'additionalProperties',
    ]

    options['_notSupported'] = resolveNotSupported(
        notSupported, options['keepNotSupported'],
    )

    if options['cloneSchema']:
        schema = json.loads(json.dumps(schema, skipkeys=True))

    schema = convertSchema(schema, options)
    schema['$schema'] = 'http://json-schema.org/draft-07/schema#'

    return schema


def convertSchema(schema, options):
    structs = options['_structs']
    notSupported = options['_notSupported']

    for i, struct in enumerate(structs):
        if isinstance(schema.get(struct), list):
            for j in range(len(schema[struct])):
                schema[struct][j] = convertSchema(schema[struct][j], options)
        elif isinstance(schema.get(struct), dict):
            schema[struct] = convertSchema(schema[struct], options)

    if isinstance(schema.get('definitions'), dict):
        schema['definitions'] = convertProperties(schema['definitions'], options)

    if isinstance(schema.get('properties'), dict):
        schema['properties'] = convertProperties(schema['properties'], options)

        readOnly = []

        for k, v in schema['properties'].items():
            if v.pop('readOnly', False):
                readOnly.append(k)

        if readOnly:
            schema['readOnly'] = readOnly

        if isinstance(schema.get('required'), list):
            schema['required'] = cleanRequired(schema['required'],
                                               schema['properties'])

            if len(schema['required']) == 0:
                del schema['required']

        if len(schema['properties']) == 0:
            del schema['properties']

    schema = convertTypes(schema, options)
    validateType(schema.get('type'))
    schema['additionalProperties'] = bool(schema.get('patternProperties', False) or schema.get('additionalProperties', False))

    if (isinstance(schema.get('x-patternProperties'), dict)
            and options['supportPatternProperties']):
        schema = convertPatternProperties(schema,
                                          options['patternPropertiesHandler'])

    for unsupported in notSupported:
        try:
            del schema[unsupported]
        except KeyError:
            pass

    return schema


def convertProperties(properties, options):
    props = {}

    for key in properties:
        removeProp = False
        # note: don't shadow the `property` built-in
        pproperty = properties[key]

        for prop in options['_removeProps']:
            if pproperty.get(prop) is True:
                removeProp = True

        if removeProp:
            continue

        props[key] = convertSchema(pproperty, options)

    return props


def validateType(ttype):
    from ngoschema.pjo_validators import validators
    validTypes = list(validators.type_registry.registry)

    if ttype is not None and ttype not in validTypes:
        raise InvalidTypeError('Type "%s" is not a valid type' % ttype)


def convertTypes(schema, options):
    toDateTime = options['dateToDateTime']

    if schema.get('type') is None:
        return schema

    if (schema.get('type') == 'string' and schema.get('format') == 'date'
            and toDateTime):
        schema['format'] = 'date-time'

    if schema['type'] == 'file':
        schema['type'] = 'path'

    if not schema.get('format'):
        try:
            del schema['format']
        except KeyError:
            pass

    if schema.get('nullable') is True:
        schema['type'] = [schema['type'], 'null']

    return schema


def convertPatternProperties(schema, handler):
    schema['patternProperties'] = schema['x-patternProperties']
    del schema['x-patternProperties']
    return handler(schema)


def patternPropertiesHandler(schema):
    patternsObj = schema['patternProperties']
    additProps = schema.get('additionalProperties')

    if not isinstance(additProps, dict):
        return schema

    for pattern, value in patternsObj.items():
        if value == additProps:
            schema['additionalProperties'] = False
            break

    return schema


def resolveNotSupported(notSupported, toRetain):
    return [x for x in notSupported if x not in toRetain]


def cleanRequired(required, properties):
    required = required or []
    properties = properties or {}
    return [x for x in required if properties.get(x) is not None]
