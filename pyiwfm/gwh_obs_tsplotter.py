import geopandas as gpd
# imports for visuzalization
import holoviews as hv
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import param
# imports for geometry
import shapely
from holoviews import opts

import pyiwfm

pn.extension()


def ensure_version(verstr, min_ver):
    '''Ensure minimum version of package'''
    major, minor, patch = str.split(verstr, '.')
    min_major, min_minor, min_patch = str.split(min_ver, '.')
    assert(major) >= min_major
    if major == min_major:
        assert(minor) >= min_minor


#ensure_version(gpd.__version__, '0.8.1')  # crs doesn't work correctly before this


def get_points_within(gnodes, gdfs, distance=5000):
    buffer = gdfs.to_crs(gnodes.crs).geometry.buffer(distance)
    buf_polygon = buffer.values[0]
    return gnodes[gnodes.within(buf_polygon)]


def get_gwh_at_nodes(nodeids, gwh, layer=0):
    ids = [str(nid) for nid in nodeids]
    return gwh[layer].loc[:, ids]


def get_gw_depth_at_nodes(nodeids, gwh, strat, layer=0):
    dfheads = get_gwh_at_nodes(nodeids, gwh, layer)
    return strat.loc[nodeids, 'GSE'].values.T-dfheads


def load_and_merge_observations(gdfs, file):
    dfobs = pd.read_csv(file)
    return dfobs.join(gdfs, on='STN_ID', rsuffix='OBS_')


def get_obs_for_stn_id(dfobs, stn_id):
    dfx = dfobs[dfobs['STN_ID'] == stn_id].copy()
    dfx.index = pd.to_datetime(dfx['MSMT_DATE'])
    return dfx


class Plotter(param.Parameterized):
    depth = param.Boolean(doc='Depth to Groundwater = GSE - Level (layer 1)')
    layer = param.ObjectSelector(objects={'1': 0, '2': 1, '3': 2, '4': 3}, default=0)
    distance = param.Number(default=5000, bounds=(0, 10000))
    selected = param.List(default=[0], doc='Selected node indices to display in plot')

    def __init__(self, elements_file, nodes_file, stratigraphy_file, gwh_file, stations_file, measurements_file, **kwargs):
        super().__init__(**kwargs)
        self.grid_data = pyiwfm.load_data(elements_file, nodes_file, stratigraphy_file)
        self.gwh = pyiwfm.read_and_cache(gwh_file, self.grid_data.nlayers)
        self.gnodes = gpd.GeoDataFrame(self.grid_data.nodes.copy(), geometry=[
            shapely.geometry.Point(v) for v in self.grid_data.nodes.values], crs='EPSG:26910')
        self.stations = self.load_obs_stations(stations_file)
        self.measurements = load_and_merge_observations(self.stations, measurements_file)

        self.node_map = self.stations.hvplot.points(geo=True, tiles='CartoLight',  # c='WELL_TYPE',
                                                    frame_height=400, frame_width=300,
                                                    fill_alpha=0.9, line_alpha=0.4,
                                                    hover_cols=['index'])
        self.node_map = self.node_map.opts(opts.Points(tools=['tap', 'hover'], size=5,
                                                       nonselection_color='red', nonselection_alpha=0.6,
                                                       active_tools=['wheel_zoom']))
        # create a selection and add it to a dynamic map calling back show_ts
        self.select_stream = hv.streams.Selection1D(source=self.node_map, index=[0])
        self.select_stream.add_subscriber(self.set_selected)

    def set_selected(self, index):
        if index is None or len(index) == 0:
            pass  # keep the previous selections
        else:
            self.selected = index

    def load_obs_stations(self, stations_file):
        dfs = pd.read_csv(stations_file)
        # Filtering out null well names. Probably don't have data? Found out more later
        dfs = dfs[~dfs['WELL_NAME'].isna()]
        gdfs = gpd.GeoDataFrame(dfs,
                                geometry=gpd.points_from_xy(dfs['LONGITUDE'], dfs['LATITUDE']),
                                crs='EPSG:4326')
        return gdfs

    @param.depends('depth', 'layer', 'distance', 'selected')
    def show_ts(self):
        index = self.selected
        if index is None or len(index) == 0:
            index = self.selected
        # Use only the first index in the array
        first_index = index[0]
        dfselected = self.stations.iloc[first_index, :]
        stn_id = dfselected['STN_ID']
        # FIX inefficiency below (need to carry crs onto gdfs slice)
        pts_within = get_points_within(
            self.gnodes, self.stations[self.stations['STN_ID'] == stn_id], distance=self.distance)
        nodeids = pts_within.index.values
        dfstn = get_obs_for_stn_id(self.measurements, stn_id)
        if self.depth:
            model_data = get_gw_depth_at_nodes(
                nodeids, self.gwh, self.grid_data.stratigraphy, self.layer)
            obs_data = dfstn[['GSE_WSE']]
        else:
            model_data = get_gwh_at_nodes(nodeids, self.gwh, self.layer)
            obs_data = dfstn[['WSE']]
        obs_data.index.name = 'Time'
        model_curves = [hv.Curve(model_data.iloc[:, i], group='Model', label=c)
                        for i, c in enumerate(model_data.columns)]
        model_curves.insert(0, hv.Curve(obs_data, group='Observed',
                                        label='Observation [%s]' % dfselected['WELL_NAME']).opts(line_dash='dotted'))
        overlay = hv.Overlay(model_curves).opts(width=600, legend_position='top', legend_cols=True)
        return overlay.opts(title='Groundwater (Model vs Obs) %s (Layer %s)' % ('Depth' if self.depth else 'Level', self.layer+1))


def build_panel(plt, distance):
    plt.distance = distance
    gs = pn.GridSpec(sizing_mode='scale_both')
    gs[0:6, 0:5] = pn.Row(plt.node_map)
    gs[0:1, 5:6] = pn.Column(plt.param.depth, plt.param.layer, plt.param.distance)
    gs[1:6, 5:8] = pn.Row(plt.show_ts)
    gs.servable(title='Groundwater Model vs Periodic Measurements')
    return gs


def build_dashboard(element_file, node_file, strat_file, gwh_file, stations_file, measurements_file, distance=5000):
    plt = Plotter(element_file, node_file, strat_file, gwh_file, stations_file, measurements_file)
    gpane = build_panel(plt, distance)
    return gpane
