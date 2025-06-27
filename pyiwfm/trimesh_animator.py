# trimesh animator
import bisect
import math
import os

import cartopy.crs as ccrs
import colorcet as cc
import dask.dataframe as dd
import datashader as ds
import holoviews as hv
import holoviews.operation.datashader as hd
import numpy as np
import pandas as pd
import panel as pn
import param
import requests
import spatialpandas as sp
import spatialpandas.dask
import spatialpandas.geometry
import spatialpandas.io
from dask.diagnostics import ProgressBar
from holoviews import opts, streams
from holoviews.plotting.util import process_cmap
from PIL import Image

import pyiwfm

hv.extension('bokeh')
pn.extension()
#
# from holoviews.util.transform import lon_lat_to_easting_northing as ll2en # only in holoviews 1.14 which breaks this code


def convertxy(df, src_crs='26910', target_crs='3857'):
    epsgsrc = ccrs.epsg(src_crs)
    epsgtgt = ccrs.epsg(target_crs)
    xyz = epsgtgt.transform_points(epsgsrc, df.x.values, df.y.values, None)
    dfm = df.copy()
    dfm.x = xyz[:, 0]
    dfm.y = xyz[:, 1]
    return dfm
#


def build_trimesh_simplex(dfe):
    if len(dfe.columns) == 5:
        dfe = dfe.drop(['5'], axis=1)
    dfq = dfe[dfe['4'] != 0]

    dftri1 = dfq[['1', '2', '3']]
    dftri1.columns = ['v1', 'v2', 'v3']
    dftri2 = dfq[['3', '4', '1']]
    dftri2.columns = ['v1', 'v2', 'v3']

    dftri = dfe[dfe['4'] == 0]
    dftri = dftri.drop(['4'], axis=1)
    dftri.columns = ['v1', 'v2', 'v3']

    dftri = pd.concat([dftri, dftri1, dftri2], axis=0, ignore_index=True)
    # adjust trimesh simplices by -1 to adjust from 1-based to 0-based
    dftri = dftri - 1
    return dftri

# https://stackoverflow.com/questions/361681/algorithm-for-nice-grid-line-intervals-on-a-graph


def best_tick(largest, mostticks):
    minimum = largest / mostticks
    magnitude = 10 ** math.floor(math.log(minimum, 10))
    residual = minimum / magnitude
    # this table must begin with 1 and end with 10
    table = [1, 1.5, 2, 3, 5, 7, 10]
    tick = table[bisect.bisect_right(table, residual)] if residual < 10 else 10
    return tick * magnitude


def calc_levels(min, max, nlevels=10):
    tick = best_tick(max - min, nlevels)
    return [min + tick * i for i in range(nlevels)]

def calculate_value_at(trimesh,x,y):
    cvs=ds.Canvas(plot_width=3,plot_height=3,x_range=(x-1,x+1),y_range=(y-1,y+1))
    simplices = trimesh.dframe([0, 1, 2])
    verts = trimesh.nodes.dframe([0, 1, 3])
    for c, dtype in zip(simplices.columns[:3], simplices.dtypes):
        if dtype.kind != 'i':
            simplices[c] = simplices[c].astype('int')
    result=cvs.trimesh(verts, simplices, mesh=ds.utils.mesh(verts, simplices), agg=ds.mean('z'))
    return result.sel(x=x,y=y).values.tolist()

