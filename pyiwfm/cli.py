from argparse import ArgumentParser
from pyiwfm import __version__


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


def cli(args=None):
    p = ArgumentParser(
        description="Python utilities for IWFM",
        conflict_handler='resolve'
    )
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
    # add gwh obs node command
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
    #
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
    # Now call the appropriate response.
    pargs = p.parse_args(args)
    pargs.func(pargs)
    return 

if __name__ == '__main__':
    import sys
    cli(sys.argv[1:])
