from argparse import ArgumentParser
from pyiwfm import __version__
import pyiwfm


def start_trimesh_animator(args):
    print('starting trimesh animator: ', args.elements_file)
    from pyiwfm import trimesh_animator
    gwa = trimesh_animator.build_gwh_animator(
        args.elements_file, args.nodes_file, args.strat_file,
        args.head_file, gw_head_file_base=args.head_file_base)
    import panel as pn
    pn.extension()
    pn.serve(trimesh_animator.build_panel(gwa))


def start_gwh_obs_nodes(args):
    print('starting ground water head observations vs nodes comparator')
    from pyiwfm import gwh_obs_tsplotter
    gpane = gwh_obs_tsplotter.build_dashboard(
        args.elements_file, args.nodes_file, args.strat_file, args.head_file,
        args.stations_file, args.measurements_file, distance=1000)
    import panel as pn
    pn.extension()
    pn.serve(gpane)


def start_gwh_calib_obs_nodes(args):
    print('starting groundwater calibration observations vs nodes comparator')
    from . import gwh_obs_calib_tsplotter
    gpane = gwh_obs_calib_tsplotter.build_dashboard(args.elements_file, args.nodes_file, args.strat_file,
        args.head_file, args.calib_gdb_file, distance=5000)
    import panel as pn
    pn.extension()
    pn.serve(gpane)


def build_calib_rmse_map(args):
    print('starting calib rmse map')
    from . import gwh_obs_calib_tsplotter
    dfhyd = pyiwfm.read_hydrograph(args.cvprint_file)
    plt = gwh_obs_calib_tsplotter.build_calib_plotter(args.elements_file, args.nodes_file, args.strat_file,
                args.head_file, args.calib_gdb_file)
    rmse_map = gwh_obs_calib_tsplotter.build_rmse_map(plt, dfhyd)
    if args.output_file:
        gwh_obs_calib_tsplotter.save_html(rmse_map, args.output_file)
    import panel as pn
    pn.extension()
    pn.serve(rmse_map)


def start_gwh_nodes(args):
    print('starting ground water head nodes viewer')
    from pyiwfm import gwh_tsplotter
    plt = gwh_tsplotter.build_dashboard(
        args.elements_file, args.nodes_file, args.strat_file,
        args.head_file, gwh_file_base=args.head_file_base)
    gpane = gwh_tsplotter.build_gwh_ts_pane(plt)
    import panel as pn
    pn.extension()
    pn.serve(gpane)


def start_nodes_gis(args):
    print('starting nodes gis viewer')
    import pyiwfm
    import hvplot.pandas
    import pyiwfm.geo
    import panel as pn
    pn.extension()
    nodes = pyiwfm.read_nodes(args.nodes_file)
    nodes['ID'] = nodes.index
    gnodes = pyiwfm.geo.nodes_gdf(nodes)
    node_map = gnodes.hvplot.points(geo=True, crs='EPSG:26910', tiles='CartoLight',
                                hover_cols=['ID', 'Latitude', 'Longitude'],
                                frame_height=500, frame_width=500, fill_alpha=0.3, line_alpha=0.1)
    gpane = pn.Row(gnodes, node_map)

    if args.output_dir:
        print('writing output to ', args.output_dir)
        gnodes.to_file(args.output_dir)

    pn.serve(gpane)


def start_elements_gis(args):
    print('starting elements gis viewer')
    import pyiwfm
    import hvplot.pandas
    import pyiwfm.geo
    import panel as pn
    pn.extension()
    elements = pyiwfm.read_elements(args.elements_file)
    nodes = pyiwfm.read_nodes(args.nodes_file)
    nodes['ID'] = nodes.index
    gel = pyiwfm.geo.elements_gdf(nodes, elements)
    el_map = gel.hvplot.polygons(geo=True, tiles='OSM', crs='EPSG:26910',
                             frame_width=500, frame_height=500,
                             c='5', cmap='Category20',
                             alpha=0.5, line_alpha=0.3, fill_alpha=0.5)
    gpane = pn.Row(gel.head(), el_map)
    if args.output_dir:
        print('writing output to ', args.output_dir)
        gel.to_file(args.output_dir)

    pn.serve(gpane)


