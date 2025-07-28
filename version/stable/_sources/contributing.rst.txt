.. _contribute_scade_almgw_msoffice:

Contribute
##########

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to Ansys SCADE ALM Gateway connector for MS-Office.

The following contribution information is specific to Ansys SCADE ALM Gateway connector for MS-Office.

Install in developer mode
=========================
Installing Ansys SCADE ALM Gateway connector for MS-Office in developer mode allows you to modify the
source and enhance it.

#. Clone the ``ansys-scade-almgw-msoffice`` repository:

   .. code:: bash

      git clone https://github.com/ansys/scade-almgw-msoffice

#. Access the ``scade-almgw-msoffice`` directory where the repository has been cloned:

   .. code:: bash

      cd scade-almgw-msoffice

#. Create a clean Python 3.10 environment and activate it:

   You should use the interpreter delivered with Ansys SCADE. For example,
   ``C:\Program Files\ANSYS Inc\v241\SCADE\contrib\Python310\python.exe``.

   .. code:: bash

      # Create a virtual environment
      <path/to/SCADE/python/interpreter> -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Make sure that you have the latest required build system, documentation, testing,
   and CI tools:

   .. code:: bash

      python -m pip install -U pip     # Upgrading pip
      python -m pip install tox        # Installing tox (optional)
      python -m pip install .[build]   # for building the wheels
      python -m pip install .[tests]   # for testing the package
      python -m pip install .[doc]     # for building the documentation

#. Install the project in editable mode:

   .. code:: bash

      python -m pip install --editable .

#. Use `tox`_ to verify your development installation:

   .. code:: bash

      tox


Test
====
Ansys SCADE ALM Gateway connector for MS-Office uses `tox`_ for testing. This tool allows you to
automate common development tasks (similar to ``Makefile``), but it is oriented
towards Python development.

Use ``tox``
-----------

While ``Makefile`` has rules, ``tox`` has environments. In fact, ``tox`` creates its
own virtual environment so that anything being tested is isolated from the project
to guarantee the project's integrity.

The following ``tox`` commands are provided:

* ``tox -e code-style``: Checks for coding style quality.
* ``tox -e tests``: Checks for unit testing without code coverage.
* ``tox -e tests-coverage``: Checks for unit testing with code coverage.
* ``tox -e doc``: Checks for the documentation-building process.
   * ``tox -e doc-html``: Builds the HTML documentation.
   * ``tox -e doc-links``: Checks for broken links in the documentation.

.. tip::

   For convenience (and advanced usage), you can set a ``SCADE_INSTALLATION_DIR`` environment
   variable pointing to SCADE's installation directory, for example ``C:\Program Files\ANSYS Inc\vXXX\SCADE``.
   This will allow Tox automatically discover and use the Python interpreters that ship with SCADE in
   creating virtual environments via ``py310`` and ``py37`` factors. Using this approach, ``tox``
   commands similar to the following formats can be used:

   * ``tox -e tests-py37``: for running tests without coverage using the Python 3.7 interpreter delivered with SCADE.
   * ``tox -e tests-coverage-py310``: for running tests with coverage using the Python 3.10 interpreter delivered with SCADE.

   The host python interpreter does not have to be the one delivered with SCADE when using this approach and this
   behavior is agnostic of the host python version in which tox itself is installed. The important point to note
   is that Python 3.7 is compatible with SCADE releases prior to 23R2 and Python 3.10 compatibility starts with 23R2. This means
   that ``py37`` factor should be used when testing with releases prior to 23R2 and ``py310`` factor should be used when testing
   with releases starting from 23R2.

Use raw testing
---------------
If required, from the command line, you can call style commands like
`black`_, `isort`_, and `flake8`_. You can also call unit testing commands like `pytest`_.
However, running these commands does not guarantee that your project is being tested in an
isolated environment, which is the reason why tools like ``tox`` exist.

Use ``pre-commit``
------------------
Ansys SCADE ALM Gateway connector for MS-Office follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys developer's guide* and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  Add License Headers......................................................Passed
  ruff.....................................................................Passed
  ruff-format..............................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  check yaml...............................................................Passed
  trim trailing whitespace.................................................Passed
  numpydoc-validation......................................................Passed
  Validate GitHub Workflows................................................Passed
  check pre-commit.ci config...............................................Passed

Build documentation
===================
For building documentation, you can run the usual rules provided in the
`Sphinx`_ ``make`` file. Here are some examples:

.. code:: bash

    #  build and view the doc from the POSIX system
    make -C doc/ html && your_browser_name doc/_build/html/index.html

    # build and view the doc from a Windows environment
    .\doc\make.bat clean
    .\doc\make.bat html
    start .\doc\_build\html\index.html

However, the recommended way of checking documentation integrity is to use
``tox``:

.. code:: bash

    tox -e doc-html && your_browser_name doc/_build/html/index.html

Distribute
==========
If you would like to create either source or wheel files, start by installing
the building requirements and then executing the build module:

.. code:: bash

    python -m pip install .[build]
    python -m build
    python -m twine check dist/*

Post issues
===========

Use the `Ansys SCADE ALM Gateway connector for MS-Office Issues <https://github.com/ansys/scade-almgw-msoffice/issues>`_
page to submit questions, report bugs, and request new features. When possible, use
these templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, click
the link for opening a blank issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

.. LINKS AND REFERENCES

.. _tox: https://tox.wiki/en/4.12.0/
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _wheel file: https://github.com/ansys/scade-almgw-msoffice/releases