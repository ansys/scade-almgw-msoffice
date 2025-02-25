# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Persistence for Ansys SCADE ALM Gateway connector for MS-Office."""

from pathlib import Path

# Dict used in typing annotation compatible with Python  3.7
from typing import Dict  # noqa: F401

from lxml import etree

from ansys.scade.pyalmgw.documents import (
    ReqProject,
    # Requirement used in typing annotation compatible with Python  3.7
    Requirement,  # noqa: F401
    TraceabilityLink,
)
from ansys.scade.pyalmgw.utils import read_json


class TraceDocument:
    """
    Tracability links file.

    * Updated on export
    * Read on import

    .. Note::

       The cache document is also updated.
    """

    def __init__(self, project: ReqProject, path: Path, requirements=None):
        """Initialize the trace document."""
        self.project = project
        self.file = str(path)
        self.links = {}  # type: Dict[str, TraceabilityLink]
        self.map_requirements = requirements if requirements else {}  # type: Dict[str, Requirement]

    def read(self):
        """Read the trace file."""
        self.links = {}
        try:
            tree = etree.parse(self.file, parser=None)
        except OSError:
            return

        root = tree.getroot()
        for link in root:
            self.add(link.get('source'), link.get('target'), link.get('description', ''))

    def write(self):
        """Write the trace file."""
        root = etree.Element('Links', attrib=None, nsmap=None)
        for link in self.links.values():
            attrib = {'source': link.source, 'target': link.target}
            etree.SubElement(root, 'Link', attrib=attrib, nsmap=None)
        tree = etree.ElementTree(element=root)
        tree.write(self.file, pretty_print=True)

    def merge_links(self, file: Path):
        """Merge the traceability updates."""
        deltas = read_json(file)
        if deltas is None:
            return
        for delta in deltas:
            oid = delta['source']['oid']
            path = delta['source'].get('path_name', '')
            req = delta['target']['req_id']
            action = delta['action']
            # action is either 'ADD' or 'REMOVE'
            if action == 'ADD':
                self.add(oid, req, path)
            else:
                assert action == 'REMOVE'
                self.remove(oid, req)

    def add(self, oid: str, req: str, path: str):
        """Create a traceability link."""
        if not self.map_requirements or req in self.map_requirements:
            link = TraceabilityLink(self.project, None, oid, req)
            self.links[req + oid] = link

        else:
            print('not adding link {0} to {1} ({2})'.format(oid, req, path))

    def remove(self, oid: str, req: str):
        """Remove a tracrability link."""
        link = self.links.get(req + oid)
        if link is None:
            print('not removing link {0} to {1}'.format(oid, req))
            return -1

        del self.links[req + oid]
        self.project.traceability_links.remove(link)
        return 0
