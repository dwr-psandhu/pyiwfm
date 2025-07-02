#%%
study_dir1 = "d:/gw/c2vsimfg_v1.5_model"
study_dir2 = "d:/gw/c2vsimcg_v1.0_runs/C2VSimCG_WY1974-2015_v1.0"

# %%
from pyiwfm import trimesh_animator
template = trimesh_animator.show_side_by_side_animator(
    f'{study_dir1}/Preprocessor/C2VSimFG_Elements.dat',
    f'{study_dir1}/Preprocessor/C2VSimFG_Nodes.dat',
    f'{study_dir1}/Preprocessor/C2VSimFG_Stratigraphy.dat',
    f'{study_dir1}/Results/C2VSimFG_GW_HeadAll.out',
    f'{study_dir2}/Preprocessor/C2VSimCG_Elements.dat',
    f'{study_dir2}/Preprocessor/C2VSimCG_Nodes.dat',
    f'{study_dir2}/Preprocessor/C2VSimCG_Stratigraphy.dat',
    f'{study_dir2}/Results/C2VSimCG_GW_HeadAll.out',
)
# %%
import panel as pn
pn.extension()
pn.serve(template, show=True)

# %%
