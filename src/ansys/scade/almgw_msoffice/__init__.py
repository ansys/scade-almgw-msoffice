# -*- coding: utf-8 -*-

# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Ansys SCADE ALM Gateway connector for MS-Office."""

from pathlib import Path

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

try:
    __version__ = importlib_metadata.version(__name__.replace('.', '-'))
except importlib_metadata.PackageNotFoundError:
    # happens with pre-commit, the package is not installed in the virtual environment
    __version__ = '<unknown>'


_MS_OFFICE = 'ALMGW Connector for MS-Office'

# settings
TOOL = 'MSOFFICE'
REQSTYLE = 'REQSTYLE'
REQSTYLE_DEFAULT = 'Requirement_ID'
TEXTSTYLE = 'TEXTSTYLE'
TEXTSTYLE_DEFAULT = 'Requirement_Text'
DOCUMENTS = 'DOCUMENTS'
DOCUMENTS_DEFAULT = []


def srg() -> str:
    """
    Return the path of the SCADE Studio registry file.

    This function implements the entry point "ansys.scade.registry/srg"
    introduced in SCADE 2025 R1. It avoids creating an explicit srg file
    in ``%APPDATA%/Scade/Customize`` when the package is installed.
    """
    # the package's srg file is located in the same directory
    return str(Path(__file__).parent / 'almgw_msoffice.srg')


def exe() -> tuple[str, str]:
    """
    Return the path of the connector's executable.

    This function implements the entry point "ansys.almgw.connector/exe"
    introduced in SCADE 2025 R1. It avoids creating an explicit properties file
    in ``$(SCADE)/SCADE LifeCycle/ALM Gateway/external`` when the package is installed.
    """
    # the connector is either in Lib/site-packages/ansys/scade/almgw_msoffice
    #                      or in site-packages/ansys/scade/almgw_msoffice (pip install --user)
    #                      or in src/ansys/scade/almgw_msoffice (pip install --editable)
    site_packages = Path(__file__).parent.parent.parent.parent
    if site_packages.name == 'src':
        # install in user mode, consider the default namings
        python_dir = site_packages.parent / '.venv'
    else:
        python_dir = site_packages.parent
        if python_dir.name.lower() == 'lib':
            python_dir = python_dir.parent
    # the exe is in Scripts
    return _MS_OFFICE, str(python_dir / 'Scripts' / 'ansys_scade_almgw_msoffice.exe')
