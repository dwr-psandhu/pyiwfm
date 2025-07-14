#python -m pyiwfm calib-head-obs-nodes --elements-file tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVelement.dat --nodes-file tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVnode.dat --strat-file tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVstrat.dat --head-file tests/data/C2VSim_CG_1921IC_R374_rev/Results/CVGWheadall.out --calib-gdb-file tests/data/c2vsim_cg_1921ic_r374_gis/C2VSim_CG_1921IC_R374.gdb 

elements_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVelement.dat"
nodes_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVnode.dat"
strat_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVstrat.dat"
head_file="tests/data/C2VSim_CG_1921IC_R374_rev/Results/CVGWheadall.out"
calib_gdb_file="tests/data/c2vsim_cg_1921ic_r374_gis/C2VSim_CG_1921IC_R374.gdb"

print('starting groundwater calibration observations vs nodes comparator')
from pyiwfm import gwh_obs_calib_tsplotter
gpane = gwh_obs_calib_tsplotter.build_dashboard(elements_file, nodes_file, strat_file, head_file, calib_gdb_file, distance=5000)
#gpane.servable('Groundwater Calibration Observations vs Nodes: Coarse Grid : 374_rev') # this gives two panes to be served. need to pass this into build_dashboard