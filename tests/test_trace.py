# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path

import pytest

import ansys.scade.almgw_msoffice.trace as trace
from ansys.scade.pyalmgw.documents import ReqProject
from tests.conftest import diff_files

_root_dir = Path(__file__).parent.parent
_test_dir = _root_dir / 'tests'
_ref_dir = _test_dir / 'ref'
_res_dir = _test_dir / 'res'


@pytest.mark.parametrize(
    'name, deltas',
    [
        # nominal
        ('merge_links.xml', 'deltas.json'),
        # robustness
        ('no_trace.xml', 'unknown.json'),
    ],
)
def test_merge_links(local_tmpdir, name: str, deltas: str):
    project = ReqProject()
    map_requirements = {'REQ_1': None, 'REQ_2.1': None, 'REQ_2': None}
    doc = trace.TraceDocument(project, _res_dir / name, map_requirements)
    doc.read()
    tmp = local_tmpdir / name
    doc.file = str(tmp)
    links = _res_dir / deltas
    doc.merge_links(links)
    doc.write()
    #
    ref = _ref_dir / name

    failure = diff_files(ref, tmp)
    assert not failure


if __name__ == '__main__':
    # sometimes, debugging tests with PTVS fails:
    # following entry points are workarounds
    if False:
        test_merge_links(Path(__file__).parent / 'tmp')
