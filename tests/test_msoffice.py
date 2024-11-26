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
import shutil
import subprocess
import sys

import pytest

import ansys.scade.almgw_msoffice as ms
from ansys.scade.almgw_msoffice.msoffice import MSOffice
from tests.conftest import diff_files, load_project, std

_root_dir = Path(__file__).parent.parent
_test_dir = _root_dir / 'tests'
_ref_dir = _test_dir / 'ref'


@pytest.fixture(scope='session')
def nominal() -> std.Project:
    # unique model for these tests
    path = _root_dir / 'tests/Nominal/Nominal.etp'
    project = load_project(path)
    return project


def _run_msoffice(command: str, path: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the connector in a subprocess."""

    cmd = [
        sys.executable,
        '-m',
        'ansys.scade.almgw_msoffice.msoffice',
    ]
    _, exe = ms.exe()
    cmd = [exe]
    cmd.extend(['-' + command, str(path)])
    cmd.extend(args)
    # hardcoded pid, useless for this connector
    cmd.append('0')
    status = subprocess.run(cmd, capture_output=True)
    if status.stderr:
        print(status.stderr.decode('utf-8').strip('\n'))
        assert False
    out = status.stdout.decode('utf-8').strip('\n')
    print(out)
    return status


@pytest.mark.parametrize(
    'name, expected',
    [
        # 4294967295 is -1: return codes are expected to be unsigned
        ['Nominal', 0],
        ['NoFiles', 4294967295],
        ['MiscFiles', 0],
    ],
)
def test_import(local_tmpdir, name: str, expected: int):
    src_dir = _test_dir / name
    dst_dir = local_tmpdir / ('Import' + name)
    assert not dst_dir.exists()
    shutil.copytree(src_dir, dst_dir)
    path = dst_dir / (name + '.etp')
    dst = dst_dir / 'import.xml'
    status = _run_msoffice('import', path, str(dst))
    ref = _ref_dir / (name.lower() + '_import.xml')
    assert status.returncode == expected
    if expected == 0:
        assert not diff_files(ref, dst)


@pytest.mark.parametrize(
    'name, llrs',
    [
        ['Nominal', True],
        ['NoCache', False],
        ['WrongSchema', False],
        ['UnknownProject', False],
    ],
)
def test_export(local_tmpdir, name: str, llrs: bool):
    src_dir = _test_dir / name
    dst_dir = local_tmpdir / ('Export' + name)
    assert not dst_dir.exists()
    shutil.copytree(src_dir, dst_dir)
    path = dst_dir / (name + '.etp')

    deltas = src_dir / 'deltas.json'

    status = _run_msoffice('export', path, str(deltas))
    assert status.returncode == 1
    suffixes = ['.trace']
    if llrs:
        suffixes.extend(['.llrs', '.reqs'])
    for suffix in suffixes:
        dst = dst_dir / (name + '.msoffice' + suffix)
        ref = _ref_dir / (name.lower() + '_export' + suffix)
        assert not diff_files(ref, dst)


def test_settings():
    path = _test_dir / 'Nominal' / 'Nominal.etp'
    status = _run_msoffice('settings', path)
    assert status.returncode == 0


class TestMSOffice(MSOffice):
    __test__ = False

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.file = None
        self.req = None
        self.called = False

    def open_document(self, file: Path, req: str):
        # store thr parameters for verification
        self.file = file
        self.req = req
        self.called = True
        return 0


@pytest.mark.parametrize(
    'req, called, expected',
    [
        ['REQ_011', True, 0],
        ['REQ_007', False, -1],
    ],
)
def test_locate(nominal, req: str, called: bool, expected: bool):
    cls = TestMSOffice()
    cls.project = nominal
    status = cls.on_locate(req, 0)
    assert status == expected
    assert cls.called == called
    if called:
        assert cls.req == req
        assert cls.file == _test_dir / 'Nominal' / 'Nominal.docx'


@pytest.mark.parametrize(
    'name, called, expected',
    [
        ['NoFiles', False, -1],
        ['Nominal', True, 0],
    ],
)
def test_manage(name, called: bool, expected: int):
    path = _test_dir / name / (name + '.etp')
    cls = TestMSOffice()
    cls.project = load_project(path)
    status = cls.on_manage(0)
    assert status == expected
    assert cls.called == called
    if called:
        assert cls.req == ''
        assert cls.file == _test_dir / name / (name + '.docx')


if __name__ == '__main__':
    tmp = Path(__file__).parent / 'tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(exist_ok=True)
    test_import(tmp, 'Nominal', 0)
