#%%
import pyiwfm
from pyiwfm import gwh_obs_interpolater
cg_dir = "d:/gw/studies/20250604_1227par_PstCld_best_pars/C2VSimCG"
elements_file = f'{cg_dir}/Preprocessor/C2VSimCG_Elements.dat'
nodes_file = f'{cg_dir}/Preprocessor/C2VSimCG_Nodes.dat'
strat_file = f'{cg_dir}/Preprocessor/C2VSimCG_Stratigraphy.dat'
head_file = f'{cg_dir}/Results/C2VSimCG_GW_HeadAll.out'
gwdata = 'D:/gw/studies/gwdata/periodic_gwl.2025.07'
obs_feather_file = gwdata + '/interpolated.coarsegrid.GSE.feather'
#%%
anim_obs = gwh_obs_interpolater.build_gwh_animator(elements_file, nodes_file, strat_file, obs_feather_file, title='Groundwater Periodic')
#%%
from pyiwfm import trimesh_animator
anim_model = trimesh_animator.build_gwh_animator(
    elements_file, nodes_file, strat_file, head_file, title='Groundwater c2vsimcg_1227par')
# %%
template = trimesh_animator.build_side_by_side_animator_panel(
    anim_obs, anim_model, title='Groundwater Level Animator Side by Side')
#%%
import panel as pn
pn.extension()
pn.serve(template, show=True, title='Groundwater Level Animator Side by Side')
# %%
#template.main.save('c2vsimcg_1227par_vs_obs_anim.html', embed=True)
# %%
