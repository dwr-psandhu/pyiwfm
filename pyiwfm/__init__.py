from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

#
from .reader import read_elements, read_gwhead, read_hydrograph, read_nodes, read_stratigraphy, load_data, load_gwh, load_gwh_feather, read_and_cache

