#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    SphinxQuickStartPlus - sphinx-quickstart Utility

    sphinx:
        http://www.sphinx-doc.org/en/stable/

    extend sphix-quickstart.

    - Remember latest sphinx-quickstart settings.
    - More extensions
      - commonmark and recommonmark
      - Read the Docs theme
      - sphinx_fontawesome
      - sphinxcontrib-blockdiag
      - nbsphinx
      - sphinx-autobuild

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :author: pashango2.
    :license: Free.
"""
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
import copy
import json
from sphinx.quickstart import do_prompt, boolean, is_path, package_dir, term_decode
from sphinx.util.console import purple, bold, red, turquoise, \
    nocolor, color_terminal
from sphinx import quickstart
import sphinx

LATEST_SETTING_JSON_NAME = "setting.json"

""" Font Awesome Extension
 Font Awesome: http://fontawesome.io/
 sphinx_fontawesome: https://github.com/fraoustin/sphinx_fontawesome
"""
sphinx_fontawesome_extension = {
    "conf_py": """
import sphinx_fontawesome
extensions.append('sphinx_fontawesome')
""",
    "package": ["sphinx_fontawesome"]
}

sphinx_commonmark_extension = {
    "conf_py": """
source_suffix = [source_suffix, '.md']

from recommonmark.parser import CommonMarkParser
source_parsers = {
    '.md': CommonMarkParser,
}
""",
    "package": ["commonmark", "recommonmark"]
}

sphinx_commonmark_autostructify_extension = {
    "conf_py": """
from recommonmark.transform import AutoStructify

github_doc_root = 'https://github.com/rtfd/recommonmark/tree/master/doc/'
def setup(app):
    app.add_config_value('recommonmark_config', {
            'url_resolver': lambda url: github_doc_root + url,
            'auto_toc_tree_section': 'Contents',
            }, True)
    app.add_transform(AutoStructify)
""",
    "package": ["recommonmark"],
}

sphinx_sphinx_rtd_theme_extension = {
    "conf_py": """
import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
""",
    "package": ["sphinx_rtd_theme"],
}

sphinx_autobuild_extension = {
    "makefile": """
livehtml:
\tsphinx-autobuild -b html -r .*\.md.+ $(ALLSPHINXOPTS) $(BUILDDIR)/html
""",
    "package": ["sphinx-autobuild"],
}

nbsphinx_extension = {
    "conf_py": """
extensions.append('nbsphinx')
exclude_patterns.append('**.ipynb_checkpoints')
""",
    "package": ["nbsphinx"],
}

sphinx_blockdiag_extension = {
    "conf_py": """
extensions.extend([
    'sphinxcontrib.blockdiag',
    'sphinxcontrib.seqdiag',
    'sphinxcontrib.actdiag',
    'sphinxcontrib.nwdiag',
    'sphinxcontrib.rackdiag',
    'sphinxcontrib.packetdiag',
])
blockdiag_html_image_format = 'SVG'
seqdiag_html_image_format = 'SVG'
actdiag_html_image_format = 'SVG'
nwdiag_html_image_format = 'SVG'
rackiag_html_image_format = 'SVG'
packetdiag_html_image_format = 'SVG'
""",
    "package": ["sphinxcontrib-actdiag", "sphinxcontrib-blockdiag", "sphinxcontrib-nwdiag", "sphinxcontrib-seqdiag"],
}

qsp_extensions = [
    sphinx_fontawesome_extension,
    sphinx_commonmark_extension,
    sphinx_commonmark_autostructify_extension,
    sphinx_sphinx_rtd_theme_extension,
    sphinx_autobuild_extension,
    nbsphinx_extension,
    sphinx_blockdiag_extension,
]

EXCLUDE_VALUE = ['project', 'author', 'path', 'version', 'release', 'extensions']


INTELLIJ_IDEA_IGNORE_RE = "___jb_(.*?)___$"


AUTO_BUILD_BATCH = """
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx auto build

set SOURCEDIR={source_dir}
set BUILDDIR={build_dir}

