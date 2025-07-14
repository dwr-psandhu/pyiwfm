import panel as pn
pn.extension()
import functools
import asyncio

def deferred_load(title="Loading data...", template="vanilla"):
    """
    Decorator that creates a deferred loading wrapper around Panel components.
    Uses pn.state.onload for callback to load data after the page loads.
    
    Args:
        loading_message (str): Message to display during loading
        
    Returns:
        A wrapper function that handles deferred loading
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a loading indicator
            loading_indicator = pn.indicators.LoadingSpinner(
                value=True, 
                color="primary",
                size=50,
                name="Loading..."
            )
            
            main_panel = pn.Column(
                pn.indicators.LoadingSpinner(
                    value=True, color="primary", size=50, name="Loading..."
                )
            )
            sidebar_panel = pn.Column(
                pn.indicators.LoadingSpinner(
                    value=True, color="primary", size=50, name="Loading..."
                )
            )
            template = pn.template.VanillaTemplate(
                title=title,
                sidebar=[sidebar_panel],
                main=[main_panel],
                sidebar_width=450,
                header_color="blue",
                logo="https://sciencetracker.deltacouncil.ca.gov/themes/custom/basic/images/logos/DWR_Logo.png",
            )
            
            # Function to load actual component asynchronously
            def load_component():
                # Get the actual component
                result = func(*args, **kwargs)
                
                # Check if the result is a template (has sidebar and main attributes)
                if hasattr(result, 'sidebar') and hasattr(result, 'main'):
                    # It's a template, replace the sidebar and main content
                    # Clear existing content first
                    main_panel.clear()
                    sidebar_panel.clear()
                    template.title = result.title if hasattr(result, 'title') else "Loaded"
                    # Add objects individually to ensure proper reactivity
                    for obj in result.main:
                        main_panel.append(pn.panel(obj))
                    
                    for obj in result.sidebar:
                        sidebar_panel.append(pn.panel(obj))
                else:
                    # It's a regular panel, replace the content in the result container
                    main_panel.clear()
                    sidebar_panel.clear()
                    main_panel.append(result)
            
            # If using a template, create a template with loading indicators
            # Register the callback to run on page load
            pn.state.onload(load_component)
            return template
        return wrapper
    return decorator


@deferred_load(title="C2VSim Coarse Grid R374 Model")
def trimesh_animator_cg_r374():
    from pyiwfm import trimesh_animator
    elements_file = 'tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVelement.dat'
    nodes_file = 'tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVnode.dat'
    strat_file = 'tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVstrat.dat'
    head_file = 'tests/data/C2VSim_CG_1921IC_R374_rev/Results/CVGWheadall.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file, head_file, gw_head_file_base=None)
    p = trimesh_animator.build_panel(gwa)  # servable pane
    return p

@deferred_load(title="C2VSim Coarse Grid 1227 Model")
def trimesh_animator_cg_1227():
    from pyiwfm import trimesh_animator
    elements_file = 'tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG/Preprocessor/C2VSimCG_Elements.dat'
    nodes_file = 'tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG/Preprocessor/C2VSimCG_Nodes.dat'
    strat_file = 'tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG/Preprocessor/C2VSimCG_Stratigraphy.dat'
    head_file = 'tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG/Results/C2VSimCG_GW_HeadAll.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file, head_file, gw_head_file_base=None)
    p = trimesh_animator.build_panel(gwa)  # servable pane
    return p

@deferred_load(title="C2VSim Coarse Grid v1.5 Model")
def trimesh_animator_cg_15():
    from pyiwfm import trimesh_animator
    elements_file = 'tests/data/c2vsimcg_v1.5_model/Preprocessor/C2VSimCG_Elements.dat'
    nodes_file = 'tests/data/c2vsimcg_v1.5_model/Preprocessor/C2VSimCG_Nodes.dat'
    strat_file = 'tests/data/c2vsimcg_v1.5_model/Preprocessor/C2VSimCG_Stratigraphy.dat'
    head_file = 'tests/data/c2vsimcg_v1.5_model/Results/C2VSimCG_GW_HeadAll.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file, head_file, gw_head_file_base=None)
    p = trimesh_animator.build_panel(gwa)  # servable pane
    return p

@deferred_load(title="C2VSim Fine Grid v1.0 Model")
def trimesh_animator_fg_1():
    from pyiwfm import trimesh_animator
    elements_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat'
    nodes_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat'
    strat_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat'
    head_file='tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file,head_file, gw_head_file_base=None)
    p=trimesh_animator.build_panel(gwa) # servable pane
    return p

@deferred_load(title="C2VSim Fine Grid v1.5 Model")
def trimesh_animator_fg_15():
    from pyiwfm import trimesh_animator
    dir = 'c2vsimfg_v1.5_model'
    elements_file=f'tests/data/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Elements.dat'
    nodes_file=f'tests/data/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Nodes.dat'
    strat_file=f'tests/data/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Stratigraphy.dat'
    head_file=f'tests/data/c2vsimfg_v1.5_model/Results/C2VSimFG_GW_HeadAll.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file,head_file, gw_head_file_base=None)
    p=trimesh_animator.build_panel(gwa) # servable pane
    return p

@deferred_load(title="C2VSim Coarse Grid 1227 vs v1.0 Model Comparison")
def trimesh_dual_animator_cg_1227_vs_1():
    from pyiwfm import trimesh_animator
    study_dir1 = "tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG"
    study_dir2 = "tests/data/c2vsimcg_v1.0_runs/C2VSimCG_WY1974-2015_v1.0"
    
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
    return template

@deferred_load(title="C2VSim Fine Grid v1.5 vs Coarse Grid v2 Model Comparison")
def trimesh_dual_animator_fg_15_cg_v2():

    study_dir1 = "tests/data/c2vsimfg_v1.5_model"
    study_dir2 = "tests/data/c2vsimcg_v1.0_runs/C2VSimCG_WY1974-2015_v1.0"

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
        title1='C2VSimFG v1.5',
        title2='C2VSimCG v1.0',)
    return template

@deferred_load(title="C2VSim Coarse Grid 1227 vs Fine Grid v1.5 Model Comparison")
def trimesh_dual_animator_cg_1227_vs_fg_15():
    from pyiwfm import trimesh_animator
    study_dir1 = "tests/data/20250604_1227par_PstCld_best_pars/C2VSimCG"
    study_dir2 = "tests/data/c2vsimfg_v1.5_model"

    template = trimesh_animator.show_side_by_side_animator(
        f'{study_dir1}/Preprocessor/C2VSimCG_Elements.dat',
        f'{study_dir1}/Preprocessor/C2VSimCG_Nodes.dat',
        f'{study_dir1}/Preprocessor/C2VSimCG_Stratigraphy.dat',
        f'{study_dir1}/Results/C2VSimCG_GW_HeadAll.out',
        f'{study_dir2}/Preprocessor/C2VSimFG_Elements.dat',
        f'{study_dir2}/Preprocessor/C2VSimFG_Nodes.dat',
        f'{study_dir2}/Preprocessor/C2VSimFG_Stratigraphy.dat',
        f'{study_dir2}/Results/C2VSimFG_GW_HeadAll.out',
        title1='20250604_1227par_PstCld_best_pars',
        title2='C2VSimFG v1.5',)
    return template    

@deferred_load(title="C2VSim Fine Grid v1.5 vs Fine Grid v1.0 Model Comparison")
def trimesh_dual_animator_fg_15_vs_fg_v1():
    from pyiwfm import trimesh_animator
    study_dir1 = "tests/data/c2vsimfg_v1.5_model"
    study_dir2 = "tests/data/c2vsimfg_v1_0_publicrelease"

    template = trimesh_animator.show_side_by_side_animator(
        f'{study_dir1}/Preprocessor/C2VSimFG_Elements.dat',
        f'{study_dir1}/Preprocessor/C2VSimFG_Nodes.dat',
        f'{study_dir1}/Preprocessor/C2VSimFG_Stratigraphy.dat',
        f'{study_dir1}/Results/C2VSimFG_GW_HeadAll.out',
        f'{study_dir2}/Preprocessor/C2VSimFG_Elements.dat',
        f'{study_dir2}/Preprocessor/C2VSimFG_Nodes.dat',
        f'{study_dir2}/Preprocessor/C2VSimFG_Stratigraphy.dat',
        f'{study_dir2}/Results/C2VSimFG_GW_HeadAll.out',
        title1='C2VSimFG v1.5',
        title2='C2VSimFG v1.0',)
    return template

@deferred_load(title="C2VSim Fine Grid v1.0 Model with Differences")
def trimesh_animator_fg_diff():
    from pyiwfm import trimesh_animator
    elements_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat'
    nodes_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat'
    strat_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat'
    head_file='tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out'
    gw_head_file_base='tests/data/C2VSimFG-BETA_PublicRelease/Results/C2VSimFG_GW_HeadAll.out'

    gwa = trimesh_animator.build_gwh_animator(
            elements_file, nodes_file, strat_file,head_file, gw_head_file_base)
    p=trimesh_animator.build_panel(gwa) # servable pane
    return p


def head_nodes_fg():
    from pyiwfm import gwh_tsplotter
    elements_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat"
    nodes_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat"
    strat_file="tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat"
    head_file="tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out"
    plt = gwh_tsplotter.build_dashboard(
        elements_file, nodes_file, strat_file,
        head_file, gwh_file_base=None)
    gpane = gwh_tsplotter.build_gwh_ts_pane(plt)
    return pn.Column("# Groundwater Head @ Nodes: Fine Grid v1.0", gpane)

def head_obs_node_fg():
    from pyiwfm import gwh_obs_tsplotter
    elements_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Elements.dat'
    nodes_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Nodes.dat'
    strat_file='tests/data/c2vsimfg_v1_0_publicrelease/Preprocessor/C2VSimFG_Stratigraphy.dat'
    head_file='tests/data/c2vsimfg_v1_0_publicrelease/Results/C2VSimFG_GW_HeadAll.out'
    stations_file='tests/data/gwdata/periodic_gwl/stations.csv'
    measurements_file='tests/data/gwdata/periodic_gwl/measurements.csv'
    gpane = gwh_obs_tsplotter.build_dashboard(
        elements_file, nodes_file, strat_file, head_file,
        stations_file, measurements_file, distance=1000)
    return pn.Column('# Groundwater Head Observations vs Fine Grid v1.0 Model @ Nodes', gpane)

def head_calib_head_obs_nodes_cg():
    elements_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVelement.dat"
    nodes_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVnode.dat"
    strat_file="tests/data/C2VSim_CG_1921IC_R374_rev/Preprocessor/CVstrat.dat"
    head_file="tests/data/C2VSim_CG_1921IC_R374_rev/Results/CVGWheadall.out"
    calib_gdb_file="tests/data/c2vsim_cg_1921ic_r374_gis/C2VSim_CG_1921IC_R374.gdb"

    print('starting groundwater calibration observations vs nodes comparator')
    from pyiwfm import gwh_obs_calib_tsplotter
    gpane = gwh_obs_calib_tsplotter.build_dashboard(elements_file, nodes_file, strat_file, head_file, calib_gdb_file, distance=5000)
    return pn.Column('# Groundwater Calibration Observations vs Nodes: Coarse Grid : 374_rev', gpane) 

pn.serve(
    {
    "animator_cg_1227": trimesh_animator_cg_1227,
    "animator_cg_15": trimesh_animator_cg_15,
    "animator_cg_r374": trimesh_animator_cg_r374,
    "animator_fg_1": trimesh_animator_fg_1,
    "animator_fg_15": trimesh_animator_fg_15,
    "dual_animator_cg_1227_vs_1": trimesh_dual_animator_cg_1227_vs_1,
    "dual_animator_fg_15_cg_v2": trimesh_dual_animator_fg_15_cg_v2,
    "dual_animator_cg_1227_vs_fg_15": trimesh_dual_animator_cg_1227_vs_fg_15,
    "dual_animator_fg_15_vs_fg_v1": trimesh_dual_animator_fg_15_vs_fg_v1,
    "animator_fg_diff":trimesh_animator_fg_diff,
    "head_nodes_fg": head_nodes_fg,
    "head_obs_node_fg": head_obs_node_fg,
    "head_calib_head_obs_nodes_cg": head_calib_head_obs_nodes_cg},
    port=80, address="0.0.0.0", websocket_origin="*",
    websocket_max_message_size=1024*1024*48,
)

