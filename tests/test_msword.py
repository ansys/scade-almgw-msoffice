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

import difflib
from pathlib import Path

import ansys.scade.almgw_msoffice.msword as msword

_msoffice_dir = Path(msword.__file__).parent
_test_dir = Path(__file__).parent.parent / 'tests'
_ref_dir = _test_dir / 'ref'


def cmp_file(fromfile: Path, tofile: Path, n=3, linejunk=None):
    """Return the differences between two files."""
    with fromfile.open() as fromf, tofile.open() as tof:
        if linejunk:
            fromlines = [line for line in fromf if not linejunk(line)]
            tolines = [line for line in tof if not linejunk(line)]
        else:
            fromlines, tolines = list(fromf), list(tof)

    diff = difflib.context_diff(fromlines, tolines, str(fromfile), str(tofile), n=n)
    return diff


def test_parser(local_tmpdir):
    """
    Build manually the test file links.xml and make sure it is identical.
    """
    ref = Path(__file__).parent / 'ref' / 'hierarchy.xml'
    dst = local_tmpdir / 'hierarchy.xml'
    project = msword.ReqProject(dst)
    path = Path(__file__).parent / 'Hierarchy' / 'Hierarchy.docx'
    reqs = msword.add_document(project, path, 'Requirement_ID', 'Requirement_Text')
    assert len(reqs) > 1
    print(str(reqs))
    project.write()

    print('compare', str(ref), str(dst))
    diffs = cmp_file(ref, dst)
    failure = False
    for d in diffs:
        print(d.rstrip('\r\n'))
        failure = True
    assert not failure


if __name__ == '__main__':
    tmp = Path(__file__).parent / 'tmp'
    tmp.mkdir(exist_ok=True)
    test_parser(tmp)
