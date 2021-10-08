import geopandas as gpd
# imports for visuzalization
import holoviews as hv
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
from panel.layout import grid
import param
# imports for geometry
import shapely
from holoviews import opts

import pyiwfm
import pyiwfm.geo

pn.extension()


def ensure_version(verstr, min_ver):
    '''Ensure minimum version of package'''
    major, minor, patch = str.split(verstr, '.')
    min_major, min_minor, min_patch = str.split(min_ver, '.')
    assert(major) >= min_major
    if major == min_major:
        assert(minor) >= min_minor


ensure_version(gpd.__version__, '0.8.1')  # crs doesn't work correctly before this


def get_points_within(gnodes, gdfs, distance=5000):
    from . import gwh_obs_tsplotter
    return gwh_obs_tsplotter.get_points_within(gnodes, gdfs, distance)


def get_gwh_at_nodes(nodeids, gwh, layer=0):
    from . import gwh_obs_tsplotter
    return gwh_obs_tsplotter.get_gwh_at_nodes(nodeids, gwh, layer)


def get_obs_for_id(dfobs, stn_id):
    dfx = dfobs[dfobs['Calibration_ID'] == stn_id].copy()
    dfx.index = pd.to_datetime(dfx['Date_'])
    return dfx


def get_model_obs_data_for_sid(gnodes, gwh, stations, measurements, sid=1, distance=5000, layer=0):
    pts_within = get_points_within(gnodes,
                                   stations[stations['Calibration_ID'] == sid],
                                   distance=distance)
    nodeids = pts_within.index.values
    dfstn = get_obs_for_id(measurements, sid)
    model_data = get_gwh_at_nodes(nodeids, gwh, layer=layer)
    obs_data = dfstn[['Value_']]
    obs_data.index.name = 'Time'
    return model_data, obs_data


def get_model_interpolated_obs_data_for_sid(gelements, gwh, stations, measurements, sid=1, layer=0):
    dfstn = get_obs_for_id(measurements, sid)
    model_data = get_model_interpolated_data_for_sid(gelements, gwh, stations, sid, layer=layer)
    obs_data = dfstn[['Value_']]
    obs_data.index.name = 'Time'
    return model_data, obs_data


def get_model_interpolated_data_for_sid(gelements, gwh, stations, sid, layer=0):
    station_selected = stations[stations['Calibration_ID'] == sid]
    station_geometry = station_selected.geometry.values[0]
    xp, yp = station_geometry.coords.xy
    xp, yp = xp[0], yp[0]
    gel = gelements[gelements.contains(station_geometry)]
    poly_containing = gel.geometry.values[0]
    npts = len(poly_containing.exterior.coords) - 1
    nodes_list = gel.iloc[0, 0:npts].astype('str').to_list()
    node_heads = gwh[layer].loc[:, nodes_list]
    x, y = poly_containing.exterior.coords.xy
    x, y = x[:-1], y[:-1]
    coeffs = pyiwfm.geo.interp(xp, yp, x, y)
    head_weighted = node_heads * coeffs
    head_xy = head_weighted.sum(axis=1)
    return head_xy


def calculate_model_metric(gelements, gwh, stations, measurements, dfhyd):
    rmse_arr = []
    for sid in stations['Calibration_ID']:
        layer = dfhyd[dfhyd['Calibration_ID'] == 3]['iouthl'].values[0] - 1
        model_data, obs_data = get_model_interpolated_obs_data_for_sid(
            gelements, gwh, stations, measurements, sid, layer)
        model_data_interp = model_data.resample('D').interpolate()
        dfall = pd.concat([model_data_interp, obs_data], axis=1).dropna()
        dfdiff = dfall.iloc[:, :-1].subtract(dfall.iloc[:, -1], axis=0)
        rmse = np.mean((dfdiff**2).mean()**0.5)
        rmse_arr.append(rmse)
    return rmse_arr


