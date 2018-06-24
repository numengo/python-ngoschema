# -*- coding: utf-8 -*-
""" 
retrieve protected regions from a string

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  
"""
from __future__ import print_function
from __future__ import unicode_literals

from ngoschema.decorators import assert_arg
from ngoschema.decorators import SCH_PATH
from ngofile.pathlist import PathList

import re

# https://regex101.com/r/aXmpPk/4
#pr_regex = re.compile(r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n][\s\\/<>#*@-]*(Insert)?( here)?( user)?[^\r\n]*[\r\n](?P<usercode>[\S\r\n\s]*?)[\r\n]*[\s\\/<>#*@-]*(End of user)?", re.DOTALL | re.MULTILINE | re.UNICODE)
pr_regex = re.compile(
    r"PROTECTED REGION ID\((?P<canonical>[\w\.\=]+)\) ENABLED START[^\r\n]*[\r\n](?P<usercode>[\S\r\n\s]*?)[\r\n]*[\s\\/<>#*@-]+PROTECTED REGION END",
    re.DOTALL | re.MULTILINE | re.UNICODE)


def get_protected_regions(sourcecode):
    """
    Return a dictionnary of the protected areas of a text

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
def get_protected_regions_from_file(fp):
    """
    Return a dictionnary of the protected areas of a text

    { region_id : region_source_code}

    :param fp: file path
    :type fp : path, isPathExisting=True
    :rtype: dict
    """
    if not fp.exists():
        return {}
    with fp.open('r') as f:
        return get_protected_regions(f.read())


def load_project_protected_regions(project):
    src_dir = project.repoDir.joinpath('src', str(project.packageName))
    incl_dir = project.repoDir.joinpath('include', str(project.packageName))
    simx_dir = project.repoDir.joinpath('modelica', str(project.alias))
    ame_dir = project.repoDir.joinpath('amesim', str(project.alias),
                                       'submodels')
    mlab_dir = project.repoDir.joinpath('simulink', str(project.alias),
                                        'submodels')
    user_code = {}
    for f in PathList([src_dir, incl_dir]).list_files(
        ['*.c', '*.cpp', '*.h', '*.mo'], recursive=True):
        user_code.update(get_protected_regions_from_file(f))
    return user_code
