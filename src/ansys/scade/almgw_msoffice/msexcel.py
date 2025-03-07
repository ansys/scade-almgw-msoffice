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

"""Generation of traceability matrices as an Excel document."""

from collections import defaultdict
from copy import copy
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, TypeVar

import xlsxwriter as xl

from ansys.scade.almgw_msoffice.utils import Cursor, Formats
from ansys.scade.pyalmgw.documents import Container, ReqProject, Requirement, Section

CovResult = Tuple[int, int]  # Coverage result (nb_covered, nb_total)
SectionDesc = List[Tuple[str, Iterator[bool]]]  # Section description
Headers = List[Tuple[str, float]]  # List of (header name , column size )
LlrElement = Dict[str, Any]  # Dict from JSON

##############################################################################
#
#   COMMON functions for both HLR→LLR and LLR→HLR sheets
#
##############################################################################

T = TypeVar('T')


def constant(v: T) -> Iterator[T]:
    """Return Scade's constant flow ``v``."""
    while True:
        yield v


def init(init_value: T, other_value: T) -> Iterator[T]:
    """Return Scade's flow ``init_value -> other_value``."""
    yield init_value
    yield from constant(other_value)


def on_first() -> Iterator[bool]:
    """Return Scade's flow ``true -> false``."""
    yield from init(True, False)


def add_cov(x: CovResult, y: CovResult) -> CovResult:
    """Return the combination of two coverage statuses."""
    x_cov, x_tot = x
    y_cov, y_tot = y
    return x_cov + y_cov, x_tot + y_tot


def write_headers(formats: Formats, c: Cursor, headers: Headers) -> None:
    """Write the header of a matrix."""
    header_fmt = formats.get('header')
    for name, width in headers:
        c.write(name, header_fmt).set_column_width(width).right()
    c.left()
    c.ws.autofilter(0, 0, 0, c.col())
    c.new_line()


def write_section(
    c: Cursor, formats: Formats, is_first: bool, upper_section: SectionDesc, nb_sections: int
) -> None:
    """Write a section of a matrix."""
    dupe_fmt = formats.get('dupe')
    section_fmt = formats.get('section')
    for upper, first_occur_iterator in upper_section:
        fmt = section_fmt if is_first and next(first_occur_iterator) else dupe_fmt
        c.write(upper, fmt).right()
    for _ in range(len(upper_section), nb_sections):
        c.write('…', fmt).right()  # continue with the previous cell format


def is_section(llr_elt: LlrElement) -> bool:
    """Return whether a LLR element is a section."""
    return llr_elt.get('almtype') == 'section'


def is_req(llr_elt: LlrElement) -> bool:
    """Return whether a LLR element is a requirement."""
    return llr_elt.get('almtype') == 'req'


def iter_llr_section(s: LlrElement) -> Iterator[LlrElement]:
    """Iterate the document hierarchy."""
    for e in s.get('elements', []):
        if is_section(e):
            yield from iter_llr_section(e)
        elif is_req(e):
            yield e
        else:
            return None


def write_llr_name_and_type(formats: Formats, c: Cursor, llr: LlrElement, is_first: bool) -> None:
    """Write a LLR, its kind, and insert its icon."""

    def llr_str(field: str, default: str = '') -> str:
        """Return the value of a field in a LLR element."""
        r = llr.get(field, default)
        return r if isinstance(r, str) else default

    llr_icon = llr_str('icon')
    llr_type = llr_str('scadetype')
    llr_fmt = formats.get('LLR') if is_first else formats.get('LLR dupe')

    if llr_icon is None:
        c.write(llr_type, llr_fmt).right()
    else:
        c.insert_image(llr_icon, {'x_offset': 2, 'y_offset': 4, 'positioning': 1}).write(
            llr_type, llr_fmt
        ).right()
    c.write_url(llr_str('url'), string=llr_str('name'), tip=llr_str('pathname')).right()


def write_section_cov(c: Cursor, cov: CovResult, formats: Formats) -> None:
    """Write the section's coverage."""
    nb_covered, nb_total = cov
    cov_fmt = formats.get('section covered') if nb_covered == nb_total else formats.get('section')
    c.write('={0}/{1}'.format(nb_covered, nb_total), cov_fmt).right()


##############################################################################
#   HLR→LLR
##############################################################################


