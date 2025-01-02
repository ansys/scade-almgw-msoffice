# Copyright (C) 2020 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Command line utility to setup a project for the connector.

.. code:: text

    usage: setup_ansys_scade_almgw_msoffice [-h] -p <project> [-r <req>]
                                            [-t <text>] [-s <schema>]
                                            [-d [<documents> ...]]

    options:
      -h, --help            show this help message and exit
      -p <project>, --project <project>
                            Ansys SCADE project (ETP)
      -r <req>, --req_style <req>
                            requirement identifier style
      -t <text>, --text_style <text>
                            requirement text style
      -s <schema>, --schema <schema>
                            json export schema
      -d [<documents> ...], --documents [<documents> ...]
                            documents
"""

from argparse import ArgumentParser, Namespace

# shall modify sys.path to access SCACE APIs
from ansys.scade.apitools import declare_project

# isort: split

from scade.model.project.stdproject import Project, get_roots as get_projects

import ansys.scade.almgw_msoffice as ms
import ansys.scade.pyalmgw as pyamlgw


def setup(project: Project, options: Namespace) -> int:
    """Update the project with the settings."""
    project.set_tool_prop_def(ms.TOOL, ms.DOCUMENTS, options.documents, ms.DOCUMENTS_DEFAULT, None)

    if options.req_style:
        project.set_scalar_tool_prop_def(
            ms.TOOL, ms.REQSTYLE, options.req_style, ms.REQSTYLE_DEFAULT, None
        )

    if options.text_style:
        project.set_scalar_tool_prop_def(
            ms.TOOL, ms.TEXTSTYLE, options.text_style, ms.TEXTSTYLE_DEFAULT, None
        )

    if options.schema:
        project.set_scalar_tool_prop_def(
            pyamlgw.TOOL, pyamlgw.LLRSCHEMA, options.schema, pyamlgw.LLRSCHEMA_DEFAULT, None
        )
    project.save(project.pathname)
    return 0


def main() -> int:
    """Implement the ``ansys.scade.almgw_msoffice.setup:main`` packages's project script."""
    parser = ArgumentParser()
    parser.add_argument(
        '-p', '--project', metavar='<project>', help='Ansys SCADE project (ETP)', required=True
    )
    parser.add_argument(
        '-r', '--req_style', metavar='<req>', help='requirement identifier style', default=''
    )
    parser.add_argument(
        '-t', '--text_style', metavar='<text>', help='requirement text style', default=''
    )
    parser.add_argument('-s', '--schema', metavar='<schema>', help='json export schema', default='')
    parser.add_argument(
        '-d', '--documents', metavar='<documents>', help='documents', nargs='*', default=[]
    )

    options = parser.parse_args()

    assert declare_project
    declare_project(options.project)
    # must be one and only one project
    project = get_projects()[0]

    return setup(project, options)


if __name__ == '__main__':
    main()
