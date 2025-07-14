print('starting ground water head observations vs nodes comparator')
from pyiwfm import gwh_obs_tsplotter
elements_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat'
nodes_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat'
strat_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat'
head_file='tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out'
stations_file='tests/data/gwdata/periodic_gwl/stations.csv'
measurements_file='tests/data/gwdata/periodic_gwl/measurements.csv'
gpane = gwh_obs_tsplotter.build_dashboard(
    elements_file, nodes_file, strat_file, head_file,
    stations_file, measurements_file, distance=1000)
#gpane.servable(title='Groundwater Head Observations vs Fine Grid v1.0 Model @ Nodes')