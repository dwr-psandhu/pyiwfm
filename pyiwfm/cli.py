from argparse import ArgumentParser
from pyiwfm import __version__
import pyiwfm


def start_trimesh_animator(args):
    print('starting trimesh animator: ', args.elements_file)
    from pyiwfm import trimesh_animator
    gwa = trimesh_animator.build_gwh_animator(
        args.elements_file, args.nodes_file, args.strat_file, args.head_file)
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


def start_gwh_nodes(args):
    print('starting ground water head nodes viewer')
    from pyiwfm import gwh_tsplotter
    plt = gwh_tsplotter.build_dashboard(
        args.elements_file, args.nodes_file, args.strat_file, args.head_file)
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
    parser_gwh_nodes.set_defaults(func=start_gwh_nodes)
    # nodes-gis
    parser_nodes_gis = sub_p.add_parser(
        'nodes-gis', help='plot nodes on a map & save to gis shapefile information')
    parser_nodes_gis.add_argument('--nodes-file', type=str, required=True,
                                 help='path to nodes.dat file')
    parser_nodes_gis.add_argument('-o', '--output-dir', type=str,
                                  help='output directory to write out shapefile information')
    parser_nodes_gis.set_defaults(func=start_nodes_gis)
    # Now call the appropriate response.
    pargs = p.parse_args(args)
    pargs.func(pargs)
    return


if __name__ == '__main__':
    import sys
    cli(sys.argv[1:])