def cli(args=None):
    p = ArgumentParser(
        description="Python utilities for IWFM",
        conflict_handler='resolve'
    )
    p.set_defaults(func=lambda args: p.print_help())
    p.add_argument(
        '-V', '--version',
        action='version',
        help='Show the conda-prefix-replacement version number and exit.',
        version="pyiwfm %s" % __version__,
    )

    sub_p = p.add_subparsers(help='sub-command help')
    # add animator command
    parser_animator = sub_p.add_parser('trimesh-animator', help='start trimesh animator')
    parser_animator.add_argument('--elements-file', type=str,
                                 required=True, help='path to elements.dat file')
    parser_animator.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_animator.add_argument('--strat-file', type=str, required=True,
                                 help='path to stratigraphy.dat file')
    parser_animator.add_argument('--head-file', type=str, required=True,
                                 help='path to heads-all.out file')
    parser_animator.add_argument('--head-file-base', type=str, required=False,
                                 help='path to base heads-all.out file to display differences calculated as headfile - headfilebase')
    parser_animator.set_defaults(func=start_trimesh_animator)
    # head-obs-nodes
    parser_gwh_obs_nodes = sub_p.add_parser(
        'head-obs-nodes', help='start groundwater heads observations vs nodes plotter')
    parser_gwh_obs_nodes.add_argument('--elements-file', type=str,
                                 required=True, help='path to elements.dat file')
    parser_gwh_obs_nodes.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_gwh_obs_nodes.add_argument('--strat-file', type=str, required=True,
                                 help='path to stratigraphy.dat file')
    parser_gwh_obs_nodes.add_argument('--head-file', type=str, required=True,
                                 help='path to heads-all.out file')
    parser_gwh_obs_nodes.add_argument(
        '--stations-file', type=str, required=True, help='path to groundwater periodic stations file')
    parser_gwh_obs_nodes.add_argument(
        '--measurements-file', type=str, required=True, help='path to groundwater periodic measurements file')
    parser_gwh_obs_nodes.set_defaults(func=start_gwh_obs_nodes)
    # calib-head-obs-nodes
    parser_calib_gwh_obs_nodes = sub_p.add_parser(
        'calib-head-obs-nodes', help='start calibration groundwater heads observations vs nodes plotter')
    parser_calib_gwh_obs_nodes.add_argument('--elements-file', type=str,
                                 required=True, help='path to elements.dat file')
    parser_calib_gwh_obs_nodes.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_calib_gwh_obs_nodes.add_argument('--strat-file', type=str, required=True,
                                 help='path to stratigraphy.dat file')
    parser_calib_gwh_obs_nodes.add_argument('--head-file', type=str, required=True,
                                 help='path to heads-all.out file')
    parser_calib_gwh_obs_nodes.add_argument('--calib-gdb-file', type=str, required=True,
                                 help='path to gdb file')
    parser_calib_gwh_obs_nodes.set_defaults(func=start_gwh_calib_obs_nodes)
    # calib-rmse-map
    parser_rmse_map = sub_p.add_parser(
        'calib-rmse-map', help='create calibration rmse (root mean squared) map')
    parser_rmse_map.add_argument('--elements-file', type=str,
                                 required=True, help='path to elements.dat file')
    parser_rmse_map.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_rmse_map.add_argument('--strat-file', type=str, required=True,
                                 help='path to stratigraphy.dat file')
    parser_rmse_map.add_argument('--head-file', type=str, required=True,
                                 help='path to heads-all.out file')
    parser_rmse_map.add_argument('--calib-gdb-file', type=str, required=True,
                                 help='path to gdb file')
    parser_rmse_map.add_argument('--cvprint-file', type=str, required=True,
                                 help='path to cvprint file')
    parser_rmse_map.add_argument('--output-file', type=str, required=False,
                                 help='html file to save rmse map to')

    parser_rmse_map.set_defaults(func=build_calib_rmse_map)
    # head-nodes
    parser_gwh_nodes = sub_p.add_parser(
        'head-nodes', help='dashboard to plot groundwater heads at nodes')
    parser_gwh_nodes.add_argument('--elements-file', type=str,
                                 required=True, help='path to elements.dat file')
    parser_gwh_nodes.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_gwh_nodes.add_argument('--strat-file', type=str, required=True,
                                 help='path to stratigraphy.dat file')
    parser_gwh_nodes.add_argument('--head-file', type=str, required=True,
                                 help='path to heads-all.out file')
    parser_gwh_nodes.add_argument('--head-file-base', type=str, required=False,
                                 help='path to heads-all.out file to display differences calculated as headfile - headfilebase')
    parser_gwh_nodes.set_defaults(func=start_gwh_nodes)
    # nodes-gis
    parser_nodes_gis = sub_p.add_parser(
        'nodes-gis', help='plot nodes on a map & save to gis shapefile information')
    parser_nodes_gis.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_nodes_gis.add_argument('-o', '--output-dir', type=str,
                                  help='output directory to write out shapefile information')
    parser_nodes_gis.set_defaults(func=start_nodes_gis)
    # elements-gis
    parser_elements_gis = sub_p.add_parser(
        'elements-gis', help='plot elements on a map & save to gis shapefile information')
    parser_elements_gis.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_elements_gis.add_argument('--elements-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_elements_gis.add_argument('-o', '--output-dir', type=str,
                                  help='output directory to write out shapefile information')
    parser_elements_gis.set_defaults(func=start_elements_gis)
    # Now call the appropriate response.
    pargs = p.parse_args(args)
    pargs.func(pargs)
    return


if __name__ == '__main__':
    import sys
    cli(sys.argv[1:])