sphinx-autobuild -b html -r {INTELLIJ_IDEA_IGNORE_RE} %SOURCEDIR% %BUILDDIR%/html
goto end

:end
popd
""".strip()


# for python2... can't use nonlocal
hook_d = {}


def qsp_ask_user():
    global hook_d

    if hook_d:
        print(bold('Welcome to the Sphinx %s quickstart-plus utility.') % quickstart.__display_version__)
        print('''
Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets).''')

        d = {}
        do_prompt(d, 'use_latest', 'Use latest setting? (y/n)', 'y', boolean)
        return d['use_latest']

    return False



def main(argv):
    global hook_d

    # load latest setting.
    home_dir = os.path.join(os.path.expanduser('~'), ".sphinx_qsp")
    if not os.path.isdir(home_dir):
        os.mkdir(home_dir)

    json_path = os.path.join(home_dir, LATEST_SETTING_JSON_NAME)
    if os.path.isfile(json_path):
        hook_d.update(json.load(open(json_path)))

        # oh..
        hook_d = {str(key): value for key, value in hook_d.items()}

    # monkey patch : sphinx.quickstart.ask_user
    original_ask_user = quickstart.ask_user

    def monkey_patch_ask_user(d):
        # for python2... can't use nonlocal
        global hook_d

        if qsp_ask_user():
            d.update(hook_d)

        original_ask_user(d)

    quickstart.ask_user = monkey_patch_ask_user

    # monkey patch : sphinx.quickstart.generate
    original_generate = quickstart.generate

    def monkey_patch_generate(d, templatedir=None):
        # for python2... don't use nonlocal
        global hook_d
        hook_d = copy.copy(d)

        original_generate(d, templatedir)
    quickstart.generate = monkey_patch_generate

    # do sphinx.quickstart
    quickstart.main(argv)

    # save latest stiing.
    save_d = {key: value for key, value in hook_d.items() if key not in EXCLUDE_VALUE}
    json.dump(save_d, open(json_path, "w"), indent=4)

    # write ext-extensions
    d = hook_d

    srcdir = d['sep'] and os.path.join(d['path'], 'source') or d['path']
    conf_path = os.path.join(srcdir, "conf.py")
    with open(conf_path, "a+") as fc:
        for ext in qsp_extensions:
            if "conf_py" in ext:
                fc.write(ext["conf_py"])

    if d['makefile'] is True:
        make_path = os.path.join(d['path'], 'Makefile')
        with open(make_path, "a+") as fm:
            for ext in qsp_extensions:
                if "makefile" in ext:
                    fm.write(ext["makefile"])

    if d['batchfile'] is True:
        batchfile_path = os.path.join(d['path'], 'auto_build.bat')
        source_dir = d['sep'] and 'source' or '.'
        build_dir = d['sep'] and 'build' or d['dot'] + 'build'

        open(batchfile_path, "w").write(
            AUTO_BUILD_BATCH.format(
                build_dir=build_dir, source_dir=source_dir,
                INTELLIJ_IDEA_IGNORE_RE=INTELLIJ_IDEA_IGNORE_RE,
            )
        )


    # json_path = os.path.join(home_dir, JSON_NAME)
    # if os.path.isfile(json_path):
    #     d = json.load(open(json_path))
    # else:
    #     d = {}
    #
    # ask_user(d)
    #
    # save_d = d.copy()
    # for key in EXCLUDE_VALUE.keys():
    #     try:
    #         del save_d[key]
    #     except KeyError:
    #         pass
    #
    # json.dump(save_d, open(json_path, "w"), indent=4)
    #
    # quickstart.generate(d, templatedir="test_output")
    #
    # conf_path = os.path.join(d["path"], "conf.py")
    # make_path = os.path.join(d["path"], "Makefile")
    #
    # with open(conf_path, "a+") as fc, open(make_path, "a+") as fm:
    #     for ext in qsp_extensions:
    #         if "conf_py" in ext:
    #             fc.write(ext["conf_py"])
    #         if "makefile" in ext:
    #             fm.write(ext["makefile"])
