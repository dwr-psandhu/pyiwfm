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

Miniconda_ is required. After installing

::

    conda config --set channel_priority strict
    conda env create -f environment.yml


The above command ensures that strict channel priority is used when creating the environment.
The environment will be named env_iwfm by default and will contain all the dependencies needed. 

Finally, clone this directory and change directory to it and install it as follows

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


Groundwater Head Observations vs Node Plotter
.............................................

Groundwater Heads Observations vs Node Plotter displays the observation wells as dots on a map
and displays nearby model node heads along with observed values in a plot

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