class GWHeadAnimator(param.Parameterized):
    # layer = param.Integer(default=1, bounds=(1,4))
    # year = param.ObjectSelector(default='',objects=['']) # will be set in constructor
    #depth = param.Boolean(default=True, doc='If true then show depth values else show level (referenced to a datum)')
    draw_contours = param.Boolean(default=False, doc='Draw contours')
    do_shading = param.Boolean(default=False, doc='Do datashading (holoviz)')
    fix_color_range = param.Boolean(
        default=False, doc='Fix color range to current limits or let it be dynamic')
    color_range = param.Range(default=(-1000., 1000.), doc='Range of Color Bar')

    def __init__(self, dfe, dfn0, dfgwh, dfgse, **kwargs):
        super().__init__(**kwargs)
        self.trimesh = hv.TriMesh((build_trimesh_simplex(dfe), hv.Points(dfn0, vdims='z')))
        self.dfgwh = dfgwh
        self.dfgse = dfgse
        self.layer = 1  # layers are 1-based
        #self.year = pn.widgets.DiscretePlayer(name='Year', options=gwa.dfgwh[0].index.to_list(), value=0, loop_policy='loop')
        #self.depth = pn.widgets.Checkbox(nameme="Depth", default=True)
        # setup parameter based on index
        # self.param.year.objects=list(self.dfgwh[self.layer-1].index)
        # self.year=self.dfgwh[self.layer-1].index[0]
        #
        self.cmap_rainbow = process_cmap("rainbow", provider="colorcet")
        self.tiles = hv.element.tiles.CartoLight().opts(alpha=1.0).opts(responsive=True, min_height=600)
        self.hvopts = {'cmap': self.cmap_rainbow, 'colorbar': True,
                       'tools': ['hover'], 'alpha': 0.5, 'logz': False,
                       'min_width': 900, 'min_height': 700}  # 'clim': (0,100)}
        self.shaded_opts = self.hvopts.copy()
        for key in ['cmap', 'colorbar', 'logz', 'tools']:
            self.shaded_opts.pop(key)
        self.overlay = None
        self.dmap = None

    def keep_zoom(self, x_range, y_range):
        self.startX, self.endX = x_range
        self.startY, self.endY = y_range

    # @param.depends('year','depth')
    def update_mesh(self, year, depth):
        #print('Called update_mesh')
        # set the z values based on args
        if depth:
            self.trimesh.nodes.data.z = self.dfgse['GSE'].values - \
                self.dfgwh[self.layer - 1].loc[year, :].values
        else:
            self.trimesh.nodes.data.z = self.dfgwh[self.layer - 1].loc[year, :].values
        return self.trimesh

    @param.depends('draw_contours', 'do_shading', 'fix_color_range', 'color_range')
    def viewmap(self):
        #print('Called view')
        if self.dmap is None:
            self.dmap = hv.DynamicMap(self.update_mesh, kdims=['year', 'depth'], cache_size=1)
            self.dmap = self.dmap.redim.values(year=self.dfgwh[0].index, depth=[False, True])
        # create mesh and contours
        if self.overlay is None:
            mesh = hd.rasterize(self.dmap, precompute=True, aggregator=ds.mean('z'))
        else:
            mesh = hd.rasterize(self.dmap, precompute=True, aggregator=ds.mean('z'),
                                x_range=(self.startX, self.endX), y_range=(self.startY, self.endY))
        if self.fix_color_range:
            meshx = hd.rasterize(self.trimesh, precompute=True, dynamic=False, aggregator=ds.mean('z'),
                                 x_range=(self.startX, self.endX), y_range=(self.startY, self.endY))
            if 'clim' not in self.hvopts:
                self.color_range = (float(meshx.data['x_y z'].min()),
                                    float(meshx.data['x_y z'].max()))
            self.hvopts['clim'] = self.color_range
        else:
            if 'clim' in self.hvopts:
                self.hvopts.pop('clim')
        mesh = mesh.opts(**self.hvopts)
        self.mesh = mesh
        elements = [self.tiles, mesh]
        if self.do_shading:
            mesh = mesh.opts(alpha=0, colorbar=False)
            shaded_args = {'cmap': self.cmap_rainbow}
            # if 'clim' in self.hvopts:
            #    shaded_args['clim'] = self.hvopts['clim']
            shaded = hd.shade(mesh, **shaded_args).opts(**self.shaded_opts)
            elements.append(shaded)
        if self.draw_contours:
            contour_args = {}
            if 'clim' in self.hvopts:
                vlims = self.hvopts['clim']
                # contour_args['levels']=[vlims[0]+(vlims[1]-vlims[0])/10*i for i in range(11)]
                contour_args['levels'] = calc_levels(vlims[0], vlims[1])
            contours = hv.operation.contours(mesh, **contour_args).opts(**self.hvopts)
            self._contours = contours
            elements.append(contours)
        overlay = hv.Overlay(elements)
        overlay = overlay.collate()
        # ,title=f'{self.year},{self.depth}')
        overlay = overlay.opts(active_tools=['pan', 'wheel_zoom'])
        if self.overlay is None:
            self.startX, self.endX = self.dmap.range('x')
            self.startY, self.endY = self.dmap.range('y')
            self.rangexy = streams.RangeXY(source=self.dmap,
                                           x_range=(self.startX, self.endX), y_range=(self.startY, self.endY))
            self.rangexy.add_subscriber(self.keep_zoom)
            self.overlay = overlay
        else:
            self.overlay = overlay.redim.range(
                x=(self.startX, self.endX), y=(self.startY, self.endY))
        #self.overlay.opts(title='%s Groundwater: %s'%( "Depth to" if self.depth else "Level of", self.year))
        return self.overlay


