# -*- coding: utf-8 -*-
"""
retrieve protected regions from a string

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import re

from ngoschema.decorators import SCH_PATH
from ngoschema.decorators import assert_arg

# https://regex101.com/r/aXmpPk/4
#pr_regex = re.compile(r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n][\s\\/<>#*@-]*(Insert)?( here)?( user)?[^\r\n]*[\r\n](?P<usercode>[\S\r\n\s]*?)[\r\n]*[\s\\/<>#*@-]*(End of user)?", re.DOTALL | re.MULTILINE | re.UNICODE)
pr_regex = re.compile(
    r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n](?P<usercode>[\S\r\n\s]*?)[\r\n]+[\s\\/<>#*@-]+PROTECTED REGION END",
    re.DOTALL | re.MULTILINE | re.UNICODE)


def get_protected_regions(sourcecode):
    """
    Return a dictionary of the protected areas of a text

    { region_id : region_source_code}

    :param sourcecode : string containing source code
    :type sourcecode : str
    :rtype: dict
    """
    return {
        m.group('canonical'): m.group('usercode')
        for m in pr_regex.finditer(sourcecode)
    }


@assert_arg(0, SCH_PATH)
def get_protected_regions_from_file(fp, encoding='utf-8'):
    """
    Return a dictionary of the protected areas of a text

    { region_id : region_source_code}

    :param fp: file path
    :type fp : path, isPathExisting=True
    :rtype: dict
    """
    if not fp.exists():
        return {}
    with codecs.open(str(fp.resolve()), 'r', encoding) as f:
        return get_protected_regions(f.read())


