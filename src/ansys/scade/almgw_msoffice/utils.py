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

"""Utilities for managing Excel documents."""

from typing import Any, Dict, Optional, Tuple, Union

from xlsxwriter import Workbook
from xlsxwriter.format import Format

FormatCtor = Dict[str, Any]


class Formats:
    """Cache for formats."""

    def __init__(self, wb: Workbook) -> None:
        """Initialize the cache."""
        self.wb = wb
        self.formats = {}  # type: Dict[str, Format]

    def add_format(self, fmt_name: str, fmt_dict: FormatCtor) -> Format:
        """Add a new format."""
        fmt = self.wb.add_format(fmt_dict)
        self.formats[fmt_name] = fmt
        return fmt

    def get(self, name: str) -> Optional[Format]:
        """Return a format."""
        return self.formats.get(name)


class Cursor:
    """Cursor management."""

    def __init__(self, ws, pos: Tuple[int, int] = (0, 0)) -> None:
        """Initialize the cursor."""
        self.pos = pos
        self.ws = ws

    def move(self, v: Tuple[int, int]):
        """N/A."""
        y, x = self.pos
        dy, dx = v
        self.pos = y + dy, x + dx
        return self

    def left(self):
        """N/A."""
        return self.move((0, -1))

    def right(self):
        """N/A."""
        return self.move((0, 1))

    def up(self):
        """N/A."""
        return self.move((-1, 0))

    def down(self):
        """N/A."""
        return self.move((1, 0))

    def line(self) -> int:
        """N/A."""
        line, _ = self.pos
        return line

    def col(self) -> int:
        """N/A."""
        _, col = self.pos
        return col

    def new_line(self, new_col=0):
        """N/A."""
        self.pos = self.line() + 1, new_col
        return self

    def write(self, *args):
        """N/A."""
        row, col = self.pos
        self.ws.write(row, col, *args)
        return self

    def write_url(
        self, url: str, cell_format: Optional[Format] = None, string: str = None, tip: str = None
    ):
        """N/A."""
        row, col = self.pos
        self.ws.write_url(row, col, url, cell_format=cell_format, string=string, tip=tip)
        return self

    def insert_image(self, image: str, options: Dict[str, Union[int, str]] = {}):
        """N/A."""
        row, col = self.pos
        self.ws.insert_image(row, col, image, options)
        return self

    def set_row(
        self,
        height: float = None,
        cell_format: Optional[Format] = None,
        options: Dict[str, Union[int, str]] = {},
    ):
        """N/A."""
        self.ws.set_row(self.line(), height, cell_format, options)
        return self

    def set_column(
        self,
        width: float = None,
        cell_format: Optional[Format] = None,
        options: Dict[str, Union[int, str]] = {},
    ):
        """N/A."""
        self.ws.set_column(self.col(), self.col(), width=width, cell_format=None, options={})
        return self

    def write_comment(self, comment: str):
        """N/A."""
        row, col = self.pos
        if comment is not None:
            self.ws.write_comment(row, col, comment)
        return self

    def set_row_lvl(self, level: int, collapsed: bool = False):
        """N/A."""
        return self.set_row(None, None, {'level': min(level, 7), 'collapsed': collapsed})

    def set_column_width(self, width: float):
        """N/A."""
        return self.set_column(width=width)
