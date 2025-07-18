#%% 
print('This example shows how to use the pyiwfm library to create an animated visualization of groundwater head observations using a trimesh animator.')
#%%
import holoviews as hv
hv.extension('bokeh')
import pyiwfm
from pyiwfm import gwh_obs_interpolater, trimesh_animator
import panel as pn
pn.extension()

fg_dir = 'D:/gw/studies/c2vsimfg_v1.5_model'
elements_file=fg_dir + '/Preprocessor/C2VSimFG_Elements.dat'
nodes_file=fg_dir + '/Preprocessor/C2VSimFG_Nodes.dat'
strat_file=fg_dir + '/Preprocessor/C2VSimFG_Stratigraphy.dat'
obs_feather_file = 'D:/gw/pyiwfm/tests/data/gwdata/periodic_gwl.2025.07/interpolated.finegrid.GSE.feather'
#%%
animobs = gwh_obs_interpolater.build_gwh_animator(elements_file, nodes_file, strat_file, obs_feather_file, title='Groundwater Periodic Observed Levels')

#%%
# Create the panel once
panel = trimesh_animator.build_panel(animobs)

# Now serve the already created panel
pn.serve(panel, show=True, title='Groundwater Periodic Observed Levels')

# You can still modify parameters of animobs and they will affect the panel
# animobs.color_range = (0, 200)

# %%
