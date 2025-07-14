from pyiwfm import trimesh_animator
elements_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat'
nodes_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat'
strat_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat'
head_file='tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out'

gwa = trimesh_animator.build_gwh_animator(
        elements_file, nodes_file, strat_file,head_file, gw_head_file_base=None)
p=trimesh_animator.build_panel(gwa) # servable pane
#p.servable(title='Trimesh Animator for C2VSim Finegrid: v1.0 public release')
