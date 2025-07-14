import pandas as pd
import geopandas as gpd
import fiona
import shapely

def load_obs_stations(stations_file):
    """Load observation stations from a CSV file"""
    # read the first couple of lines to check the file format
    dfc = pd.read_csv(stations_file, nrows=5)
    header = dfc.columns.tolist()
    #check if the header contains 'STN_ID'
    if 'STN_ID' in header:
        dtype_dict = {
            'STN_ID': 'int',
            'SITE_CODE': 'category',
            'LATITUDE': 'float',
            'LONGITUDE': 'float'
        }
    elif 'site_code' in header:
        if 'x' in header and 'y' in header:
            dtype_dict = {
                'site_code': 'category',
                'x': 'float',
                'y': 'float'
            }
        elif 'latitude' in header and 'longitude' in header:
            dtype_dict = {
                'site_code': 'category',
                'latitude': 'float',
                'longitude': 'float'
            }
        else:
            print('Obs stations file: ', stations_file)
            print('Header columns:', header)
            raise ValueError("The stations file must contain 'x' and 'y' or 'latitude' and 'longitude' columns for coordinates.")
    else:
        print('Obs stations file: ', stations_file)
        print('Header columns:', header)
        raise ValueError("The stations file must contain 'STN_ID' or 'site_code' columns for identification.")
    dfs = pd.read_csv(stations_file, dtype=dtype_dict)
    # Filtering out null well names. Probably don't have data? Found out more later
    if 'WELL_NAME' in dfs.columns:
        dfs = dfs[~dfs['WELL_NAME'].isna()]

    if 'LONGITUDE' in dfs.columns and 'LATITUDE' in dfs.columns:
        gdfs = gpd.GeoDataFrame(dfs,
                                geometry=gpd.points_from_xy(dfs['LONGITUDE'], dfs['LATITUDE']),
                                crs='EPSG:4326')
    elif 'x' in dfs.columns and 'y' in dfs.columns:
        gdfs = gpd.GeoDataFrame(dfs,
                                geometry=gpd.points_from_xy(dfs['x'], dfs['y']),
                                crs='EPSG:26910')
    elif 'latitude' in dfs.columns and 'longitude' in dfs.columns:
        gdfs = gpd.GeoDataFrame(dfs,
                                geometry=gpd.points_from_xy(dfs['longitude'], dfs['latitude']),
                                crs='EPSG:4326')
    else:
        print('Obs stations file: ', stations_file)
        print('Header columns:', dfs.columns.tolist())
        raise ValueError("The stations file must contain 'LONGITUDE' and 'LATITUDE' or 'x' and 'y' or 'latitude' and 'longitude' columns for coordinates.")
    return gdfs

def load_obs_measurements(measurements_file):
    """Load observation measurements from a CSV file"""
    dfc  = pd.read_csv(measurements_file, nrows=5)
    header = dfc.columns.tolist()
    if 'MSMT_DATE' in header:
        date_col = 'MSMT_DATE'
    elif 'msmt_date' in header:
        date_col = 'msmt_date'
    elif 'date' in header:
        date_col = 'date'
    else:
        print('Obs measurements file: ', measurements_file)
        print('Header columns:', header)
        raise ValueError("The measurements file must contain a 'MSMT_DATE' or 'date' column for date parsing.")
    df=pd.read_csv(measurements_file, parse_dates=[date_col])
    df[date_col] = pd.to_datetime(df[date_col], format='mixed')
    return df

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

