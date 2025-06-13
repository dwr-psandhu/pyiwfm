try:
    from ._version import version as __version__
except ImportError:
    # If running from source without setuptools_scm installed
    __version__ = "0.0.1+unknown"

from .reader import read_elements, read_gwhead, read_hydrograph, read_nodes, read_stratigraphy, load_data, load_gwh, load_gwh_feather, read_and_cache

