#%%
study_dir1 = "d:/gw/studies/20250604_1227par_PstCld_best_pars/C2VSimCG"
study_dir2 = "d:/gw/studies/c2vsimcg_v1.0_runs/C2VSimCG_WY1974-2015_v1.0"

# %%
from pyiwfm import trimesh_animator
template = trimesh_animator.show_side_by_side_animator(
    f'{study_dir1}/Preprocessor/C2VSimCG_Elements.dat',
    f'{study_dir1}/Preprocessor/C2VSimCG_Nodes.dat',
    f'{study_dir1}/Preprocessor/C2VSimCG_Stratigraphy.dat',
    f'{study_dir1}/Results/C2VSimCG_GW_HeadAll.out',
    f'{study_dir2}/Preprocessor/C2VSimCG_Elements.dat',
    f'{study_dir2}/Preprocessor/C2VSimCG_Nodes.dat',
    f'{study_dir2}/Preprocessor/C2VSimCG_Stratigraphy.dat',
    f'{study_dir2}/Results/C2VSimCG_GW_HeadAll.out',
    title1='20250604_1227par_PstCld_best_pars',
    title2='C2VSimCG_WY1974-2015_v1.0',
)
# %%
import panel as pn
pn.extension()
pn.serve(template, show=True)

# %%