class CalibPlotter(param.Parameterized):
    layer = param.ObjectSelector(objects={'1': 0, '2': 1, '3': 2, '4': 3}, default=0)
    distance = param.Number(default=5000, bounds=(0, 10000))
    selected = param.List(default=[0], doc='Selected node indices to display in plot')

    def __init__(self, grid_data, gwh, stations, measurements, **kwargs):
        super().__init__(**kwargs)
        self.grid_data = grid_data
        self.gwh = gwh
        self.gnodes = gpd.GeoDataFrame(self.grid_data.nodes.copy(), geometry=[
            shapely.geometry.Point(v) for v in self.grid_data.nodes.values], crs='EPSG:26910')
        self.stations = stations
        self.measurements = measurements

        self.node_map = self.stations.hvplot.points(geo=True, tiles='CartoLight',  # c='WELL_TYPE',
                                                    frame_height=400, frame_width=300,
                                                    crs='EPSG:26910',
                                                    fill_alpha=0.9, line_alpha=0.4,
                                                    hover_cols=['index'])
        self.node_map = self.node_map.opts(opts.Points(tools=['tap', 'hover'], size=8,
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

    @param.depends('layer', 'distance', 'selected')
    def show_ts(self):
        index = self.selected
        if index is None or len(index) == 0:
            index = self.selected
        # Use only the first index in the array
        first_index = index[0]
        dfselected = self.stations.iloc[first_index, :]
        stn_id = dfselected['Calibration_ID']
        # FIX inefficiency below (need to carry crs onto gdfs slice)
        pts_within = get_points_within(
            self.gnodes, self.stations[self.stations['Calibration_ID'] == stn_id], distance=self.distance)
        nodeids = pts_within.index.values
        dfstn = get_obs_for_id(self.measurements, stn_id)
        model_data = get_gwh_at_nodes(nodeids, self.gwh, self.layer)
        obs_data = dfstn[['Value_']]
        obs_data.index.name = 'Time'
        model_curves = [hv.Curve(model_data.iloc[:, i], group='Model', label=c)
                        for i, c in enumerate(model_data.columns)]
        model_curves.insert(0, hv.Curve(obs_data, group='Observed',
                                        label='Observation [%s]' % dfselected['Calibration_ID']).opts(line_dash='dotted'))
        overlay = hv.Overlay(model_curves).opts(width=600, legend_position='top', legend_cols=True)
        return overlay.opts(title='Groundwater (Model vs Calibration Wells) %s (Layer %s)' % ('Level', self.layer + 1))


def build_panel(plt, distance):
    plt.distance = distance
    gs = pn.GridSpec(sizing_mode='scale_both')
    gs[0:6, 0:5] = pn.Row(plt.node_map)
    gs[0:1, 5:6] = pn.Column(plt.param.layer, plt.param.distance)
    gs[1:6, 5:8] = pn.Row(plt.show_ts)
    gs.servable(title='Groundwater Model vs Calibration Well Measurements')
    return gs


def build_calib_plotter(elements_file, nodes_file, stratigraphy_file, gwh_file, calib_gdb_file):
    from . import obsreader, reader
    grid_data = reader.load_data(elements_file, nodes_file, stratigraphy_file)
    gwh = reader.load_gwh(gwh_file, grid_data.nlayers)
    stations = obsreader.load_calib_stations(calib_gdb_file)
    measurements = obsreader.load_calib_measurements(calib_gdb_file)
    plt = CalibPlotter(grid_data, gwh, stations, measurements)
    return plt


def build_dashboard(element_file, node_file, strat_file, gwh_file, calib_gdb_file, distance=5000):
    plt = build_calib_plotter(element_file, node_file, strat_file, gwh_file, calib_gdb_file)
    gpane = build_panel(plt, distance)
    return gpane


def build_rmse_map(plt, dfhyd):
    gelements = pyiwfm.geo.elements_gdf(plt.grid_data.nodes, plt.grid_data.elements)
    rmse_arr = calculate_model_metric(
        gelements, plt.gwh, plt.stations, plt.measurements, dfhyd)
    plt.stations['rmse'] = rmse_arr
    rmse_map = plt.stations.hvplot(geo=True, crs='EPSG:26910', c='rmse',
                                   s=50, alpha=0.6, cmap='rainbow', clim=(0, 100)).opts(frame_height=500, frame_width=400)

    desc = pn.pane.Markdown('''#### Root Mean Squared Error (RMSE) Map
    The map depicts RMSE calculated as the difference between calibration well level 
    and the interpolated (triangular/quad) value from the element the station is within.
    
    The layer from the model to compare with observed is chosen from CVPrint.dat

    The color bar on the right is limited from 0 (no error) to a maximum of 100 feet ''')
    row = pn.Row(hv.element.tiles.CartoLight() * rmse_map)
    rmse_map_panel = pn.Column(desc, row)
    return rmse_map_panel


def save_html(map_panel, fname):
    from bokeh.resources import INLINE
    map_panel.save(fname, resources=INLINE)


def build_element_map(plt):
    elgeo = pyiwfm.geo.elements_gdf(plt.nodes, plt.elements)
    el_map = elgeo.hvplot.polygons(geo=True, tiles='CartoLight', crs='EPSG:26910',
                                   frame_width=500, frame_height=500,
                                   c='5', cmap='Category20',  # no 5th column info here
                                   alpha=0.5, line_alpha=0.3, fill_alpha=0.5, hover_cols=['index'])\
        .opts(opts.Points(active_tools=['wheel_zoom']))
    return el_map
