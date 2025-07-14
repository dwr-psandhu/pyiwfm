try:
    from ._version import version as __version__
except ImportError:
    # If running from source without setuptools_scm installed
    __version__ = "0.0.1+unknown"

from .reader import read_elements, read_gwhead, read_hydrograph, read_nodes, read_stratigraphy, load_data, load_gwh, load_gwh_feather, read_and_cache
from .obsreader import load_obs_stations, load_and_merge_observations, load_calib_stations, load_calib_measurements, load_gwheads, load_obs_measurements
from .gwh_obs_interpolater import interpolate_observations_to_mesh, cache_obs_interpolation_feather, load_obs_interpolation_feather, visualize_interpolated_results
