import pandas as pd
import geopandas as gpd


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
