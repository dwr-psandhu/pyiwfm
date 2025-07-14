from pyiwfm import gwh_tsplotter
elements_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat"
nodes_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat"
strat_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat"
head_file="tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out"
plt = gwh_tsplotter.build_dashboard(
    elements_file, nodes_file, strat_file,
    head_file, gwh_file_base=head_file_base)
gpane = gwh_tsplotter.build_gwh_ts_pane(plt)
#gpane.servable(title="Groundwater Head @ Nodes: Fine Grid v1.0")