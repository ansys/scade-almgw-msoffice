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

"""Ansys SCADE ALM Gateway connector for MS-Office."""

from pathlib import Path
import shutil
import subprocess
from typing import List

import ansys.scade.almgw_msoffice.msexcel as msexcel
import ansys.scade.almgw_msoffice.msword as msword
from ansys.scade.almgw_msoffice.trace import TraceDocument
from ansys.scade.pyalmgw.connector import Connector
from ansys.scade.pyalmgw.documents import ReqDocument, ReqProject
import ansys.scade.pyalmgw.utils as utils

# ---------------------------------------------
# connector implementation
# ---------------------------------------------


class MSOffice(Connector):
    """Specialization of the connector for MS Office."""

    def __init__(self):
        """Initialize the MS Office connector."""
        super().__init__('msoffice')
        # all requirements
        self.map_requirements = {}

    def get_reqs_file(self) -> Path:
        """Return the path of the temporary file containing the requirements and traceability."""
        assert self.project
        return Path(self.project.pathname).with_suffix('.' + self.id + '.reqs')

    def get_trace_file(self) -> Path:
        """Return the path of the file containing the traceability."""
        assert self.project
        return Path(self.project.pathname).with_suffix('.' + self.id + '.trace')

    def on_settings(self, pid: int) -> int:
        """
        Stub the command ``settings``.

        Nothing to do, the settings are managed by a dedicated plug-in.

        Parameters
        ----------
        pid : int
            SCADE product process ID.

        Returns
        -------
        int

            * -1: if an error occurs, therefore previous settings information shall be kept
            * 0: set settings information shall be OK
            * 1: ALM Gateway project shall be removed, i.e., ALM connection shall be reset
        """
        print('settings: command not supported.')
        return 0

    def on_import(self, file: Path, pid: int) -> int:
        """
        Import requirements and traceability links to ALM Gateway.

        The function reads the requirements from the documents and
        adds the traceability data stored in a separate file.

        Parameters
        ----------
        path : Path
            Absolute path where the XML requirements file is saved.
        pid : int
            SCADE product process ID.

        Returns
        -------
        int

            * -1: if an error occurs, therefore previous export status
              and requirement tree shall be kept
            * 0: requirements and traceability links shall be correctly imported
        """
        files = self.get_documents()
        if not files:
            print('import: No documents')
            return -1

        self.map_requirements = {}
        project = ReqProject(file)
        self.read_requirements(project)

        links = TraceDocument(project, self.get_trace_file(), self.map_requirements)
        links.read()

        project.write()

        # cache the requirements, for debug purpose
        cache = self.get_reqs_file()
        shutil.copyfile(file, cache)

        # req_file is updated
        print('requirements imported.')
        return 0

    def on_export(self, links: Path, pid: int) -> int:
        """
        Update the traceability data and produce a traceability matrix.

        This function updates the tracability data in a separate file.

        It produces the traceability matrices when an export configuration
        file is specified in the project.

        Parameters
        ----------
        links : Path
            Path of a JSON file that contains the links to add and remove.
        pid : int
            SCADE product process ID.

        Returns
        -------
        int

            * -1: if an error occurs, therefore previous export status
              and requirement tree shall be kept
            * 0: requirements and traceability links shall not be exported
            * 1: requirements and traceability links shall be exported
            * 2: previous export status and requirement tree shall be kept
        """
        # update the cache, if exists
        cache = self.get_reqs_file()
        if not cache.exists():
            cache = None
            project = ReqProject()
        else:
            project = ReqProject(cache)
            project.read()
            # reset the tracebaility
            project.traceability_links = []
        # cache the links into a separate trace file since there's no way
        # to store traceability links within MS Word
        trace = TraceDocument(project, self.get_trace_file())
        trace.read()
        trace.merge_links(links)
        trace.write()

        if not cache:
            # nothing to export
            print('matrices not produced: re-import the requirements first')
            return 1

        # save the updated cache
        project.write()
        model = self.export_llrs()
        if not model:
            # error but return 1 since the traceability has been updated
            print('llr generation failure')
            return 1

        # generation of matrix with the cached imported data
        llrs = utils.read_json(model)
        assert llrs
        msexcel.generate_matrix(project, llrs)
        print('requirements exported.')
        return 1

    def on_manage(self, pid: int) -> int:
        """
        Run Microsoft Word with the first referenced document.

        Parameters
        ----------
        pid : int
            SCADE product process ID.

        Returns
        -------
        int

            * -1: if an error occurs launching the command
            * 0: if ‘Management Requirements’ UI of ALM tool is successfully launched
            * 1: to clean requirement list on the SCADE IDE ‘Requirements’ window
        """
        documents = self.get_documents()
        if not documents:
            print('manage: No documents')
            return -1
        print('%s: document opened.' % documents[0])
        return self.open_document(documents[0], '')

    def on_locate(self, req: str, pid: int) -> int:
        """
        Run Microsoft Word with the document containing the requirement and locate it.

        Parameters
        ----------
        req : str
            Identifier of a requirement defined in a document.
        pid : int
            SCADE product process ID.

        Returns
        -------
        int

            * -1: if an error occurs executing the command
            * 0: if the command is successfully executed
        """
        project = ReqProject()
        self.read_requirements(project)
        requirement = self.map_requirements.get(req)
        if requirement is None:
            print('locate: %s requirement not found' % req)
            return -1

        owner = requirement.owner
        while not isinstance(owner, ReqDocument):
            owner = owner.owner

        print('%s (%s): locate performed.' % (req, owner.path))
        return self.open_document(owner.path, req)

    def open_document(self, file: Path, req: str):
        """Open the document, and locate the requirement when not empty."""
        assert self.project
        if file.suffix.lower() == '.docx':
            script = (Path(__file__).parent / 'res' / 'word-select.ps1').as_posix()
            cmd = ['powershell', '-file', script, '-file', str(file)]
            if req:
                req_style = self.project.get_scalar_tool_prop_def(
                    'MSOFFICE', 'REQSTYLE', 'Requirement_ID', None
                )
                cmd.extend(['-string', req, '-style', req_style])
            try:
                subprocess.check_output(cmd)
                return 0
            except subprocess.CalledProcessError:
                return -1
        return -1

    def get_documents(self) -> List[Path]:
        """Return the documents specified in the project."""
        assert self.project

        files = self.project.get_tool_prop_def('MSOFFICE', 'DOCUMENTS', [], None)
        # resolve the relative names to the project's directory
        directory = Path(self.project.pathname).resolve().parent
        paths = []
        for file in files:
            path = Path(file)
            if not path.is_absolute():
                path = directory.joinpath(path)
            paths.append(path)

        return paths

    def read_requirements(self, project: ReqProject):
        """Read all the requirements from the documents."""
        assert self.project

        self.map_requirements = {}
        files = self.get_documents()

        # for now, consider only MS Word documents (DOCX)
        req_style = self.project.get_scalar_tool_prop_def(
            'MSOFFICE', 'REQSTYLE', 'Requirement_ID', None
        )
        text_style = self.project.get_scalar_tool_prop_def(
            'MSOFFICE', 'TEXTSTYLE', 'Requirement_Text', None
        )
        for path in files:
            if path.suffix == '.docx':
                self.map_requirements.update(
                    msword.add_document(project, path, req_style, text_style)
                )


def main():
    """Implement the ``ansys.scade.almgw_msoffice:main`` packages's project script."""
    proxy = MSOffice()
    return proxy.main()


if __name__ == '__main__':
    main()
