# Display Groundwater level/depth for selected node
import pyiwfm
import param
import pandas as pd
import numpy as np
# imports for geometry
import shapely
import geopandas as gpd

# imports for visuzalization
import holoviews as hv
from holoviews import opts
import hvplot.pandas
import panel as pn
pn.extension()


class NodeHeadPlotter(param.Parameterized):
    depth = param.Boolean(doc='Depth to Groundwater = GSE - Level (layer selected)')
    layer = param.ObjectSelector(objects={'1': 0, '2': 1, '3': 2, '4': 3}, default=0, doc='Groundwater layers with 1 is top unconfined')
    selected = param.List(default=[0], doc='Selected node indices to display in plot')

    def __init__(self, elements_file, nodes_file, stratigraphy_file, gwh_file, recache=False, **kwargs):
        super().__init__(**kwargs)
        self.grid_data = pyiwfm.load_data(elements_file, nodes_file, stratigraphy_file)
        self.gwh = pyiwfm.read_and_cache(gwh_file, self.grid_data.nlayers, recache=recache)
        self.gnodes = gpd.GeoDataFrame(self.grid_data.nodes.copy(), geometry=[
            shapely.geometry.Point(v) for v in self.grid_data.nodes.values])
        self.node_map = self.gnodes.hvplot.points(geo=True, crs='EPSG:26910', tiles='CartoLight',
                                                  frame_height=400, frame_width=300,
                                                  fill_alpha=0.9, line_alpha=0.4,
                                                  hover_cols=['index'])
        self.node_map = self.node_map.opts(opts.Points(tools=['tap','hover'], size=10,
                                                       nonselection_color='red', nonselection_alpha=0.6, active_tools=['wheel_zoom']))
        # create a selection stream and point the source to the map 
        self.select_nodes = hv.streams.Selection1D(source=self.node_map, index=[0])
        # add the method to subscribe to selections and set param 'selected'
        self.select_nodes.add_subscriber(self.set_selected)

    def set_selected(self, index):
        self.selected = index

    @param.depends('selected', 'depth', 'layer')
    def show_ts(self):
        #print('show_ts', self.selected, self.depth, self.layer)
        index = self.selected
        if index is None or len(index) == 0:
            index = self.selected  # show last selected
        self.selected = index
        if self.depth:
            data = [self.grid_data.stratigraphy.iloc[i, 0] -
                    self.gwh[self.layer].iloc[:, i] for i in self.selected]
        else:
            data = [self.gwh[self.layer].iloc[:, i] for i in self.selected]
        els = [d.hvplot.line().opts(framewise=True) for d in data]
        return hv.Overlay(els).opts(framewise=True, title='Groundwater %s (Layer %s)'
                                    % ('Depth' if self.depth else 'Level', self.layer+1))


def build_gwh_ts_pane(plt):
    description_pane = pn.pane.Markdown('''
    # Depth to or Level of Groundwater head

    # Description
    The map below displays the nodes from C2VSIM model as points.
    The graph to the right shows the time series of levels (Layer 1) over time

    # Controls

    # Map
    On the map, the plot updates when points are selected by tapping on them

    * Selected points are blue, non-selected turn red
    * Use the zoom wheel to zoom in/out
    * Tap on a node to select it (selected nodes remain blue, others turn red).
    * To select multiple points, keep Shift key pressed while tapping on other points.
    * Unselect all points by tapping on a region containing no points

    # Depth and Layer
    Toggle to used display depth to groundwater, i.e. ground surface elevation (GSE) - water level in selected layer

    Layer 1-4 can be selected via drop down
    ''')
    map_tsplot = pn.Row(plt.node_map, pn.Column(plt.param.depth, plt.param.layer, plt.show_ts))
    gpane = pn.GridSpec(sizing_mode='scale_both')
    gpane[0, 0:4] = pn.Accordion((('Description (Click to expand/collapse)', description_pane)))
    gpane[1:4, 0:3] = map_tsplot
    gpane.servable(title='Depth To/Level of Groundwater')
    return gpane
