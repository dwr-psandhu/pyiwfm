#%%
import pyiwfm
from pyiwfm import gwh_obs_interpolater
fg_dir = 'D:/gw/studies/c2vsimfg_v1.5_model'
elements_file=fg_dir + '/Preprocessor/C2VSimFG_Elements.dat'
nodes_file=fg_dir + '/Preprocessor/C2VSimFG_Nodes.dat'
strat_file=fg_dir + '/Preprocessor/C2VSimFG_Stratigraphy.dat'
head_file=fg_dir + '/Results/C2VSimFG_GW_HeadAll.out'
gwdata = 'D:/gw/studies/gwdata/periodic_gwl.2025.07'
output_file = gwdata + '/interpolated.finegrid.GSE.feather'
#%%
obs_feather_file = 'observed_heads_1973_2021.feather'
animobs = gwh_obs_interpolater.build_gwh_animator(elements_file, nodes_file, strat_file, obs_feather_file, title='Groundwater Periodic')
#%%
from pyiwfm import trimesh_animator
animfg = trimesh_animator.build_gwh_animator(
    elements_file, nodes_file, strat_file, head_file, title='Groundwater c2vsimfg_v1.5')
# %%
template = trimesh_animator.build_side_by_side_animator_panel(
    animobs, animfg, title='Groundwater Level Animator Side by Side')
#%%
import panel as pn
pn.extension()
pn.serve(template, show=True, title='Groundwater Level Animator Side by Side')
# %%
#template.main.save('c2vsimfg_vs_obs_anim.html', embed=True)
# %%
