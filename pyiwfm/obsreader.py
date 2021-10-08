import pandas as pd
import geopandas as gpd
import fiona
import shapely

def load_obs_stations(stations_file):
    dfs = pd.read_csv(stations_file, dtype={
                      'STN_ID': 'int', 'SITE_CODE': 'category', 'LATITUDE': 'float', 'LONGITUDE': 'float'})
    # Filtering out null well names. Probably don't have data? Found out more later
    dfs = dfs[~dfs['WELL_NAME'].isna()]
    gdfs = gpd.GeoDataFrame(dfs,
                            geometry=gpd.points_from_xy(dfs['LONGITUDE'], dfs['LATITUDE']),
                            crs='EPSG:4326')
    return gdfs


def load_and_merge_observations(gdfs, file):
    dfobs = pd.read_csv(file, dtype={'SITE_CODE': 'category', 'WLM_ID': int,
                        'WLM_RPE': 'float', 'WLM_GSE': 'float', 'GWE': 'float', 'GSE_GWE': 'float',
                        'WLM_QA': 'category', 'WLM_DESC': 'category', 'WLM_ACC_DESC': 'category', 'WLM_ORG_NAME': 'category',
                        'COOP_ORG_NAME': 'category', 'MONITORING_PROGRAM': 'category', 'MSMT_CMT': 'category'})
    return dfobs.join(gdfs, on='SITE_CODE', rsuffix='OBS_')

def load_calib_stations(gdb_file):
    # gdb_file = '../tests/data/c2vsim_cg_1921ic_r374_gis/C2VSim_CG_1921IC_R374.gdb'
    # Get all the layers from the .gdb file
    layers = fiona.listlayers(gdb_file)
    calib_stations = gpd.read_file(gdb_file, layer='CalibrationWell')
    return calib_stations

def load_calib_measurements(gdb_file):
    # Get all the layers from the .gdb file
    layers = fiona.listlayers(gdb_file)
    calib_measurements = gpd.read_file(gdb_file, layer='TSData_ObservedGWL')
    calib_measurements['Date_'] = pd.to_datetime(calib_measurements.Date_)
    return calib_measurements

def load_gwheads(gdb_file):
    gwheads=gpd.read_file(gdb_file,layer='Output_GWHead')
    return gwheads