def hlr_to_llr_sheet(ws, formats: Formats, project: ReqProject, llr_dict: LlrElement):
    """Generate the downstream matrix."""
    hlr_links = defaultdict(set)  # type: DefaultDict[str, Set[TraceabilityLink]]
    for link in project.traceability_links:
        hlr_links[link.target].add(link)

    llr_dict = {llr.get('oid'): llr for llr in iter_llr_section(llr_dict)}

    c = Cursor(ws)
    nb_sections = project.depth - 1

    headers = [('HLR Document', 30.0)]
    headers += [('HLR Section ({0})'.format(lvl), 25.0) for lvl in range(1, nb_sections)]
    headers += [('HLR Name', 17.0), ('LLR Type', 14.0), ('To LLR', 17.0)]

    write_headers(formats, c, headers)

    def hlr(r: Requirement, upper_section: SectionDesc, level: int) -> int:
        """Write HLR Requirement with Cursor c.

        Returns the number of LLR covering this HLR, 0 if uncovered.
        """

        def write_hlr_line(is_first: bool, llr: Optional[LlrElement]):
            """Write a High-Level Requirement (HLR) line to the Excel sheet."""
            write_section(c, formats, is_first, upper_section, nb_sections)
            dupe_fmt = formats.get('dupe')
            c.write(r.id, None if is_first else dupe_fmt).write_comment(r.description).right()
            if llr is None:
                c.write('✗', dupe_fmt).right()
                c.write('<Uncovered>', formats.get('uncovered')).right()
            else:
                write_llr_name_and_type(formats, c, llr, True)
            c.new_line()

        llr_list = [llr_dict.get(link.source) for link in hlr_links[r.id]]
        llr_list = [_ for _ in llr_list if _ is not None]
        if not llr_list:
            write_hlr_line(True, None)
        else:
            for is_first, llr in zip(on_first(), llr_list):
                write_hlr_line(is_first, llr)

        return len(llr_list)

    def hlr_section(s: Container, upper_section: SectionDesc) -> CovResult:
        """Write a High-Level Requirement (HLR) section to the Excel sheet."""
        cov_res = (0, 0)
        if not s.is_empty():
            upper_section = upper_section + [(s.text, on_first())]
            write_section(c, formats, True, upper_section, nb_sections)
            s_cursor = copy(
                c
            )  # copy the cursor to finish writing the section line once the leefs are written
            c.new_line()

            for r in s.requirements:
                level = s.level + 1 if isinstance(s, Section) else 0
                covered_by = hlr(r, upper_section, level)
                cov = (1, 1) if covered_by > 0 else (0, 1)
                cov_res = add_cov(cov_res, cov)
            for sub in s.sections:
                sub_cov = hlr_section(sub, upper_section)
                cov_res = add_cov(cov_res, sub_cov)

            section_fmt = formats.get('section')
            s_cursor.write('…', section_fmt).right()
            s_cursor.write('…', section_fmt).right()
            write_section_cov(s_cursor, cov_res, formats)
        return cov_res

    for d in project.documents:
        hlr_section(d, [])
    c.ws.freeze_panes(1, 0)


##############################################################################
#   LLR→HLR
##############################################################################


def llr_attributes(llr_section: LlrElement) -> Set[str]:
    """Return the overall attributes."""
    ret = set()
    for req in iter_llr_section(llr_section):
        for att in req.get('attributes', []):
            name = att.get('name')
            if name is not None:
                ret.add(name)
    return ret


def llr_section_depth(section: LlrElement) -> int:
    """Return the max depth of the document hierarchy."""
    return 1 + max(
        [
            llr_section_depth(sub)
            for sub in section.get('elements', [])
            if sub.get('almtype') == 'section'
        ],
        default=0,
    )


