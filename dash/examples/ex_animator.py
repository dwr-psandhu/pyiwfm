#%%
from pyiwfm import trimesh_animator
study_dir1 = "../tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG"
study_dir2 = "..tests/data/c2vsimcg_v1.0_runs/C2VSimCG_WY1974-2015_v1.0"

from pyiwfm import trimesh_animator
animator = trimesh_animator.build_gwh_animator(
    f'{study_dir1}/Preprocessor/C2VSimCG_Elements.dat',
    f'{study_dir1}/Preprocessor/C2VSimCG_Nodes.dat',
    f'{study_dir1}/Preprocessor/C2VSimCG_Stratigraphy.dat',
    f'{study_dir1}/Results/C2VSimCG_GW_HeadAll.out')
# %%
elements_file1 = f'{study_dir1}/Preprocessor/C2VSimCG_Elements.dat'
nodes_file1 = f'{study_dir1}/Preprocessor/C2VSimCG_Nodes.dat'
strat_file1 = f'{study_dir1}/Preprocessor/C2VSimCG_Stratigraphy.dat'
head_file1 = f'{study_dir1}/Results/C2VSimCG_GW_HeadAll.out'
# %%
