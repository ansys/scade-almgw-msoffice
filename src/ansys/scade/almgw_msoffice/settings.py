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

"""Provides the ``MS Office Settings`` command."""

from enum import Enum
import os
from pathlib import Path

from scade.model.project.stdproject import Project, get_roots as get_projects
from scade.tool.suite.gui.commands import Command, Menu
from scade.tool.suite.gui.dialogs import Dialog, file_open, file_save
from scade.tool.suite.gui.widgets import Button, EditBox, Label, ListBox, ObjectComboBox

import ansys.scade.almgw_msoffice as ms
import ansys.scade.pyalmgw as pyamlgw

script_path = Path(__file__)
script_dir = script_path.parent

# -----------------------------------------------------------------------
# globals
# -----------------------------------------------------------------------

# default value, for compatibility with property pages
H_BUTTON = 20
H_COMBO = 130
H_EDIT = 20
H_LABEL = 20
H_LIST = 130
H_TREE = 30
# width of ... buttons
W_DOTS = 20

# left/right margin
hm = 15
# position / size for labels
xl = hm
wl = 140
# position / size for fields
xf = 160
wf = 250
# vertical start position
y = 7
# space between two lines
dy = 30

# width of the dialog, without margins
wd = xf - xl + wf

# ---------------------------------------------------------------------------
# reusable control library
# ---------------------------------------------------------------------------


# FileSelectorMode
class FSM(Enum):
    """Modes of the file selector bundle."""

    LOAD, SAVE = range(2)


class LabelEditBox(EditBox):
    """Bundles an edit box with a label."""

    def __init__(self, owner, text: str, wl: int, x=10, y=10, w=50, h=14, **kwargs):
        """Initialize the edit box."""
        self.label = Label(owner, text, x=x, y=y + 4, w=wl, h=H_LABEL)
        super().__init__(owner, x=x + wl, y=y, w=w - wl, h=H_EDIT, **kwargs)
        self.owner = owner


class FileSelector(LabelEditBox):
    """Bundles a file selector widget with a label, edit and button."""

    def __init__(
        self,
        owner,
        text: str,
        extension: str,
        dir: str,
        filter: str,
        mode: FSM,
        wl: int,
        x=10,
        y=10,
        w=50,
        h=14,
        **kwargs,
    ):
        """Initialize the file selector."""
        super().__init__(owner, text, wl, x=x, y=y, w=w - W_DOTS - 5, h=h, **kwargs)
        self.btn_dots = Button(
            owner, '...', x=x + w - W_DOTS, y=y, w=W_DOTS, h=H_BUTTON, on_click=self.on_click
        )
        self.owner = owner
        self.extension = extension
        self.dir = dir
        self.filter = filter
        self.mode = mode
        # set at runtime
        self.reldir = ''

    def on_click(self, button: Button):
        """Prompt the user for a configuration file."""
        name = self.get_name()
        name = '' if '$' in name else name
        dir = '' if '$' in self.dir else self.dir
        if dir and self.reldir:
            dir = str(Path(self.reldir) / dir)
        if self.mode == FSM.SAVE:
            pathname = file_save(name, self.extension, dir, self.filter)
        else:
            pathname = file_open(self.filter, dir)
        if pathname:
            if self.reldir:
                try:
                    pathname = os.path.relpath(pathname, self.reldir)
                except ValueError:
                    pass
            self.set_name(pathname)


class LabelComboBox(ObjectComboBox):
    """Bundles a combo box with a label."""

    def __init__(self, owner, text: str, wl: int, items, x=10, y=10, w=50, h=14, **kwargs):
        """Initialize the combo box."""
        self.label = Label(owner, text, x=x, y=y + 4, w=wl, h=H_LABEL)
        super().__init__(owner, items, x=x + wl, y=y, w=w - wl, h=H_COMBO, **kwargs)
        self.owner = owner


# -----------------------------------------------------------------------
# MS Office Settings
# -----------------------------------------------------------------------

# overall dimensions
w_settings = wd + hm * 2
# something strange, need to add one level of margin more
w_settings += 15
h_settings = 350


