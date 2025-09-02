User Guide
##########

Declaration
===========

Use the command ``Project/ALM Gateway/Settings...`` once
to select the connector ``ALMGW Connector for MS-Office``.

Once the connector is selected, this command does not operate anymore.
Refer to the next section for details on settings management.

.. Note::

   If the project is already connected to an ALM tool, you have first to delete this connection
   by deleting the ALM Gateway project file (ALMGP) in the project’s directory.

Settings
========

Using the Graphical User Interface
----------------------------------

This mode applies only to projects that can be loaded with SCADE Studio.
SCADE Display projects must be setup using the command line interface,
as explained in the next section.

Use the new command ``Project/ALM Gateway/MS Office Settings...`` to:

* Select the requirements documents for each loaded project.
* Select the names of the styles to consider for the requirements and their text.
* Specify the LLR export schema to produce an MS Excel traceability matrix.

  .. Note::

     Refer to `Traceable Elements Export Schema`_ for details.

.. image:: /_static/settings.png

Using the Command Line Interface
--------------------------------

The command line tool python ``setup_ansys_scade_almgw_msoffice.exe`` allows to setup
the project. It is located in the ``Scripts`` folder of the Python installation directory.

.. code:: text

    usage: setup_ansys_scade_almgw_msoffice [-h] -p <project> [-r <req>]
                                            [-t <text>] [-s <schema>]
                                            [-d [<documents> ...]]

    options:
      -h, --help            show this help message and exit
      -p <project>, --project <project>
                            Ansys SCADE project (ETP)
      -r <req>, --req_style <req>
                            requirement identifier style
      -t <text>, --text_style <text>
                            requirement text style
      -s <schema>, --schema <schema>
                            json export schema
      -d [<documents> ...], --documents [<documents> ...]
                            documents

For example:

.. code:: text

   setup_ansys_scade_almgw_msoffice -p MyProject.etp -d ../docs/Requirements.docx

Files
=====

Ansys SCADE ALM Gateway connector for MS-Office produces several files in the project's directory.

The file ``<project.msoffice.trace>`` stores the traceability links
and must be added to the configuration management system.

The other files are present for logging or debug purpose only:

* ``<project.msoffice.llrs>``: Temporary file for producing the traceability matrices.
* ``<project.msoffice.reqs>``: Copy of exchange file for importing the traceability.
* ``<links.json>``: Copy of exchange file for exporting the traceability.

Migration from 2.x versions
===========================

This connector is compatible with former releases 2.x.
To migrate an existing SCADE ALM Gateway project using the 2.x version of the connector,
edit the project file (ALMGP) and change its ``confFileName`` attribute from ``msoffice`` to ``almgw_msoffice``.

Limitations
===========

The connector supports only MS-Word files (DOCX) for input requirements.

.. _Traceable Elements Export Schema: https://pyalmgw.scade.docs.pyansys.com/version/stable/usage/schema.html
