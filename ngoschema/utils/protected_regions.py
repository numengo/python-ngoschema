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

from ..decorators import SCH_PATH
from ..decorators import assert_arg
from .str_utils import multiple_replace

# https://regex101.com/r/aXmpPk/4
#pr_regex = re.compile(r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n][\s\\/<>#*@-]*(Insert)?( here)?( user)?[^\r\n]*[\r\n](?P<usercode>[\S\r\n\s]*?)[\r\n]*[\s\\/<>#*@-]*(End of user)?", re.DOTALL | re.MULTILINE | re.UNICODE)
pr_regex = re.compile(
    r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n](?P<user_code>[\S\r\n\s]*?)[\r\n]+[\s\\/<>#*@-]+PROTECTED REGION END",
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
        m.group('canonical'): m.group('user_code')
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


@assert_arg(0, SCH_PATH)
def set_protected_regions_in_file(fp, encoding='utf-8', **protected_regions):
    """
    Set protected regions in a given file
    """
    fp = str(fp.resolve())
    with codecs.open(fp, 'r', encoding) as f:
        content = f.read()

    def replace_region(match):
        m = match
        cn = m.group('canonical')
        s = m.string
        if cn in protected_regions.keys():
            return s[m.start():m.start('user_code')] + protected_regions[cn] + s[m.end('user_code'):m.end()]
        return s[m.start(): m.end()]

    new_content = pr_regex.sub(replace_region, content)

    with codecs.open(fp, 'w', encoding) as f:
        f.write(new_content)
