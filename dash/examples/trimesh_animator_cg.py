from pyiwfm import trimesh_animator
elements_file='tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVelement.dat'
nodes_file='tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVnode.dat'
strat_file='tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVstrat.dat'
head_file='tests/data/C2VSim_CG_1921IC_R374_rev/Results/CVGWheadall.out'

gwa = trimesh_animator.build_gwh_animator(
        elements_file, nodes_file, strat_file,head_file, gw_head_file_base=None)
p=trimesh_animator.build_panel(gwa) # servable pane
#p.servable(title='Trimesh Animator for C2VSim Coarse Grid: R374_rev')