def build_gwh_animator(elements_file, nodes_file, stratigraphy_file, gw_head_file, gw_head_file_base=None, recache=False):
    # load data from files and convert to map crs
    grid_data = pyiwfm.load_data(elements_file, nodes_file, stratigraphy_file)
    dfgwh = pyiwfm.load_gwh(gw_head_file, grid_data.nlayers, recache=recache)
    if gw_head_file_base:
        dfgwhb = pyiwfm.load_gwh(gw_head_file_base, grid_data.nlayers, recache=recache)
        dfgwh = pyiwfm.reader.diff_heads(dfgwh, dfgwhb)
    dfn0 = convertxy(grid_data.nodes)
    dfgw0 = dfgwh[0]
    dfn0['z'] = dfgw0.iloc[0, :].values
    # make animator
    return GWHeadAnimator(grid_data.elements, dfn0, dfgwh, grid_data.stratigraphy, name='Groundwater Level %s Animator' % ('' if gw_head_file_base == None else 'Difference'))


def build_description_pane():
    return pn.pane.Markdown('''
    # Groundwater levels from IWFM 

    The map below displays the Groundwater depth from surface to layer 1 of IWFM. The values are in units of feet. 

    ## Controls

    ### Draw Contours
    Selecting this option draws contour lines on the map. A legend is added to indicate the isoline levels

    ### Fix Color range
    Selecting this option, calculates the range based on the current viewable values. Values can be manually typed in to the color range field (two values separated by a ",")
    Note: This also fixes the range for contour levels

    ### Datashading (Experimental feature)
    Datashading is a concept to allow proper visualization of overlapping values. A coloring histogram is used which tries to use a binning strategy to display the breaks in the data. The color bar for it would be non-linear and so should not be believed

    ### Time and Depth
    The time is calculated from the data available in the model output file. Currently it is by month.
    Drag the slider or select the slider and then use forward and back arrow keys to step through time

    The depth checkbox allows for toggling between displaying Groundwater depth and Groundwater level (UTM Z10N, NAVD 83)
    ''')


def build_panel(gwa):
    # Define control components for the color controls tab
    col1 = pn.Column(gwa.param.draw_contours, gwa.param.do_shading)
    col2 = pn.Column(gwa.param.fix_color_range, gwa.param.color_range)
    color_controls = pn.Column(
        pn.pane.Markdown("### Color Controls"),
        col1, 
        col2,
        sizing_mode='stretch_width'
    )
    
    # Create description pane for the info tab
    description_pane = pn.Column(
        build_description_pane(),
        sizing_mode='stretch_width'
    )
    
    # Create tabs for sidebar
    sidebar_tabs = pn.Tabs(
        ("Controls", color_controls),
        ("Info", description_pane)
    )
    
    # Define sidebar with tabs
    sidebar = pn.Column(
        sidebar_tabs,
        sizing_mode='stretch_width'
    )
    
    # Define map area that is responsive
    map_pane = pn.Column(gwa.viewmap, sizing_mode='stretch_both')
    
    # Use Vanilla Template
    template = pn.template.VanillaTemplate(
        title="Groundwater Level Animator",
        sidebar=sidebar,
        main=map_pane,
        sidebar_width=350
    )
    
    template.servable()
    return template


def show_animator(edge_file, node_file, gse_file, gw_head_file, recache=False):
    gwa = build_gwh_animator(edge_file, node_file, gse_file, gw_head_file, recache=recache)
    template = build_panel(gwa)
    pn.serve(template)
