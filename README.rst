Ansys SCADE ALM Gateway connector for MS-Office
===============================================
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |ruff| |doc|

..
   |ansys-scade| image:: https://img.shields.io/badge/Ansys-SCADE-ffb71b?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://github.com/ansys-scade/
   :alt: Ansys SCADE

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-scade-almgw-msoffice?logo=pypi
   :target: https://pypi.org/project/ansys-scade-almgw-msoffice/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-scade-almgw-msoffice.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-scade-almgw-msoffice
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/scade-almgw-msoffice/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/scade-almgw-msoffice
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/scade-almgw-msoffice/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/scade-almgw-msoffice/actions/workflows/ci_cd.yml

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

.. |doc| image:: https://img.shields.io/badge/docs-almgw--msoffice-green.svg?style=flat
   :target: https://almgw-msoffice.scade.docs.pyansys.com
   :alt: Doc


Overview
--------
Ansys SCADE ALM Gateway connector for MS-Office demonstrates the usage of
Ansys SCADE ALM Gateway based on MS Office documents, avoiding the availability
of an external ALM tool:

* It imports requirements from MS-Word documents
* It produces traceability matrices as MS-Excel documents

It is also a usage example of `Ansys SCADE ALM Gateway Python Toolbox`_.

Requirements
------------
The ``ansys-scade-almgw-msoffice`` package supports only the versions of Python delivered with
Ansys SCADE, starting from 2021 R2:

* 2021 R2 through 2023 R1: Python 3.7
* 2023 R2 and later: Python 3.10

Ansys SCADE ALM Gateway connector for MS-Office has two installation modes: user and developer. To install for use,
see `Getting started <https://almgw-msoffice.scade.docs.pyansys.com/version/stable/getting-started/index.html>`_.
To install for development, see `Contribute <https://almgw-msoffice.scade.docs.pyansys.com/version/stable/contributing.html>`_.

Documentation and issues
------------------------
Documentation for the latest stable release of Ansys SCADE ALM Gateway connector for MS-Office is hosted at
`Ansys SCADE ALM Gateway connector for MS-Office documentation <https://almgw-msoffice.scade.docs.pyansys.com/>`_.

In the upper right corner of the documentation's title bar, there is an option for
switching from viewing the documentation for the latest stable release to viewing the
documentation for the development version or previously released versions.

On the `Ansys SCADE ALM Gateway connector for MS-Office Issues <https://github.com/ansys/scade-almgw-msoffice/issues>`_
page, you can create issues to report bugs and request new features. On the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

License
~~~~~~~
Ansys SCADE ALM Gateway connector for MS-Office is licensed under the MIT license.

This toolkit makes no commercial claim over Ansys whatsoever. The use of this toolkit
requires a legally licensed copy of the Ansys SCADE Suite. For more information,
see the `Ansys SCADE Suite <https://www.ansys.com/products/embedded-software/ansys-scade-suite>`_
page on the Ansys website.

.. _Ansys SCADE ALM Gateway Python Toolbox: https://pyalmgw.scade.docs.pyansys.com/