class Settings(Dialog):
    """Settings editor for the connector."""

    # cache selected project between calls
    project = None

    def __init__(self):
        """Initialize the dialog."""
        super().__init__('MS-Office Settings', w_settings, h_settings)

        # controls
        self.cb_projects = None
        self.ed_req_style = None
        self.ed_text_style = None
        self.ed_schema = None
        self.lb_documents = None
        self.pb_ok = None
        self.pb_cancel = None

        # runtime
        self.project = None

    def add_edit(self, y: int, text: str) -> EditBox:
        """Add an edit bundle with normalized positions."""
        edit = LabelEditBox(self, text, wl, x=xl, y=y, w=wd)
        return edit

    def add_file(
        self, y: int, text: str, extension: str, dir: str, filter: str, mode: FSM
    ) -> FileSelector:
        """Add a file selector bundle with normalized positions."""
        file = FileSelector(self, text, extension, dir, filter, mode, wl, x=xl, y=y, w=wd, h=H_EDIT)
        return file

    def on_build(self):
        """Build the dialog."""
        # alignment for the first line
        y = 7

        projects = get_projects()
        # reuse last selected project if any and still exists
        project = self.project if self.project in projects else projects[0]
        assert isinstance(project, Project)
        # reset current project
        self.project = None
        style = ['dropdownlist', 'sort']
        self.cb_projects = LabelComboBox(
            self,
            '&Project:',
            wl,
            projects,
            x=xl,
            y=y,
            w=wd,
            selection=project,
            style=style,
            on_change_selection=self.on_project_selection,
        )
        y += dy
        self.ed_req_style = self.add_edit(y, '&Requirement style:')
        y += dy
        self.ed_text_style = self.add_edit(y, '&Text style:')
        y += dy
        filter = 'LLR Schema (*.json)|*.json|LLR Schema (*.txt)|*.txt|All Files (*.*)|*.*||'
        # ? default_dir = os.path.dirname(project.pathname)
        default_dir = ''
        self.ed_schema = self.add_file(
            y, '&LLR export schema:', '.json', default_dir, filter, FSM.LOAD
        )
        y += dy
        Label(self, 'Requirement &documents:', x=xl, y=y + 4, w=wl, h=H_LABEL)
        y += dy
        hd = h_settings - 85 - y
        self.lb_documents = ListBox(self, [], x=15, y=y, w=wd, h=hd, style=['sort'])
        y += hd + 10

        # width of a button
        wb = 65
        # space between buttons
        mb = 10
        self.pb_ok = Button(self, '&Add', x=xl, y=y, w=wb, h=H_BUTTON, on_click=self.on_add)
        self.pb_cancel = Button(
            self, 'Re&move', x=xl + wb + mb, y=y, w=wb, h=H_BUTTON, on_click=self.on_remove
        )
        self.pb_ok = Button(
            self, 'OK', x=xl + wd - wb * 2 - mb, y=y, w=wb, h=H_BUTTON, on_click=self.on_ok
        )
        self.pb_cancel = Button(
            self, 'Cancel', x=xl + wd - wb, y=y, w=wb, h=H_BUTTON, on_click=self.on_cancel
        )

        # side effect
        self.on_set_project(project)

    def on_set_project(self, project: Project):
        """Update the settings and the dialog after a project is selected."""
        if project == self.project:
            return
        if self.project:
            self.write_settings()
        self.project = project
        self.read_settings()

    def on_project_selection(self, cb: ObjectComboBox, index: int):
        """Update current project."""
        project = cb.get_selection()
        assert isinstance(project, Project)
        self.on_set_project(project)

    def on_ok(self, *args):
        """Save the changes and close the dialog."""
        self.write_settings()
        self.close()

    def on_cancel(self, *args):
        """Close the dialog."""
        self.close()

    def on_add(self, *args):
        """Prompt the user for a new document."""
        assert self.project

        path = file_open('MS Word Documents (*.docx)|*.docx|All Files (*.*)|*.*||')
        if path:
            assert self.lb_documents
            try:
                document = os.path.relpath(path, Path(self.project.pathname).parent)
            except ValueError:
                document = path
            documents = self.lb_documents.get_items()
            if document not in documents:
                documents.append(document)
                self.lb_documents.set_items(documents)

    def on_remove(self, *args):
        """Remove the selected documents."""
        assert self.lb_documents
        selected = self.lb_documents.get_selection()
        if selected:
            documents = [_ for _ in self.lb_documents.get_items() if _ not in selected]
            self.lb_documents.set_items(documents)

    def read_settings(self):
        """Update the dialog with the project's settings."""
        assert self.project

        assert self.lb_documents
        documents = self.project.get_tool_prop_def(
            ms.TOOL, ms.DOCUMENTS, ms.DOCUMENTS_DEFAULT, None
        )
        self.lb_documents.set_items(documents)

        assert self.ed_req_style
        style = self.project.get_scalar_tool_prop_def(
            ms.TOOL, ms.REQSTYLE, ms.REQSTYLE_DEFAULT, None
        )
        self.ed_req_style.set_name(style)

        assert self.ed_text_style
        style = self.project.get_scalar_tool_prop_def(
            ms.TOOL, ms.TEXTSTYLE, ms.TEXTSTYLE_DEFAULT, None
        )
        self.ed_text_style.set_name(style)

        assert self.ed_schema
        schema = self.project.get_scalar_tool_prop_def(
            pyamlgw.TOOL, pyamlgw.LLRSCHEMA, pyamlgw.LLRSCHEMA_DEFAULT, None
        )
        self.ed_schema.set_name(schema)
        self.ed_schema.reldir = str(Path(self.project.pathname).parent)

    def write_settings(self):
        """Update the project's settings from the dialog."""
        assert self.project

        assert self.lb_documents
        documents = self.lb_documents.get_items()
        self.project.set_tool_prop_def(ms.TOOL, ms.DOCUMENTS, documents, ms.DOCUMENTS_DEFAULT, None)

        assert self.ed_req_style
        style = self.ed_req_style.get_name()
        self.project.set_scalar_tool_prop_def(
            ms.TOOL, ms.REQSTYLE, style, ms.REQSTYLE_DEFAULT, None
        )

        assert self.ed_text_style
        style = self.ed_text_style.get_name()
        self.project.set_scalar_tool_prop_def(
            ms.TOOL, ms.TEXTSTYLE, style, ms.TEXTSTYLE_DEFAULT, None
        )

        assert self.ed_schema
        schema = self.ed_schema.get_name()
        self.project.set_scalar_tool_prop_def(
            pyamlgw.TOOL, pyamlgw.LLRSCHEMA, schema, pyamlgw.LLRSCHEMA_DEFAULT, None
        )


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


class CommandSettings(Command):
    """Defines a command to edit the settings."""

    def __init__(self):
        """Initialize the command settings."""
        image = str(script_dir / 'res' / 'msword.bmp')
        super().__init__(
            name='MS-Office Settings...',
            status_message='MS-Office Settings',
            tooltip_message='MS-Office Settings',
            image_file=image,
        )

    def on_activate(self):
        """Open the dialog."""
        Settings().do_modal()

    def on_enable(self):
        """Return whether the command is available."""
        return len(get_projects()) != 0


# -----------------------------------------------------------------------------
# GUI items
# -----------------------------------------------------------------------------

Menu([CommandSettings()], '&Project/ALM Gateway')
