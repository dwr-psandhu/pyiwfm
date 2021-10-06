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

```
conda config --set channel_priority strict
conda env create -f environment.yml
```

The above command ensures that strict channel priority is used when creating the environment.
The environment will be named env_iwfm by default and will contain all the dependencies needed. 

Finally, clone this directory and change directory to it and install it as follows

```
pip install -e .
```

