# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
import shutil
import subprocess

import pytest

import ansys.scade.almgw_msoffice as ms
from tests.conftest import diff_files

_root_dir = Path(__file__).parent.parent
_test_dir = _root_dir / 'tests'
_ref_dir = _test_dir / 'ref'
_res_dir = _test_dir / 'res'


def _run_setup(*args) -> subprocess.CompletedProcess:
    """Run the connector in a subprocess."""

    # get the location of 'Scripts'
    _, exe = ms.exe()
    cmd = [str(Path(exe).with_name('setup_ansys_scade_almgw_msoffice.exe'))]
    cmd.extend(args)
    print(cmd)
    status = subprocess.run(cmd, capture_output=True)
    if status.stderr:
        print(status.stderr.decode('utf-8').strip('\n'))
        assert False
    out = status.stdout.decode('utf-8').strip('\n')
    print(out)
    return status


@pytest.mark.parametrize(
    'name, args',
    [
        ['all', '-r req -t text -s c:/schema.json -d a B/c.docx'],
        ['none', ''],
    ],
)
def test_setup(local_tmpdir, name, args):
    path = _res_dir / 'setup.etp'
    dst = local_tmpdir / ('%s_%s%s' % (path.stem, name, path.suffix))
    shutil.copy(path, dst)

    params = ['-p', str(dst)] + args.split()
    status = _run_setup(*params)
    assert status.returncode == 0

    ref = _ref_dir / dst.name
    assert not diff_files(ref, dst)
