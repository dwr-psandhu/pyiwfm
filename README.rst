===============================
pyiwfm
===============================

-------------------------
Python utilities for IWFM
-------------------------

IWFM_ is a water resources model that includes a groundwater and stream flow routing model. 
These are a set of utilties to visualize the input and output for that model

.. _IWFM: https://water.ca.gov/Library/Modeling-and-Analysis/Modeling-Platforms/Integrated-Water-Flow-Model

------------
Installing
------------

Miniconda_ is required. After installing, clone this repository and change directory to it. That will 
allow the commands below to access the environment.yml file that is needed to setup the environment.

::

    conda config --set channel_priority strict
    conda env create -f environment.yml


The above command ensures that strict channel priority is used when creating the environment.
The environment will be named env_iwfm by default and will contain all the dependencies needed. 

Finally, clone this directory and change directory to it and install it as followsd

::

    conda activate env_iwfm
    pip install -e .


To confirm installation 

::

    conda activate env_iwfm 
    pyiwfm --version


.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html

-----
Usage
-----

From the command line 

Ensure that environment is activated

::

    conda activate env_iwfm


To get help on commands and sub-commands

::

    pyiwfm --help

    usage: pyiwfm [-h] [-V] {trimesh-animator,head-obs-nodes} ...

    Python utilities for IWFM

    positional arguments:
    {trimesh-animator,head-obs-nodes}
                            sub-command help
        trimesh-animator    start trimesh animator
        head-obs-nodes      start groundwater heads observations vs nodes plotter

    optional arguments:
    -h, --help            show this help message and exit
    -V, --version         Show the conda-prefix-replacement version number and
                            exit.


Trimesh Animator
................

Trimesh Animator displays the groundwater head elevations/depths on a map

::

    pyiwfm trimesh-animator --help
    usage: pyiwfm trimesh-animator [-h] --elements-file ELEMENTS_FILE --nodes-file
                                NODES_FILE --strat-file STRAT_FILE --head-file
                                HEAD_FILE

    optional arguments:
    -h, --help            show this help message and exit
    --elements-file ELEMENTS_FILE
                            path to elements.dat file
    --nodes-file NODES_FILE
                            path to nodes.dat file
    --strat-file STRAT_FILE
                            path to stratigraphy.dat file
    --head-file HEAD_FILE
                            path to heads-all.out file

.. image:: docs/images/trimesh-animator-snapshot.jpg

Groundwater Head Observations vs Node Plotter
.............................................

Groundwater Heads Observations vs Node Plotter displays the observation wells as dots on a map
and displays nearby model node heads along with observed values in a plot

The stations.csv and measurements.csv file can be downloaded from `CA DWR's Open Data Site <https://data.cnra.ca.gov/dataset/periodic-groundwater-level-measurements>`_

::

    pyiwfm head-obs-nodes --help
    usage: pyiwfm head-obs-nodes [-h] --elements-file ELEMENTS_FILE --nodes-file
                                NODES_FILE --strat-file STRAT_FILE --head-file
                                HEAD_FILE --stations-file STATIONS_FILE
                                --measurements-file MEASUREMENTS_FILE

    optional arguments:
    -h, --help            show this help message and exit
    --elements-file ELEMENTS_FILE
                            path to elements.dat file
    --nodes-file NODES_FILE
                            path to nodes.dat file
    --strat-file STRAT_FILE
                            path to stratigraphy.dat file
    --head-file HEAD_FILE
                            path to heads-all.out file
    --stations-file STATIONS_FILE
                            path to groundwater periodic stations file
    --measurements-file MEASUREMENTS_FILE
                            path to groundwater periodic measurements file

.. image:: docs/images/head-obs-nodes-snapshot.jpg

Groundwater head at nodes
.........................

The nodes are displayed as dots on the map and click on them shows a plot of the head

**Use Shift + Mouse Clicks to select multiple nodes and overlay their groundwater heads**

::

    pyiwfm head-nodes -h
    usage: pyiwfm head-nodes [-h] --elements-file ELEMENTS_FILE --nodes-file NODES_FILE --strat-file STRAT_FILE --head-file
                            HEAD_FILE

    optional arguments:
    -h, --help            show this help message and exit
    --elements-file ELEMENTS_FILE
                            path to elements.dat file
    --nodes-file NODES_FILE
                            path to nodes.dat file
    --strat-file STRAT_FILE
                            path to stratigraphy.dat file
    --head-file HEAD_FILE
                            path to heads-all.out file

.. image:: docs/images/head-nodes-snapshot.jpg


Nodes GIS Map and Export
........................

Display nodes on map and export to shapefiles

::

    pyiwfm nodes-gis -h
    usage: pyiwfm nodes-gis [-h] --nodes-file NODES_FILE [-o OUTPUT_DIR]

    optional arguments:
    -h, --help            show this help message and exit
    --nodes-file NODES_FILE
                            path to nodes.dat file
    -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            output directory to write out shapefile information

.. image:: docs/images/nodes-gis-snapshot.jpg


Elements GIS Map and Export
...........................

Display elements on map and export to shapefile

::

    pyiwfm elements-gis -h
    usage: pyiwfm elements-gis [-h] --nodes-file NODES_FILE --elements-file ELEMENTS_FILE [-o OUTPUT_DIR]

    optional arguments:
    -h, --help            show this help message and exit
    --nodes-file NODES_FILE
                            path to nodes.dat file
    --elements-file ELEMENTS_FILE
                            path to nodes.dat file
    -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            output directory to write out shapefile information

.. image:: docs/images/elements-gis-snapshot.jpg