def llr_to_hlr_sheet(ws, formats: Formats, project: ReqProject, llr_dict: LlrElement):
    """Generate the upstream matrix."""
    llr_links = defaultdict(set)  # type: DefaultDict[str, Set[TraceabilityLink]]
    for link in project.traceability_links:
        llr_links[link.source].add(link)

    hlr_dict = dict()
    for d in project.documents:
        for req in d.iter_requirements():
            hlr_dict[req.id] = req

    c = Cursor(ws)
    nb_sections = llr_section_depth(llr_dict) - 1
    llr_attribute_names = llr_attributes(llr_dict)

    headers = [('LLR Section ({0})'.format(lvl), 16.0) for lvl in range(1, nb_sections + 1)]
    headers += [('LLR Type', 14.0), ('LLR Name', 17.0), ('From HLR', 15.0)]
    headers += [(n, 12.0) for n in llr_attribute_names]

    write_headers(formats, c, headers)

    def llr(r: Dict, upper_section: SectionDesc) -> int:
        """Write LLR Requirement with Cursor c.

        Return the number of HLR covering this LLR (0 if uncovered)
        """
        llr_attributes = r.get('attributes', [])
        llr_attributes = {a.get('name'): a.get('value') for a in llr_attributes}

        def write_llr_line(is_first: bool, req: Optional[Requirement]) -> None:
            """Write a Low-Level Requirement (LLR) line to the Excel sheet."""
            dupe_fmt = formats.get('dupe')
            write_section(c, formats, is_first, upper_section, nb_sections)
            write_llr_name_and_type(formats, c, r, is_first)

            if req is None:
                c.write('<Uncovered>', formats.get('uncovered')).right()
            else:
                c.write(req.id).write_comment(req.description).right()

            for att_name in llr_attribute_names:
                try:
                    c.write(llr_attributes[att_name], None if is_first else dupe_fmt).right()
                except KeyError:
                    c.write('✗', dupe_fmt).right()

            c.new_line()

        llr_oid = r.get('oid')
        hlr_list = [hlr_dict.get(link.target) for link in llr_links[llr_oid]]
        hlr_list = [_ for _ in hlr_list if _ is not None]
        if not hlr_list:
            write_llr_line(True, None)
        else:
            for is_first, hlr in zip(on_first(), hlr_list):
                write_llr_line(is_first, hlr)

        return len(hlr_list)

    def llr_section(s: LlrElement, upper_section: SectionDesc) -> CovResult:
        """Write a Low-Level Requirement (LLR) section to the Excel sheet."""
        cov_res = 0, 0
        if any(iter_llr_section(s)):  # s is not empty
            children = [e for e in s.get('elements', [])]
            subsections = [e for e in children if is_section(e)]
            llrs = [e for e in children if is_req(e)]
            upper_section = upper_section + [(s.get('name'), on_first())]
            write_section(c, formats, True, upper_section, nb_sections)
            section_fmt = formats.get('section')
            c.write('…', section_fmt).right()
            c.write('…', section_fmt).right()
            s_cursor = copy(c)
            c.new_line()

            for ce in llrs:
                nb_covered = llr(ce, upper_section)
                llr_cov = (1, 1) if nb_covered > 0 else (0, 1)
                cov_res = add_cov(cov_res, llr_cov)
            for sub in subsections:
                sub_cov = llr_section(sub, upper_section)
                cov_res = add_cov(cov_res, sub_cov)

            write_section_cov(s_cursor, cov_res, formats)
            for _ in llr_attribute_names:
                s_cursor.write('', section_fmt).right()

        return cov_res

    for s in filter(is_section, llr_dict.get('elements', [])):
        llr_section(s, [])
    c.ws.freeze_panes(1, 0)


##############################################################################
#   Entry point
##############################################################################


def generate_matrix(project: ReqProject, llr_dict: LlrElement) -> None:
    """Generate downstream and upstream traceaibility matrices."""
    fname = Path(llr_dict['path']).with_suffix('.xlsx')
    wb = xl.Workbook(str(fname))
    formats = Formats(wb)

    formats.add_format('header', {'bold': True})
    formats.add_format('dupe', {'font_color': 'silver'})
    formats.add_format('uncovered', {'font_color': 'red', 'bold': False})
    formats.add_format('LLR', {'indent': 2})
    formats.add_format('LLR dupe', {'font_color': 'silver', 'indent': 2})
    formats.add_format('section', {'top_color': 'black', 'top': 3, 'num_format': '0.00%'})
    formats.add_format(
        'section covered',
        {'font_color': 'green', 'top_color': 'black', 'top': 3, 'num_format': '0.00%'},
    )

    hlr_to_llr, llr_to_hlr = (wb.add_worksheet(name) for name in ('HLR → LLR', 'LLR → HLR'))
    hlr_to_llr_sheet(hlr_to_llr, formats, project, llr_dict)
    llr_to_hlr_sheet(llr_to_hlr, formats, project, llr_dict)

    wb.close()
