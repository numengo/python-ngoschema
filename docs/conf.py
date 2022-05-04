# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, os.path
import sys
sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

locale_dirs = ['locale/', 'ngoschema/config/locale/']
gettext_compact = False     # optional.

source_suffix = '.rst'
master_doc = 'index'
project = 'NgoSchema'
year = '2018'
author = 'Cédric ROMAN'
copyright = '{0}, {1}'.format(year, author)
version = release = '1.0.10'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/numengo/python-ngoschema/issues/%s', '#'),
    'pr': ('https://github.com/numengo/python-ngoschema/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

############################
# SETUP THE RTD LOWER-LEFT #
############################
try:
   html_context
except NameError:
   html_context = dict()
html_context['display_lower_left'] = True

# SET CURRENT_LANGUAGE
if 'current_language' in os.environ:
   # get the current_language env var set by buildDocs.sh
   current_language = os.environ['current_language']
else:
   # the user is probably doing `make html`
   # set this build's current language to english
   current_language = 'en'

# tell the theme which language to we're currently building
html_context['current_language'] = current_language
if os.path.exists('../locale'):
    # POPULATE LINKS TO OTHER LANGUAGES
    html_context['languages'] = [(current_language, '/' + current_language + '/')]
    languages = [lang.name for lang in os.scandir('../locale') if lang.is_dir()]
    for lang in languages:
       html_context['languages'].append((lang, '/' + lang + '/'))
