#%%
import pyiwfm
from pyiwfm import gwh_obs_interpolater
fg_dir = 'D:/gw/studies/c2vsimfg_v1.5_model'
elements_file=fg_dir + '/Preprocessor/C2VSimFG_Elements.dat'
nodes_file=fg_dir + '/Preprocessor/C2VSimFG_Nodes.dat'
strat_file=fg_dir + '/Preprocessor/C2VSimFG_Stratigraphy.dat'
head_file=fg_dir + '/Results/C2VSimFG_GW_HeadAll.out'
#stations_file='tests/data/gwdata/periodic_gwl/stations.csv'
#measurements_file='tests/data/gwdata/periodic_gwl/measurements.csv'

#fg_obs_dir='D:/gw/observation_dataset/c2vsimfg_v1.5_gw_obs_20250516'
#stations_file= fg_obs_dir + '/c2vsimfg_v1.5_stn_20250516.csv'
#measurements_file= fg_obs_dir + '/c2vsimfg_v1.5_gw_obs_20250516.csv'
#output_file = fg_obs_dir + '/c2vsimfg_v1.5_gw_obs_20250516_interpolated.feather'

# cg_dir = "d:/gw/studies/20250604_1227par_PstCld_best_pars/C2VSimCG"
# elements_file = f'{cg_dir}/Preprocessor/C2VSimCG_Elements.dat'
# nodes_file = f'{cg_dir}/Preprocessor/C2VSimCG_Nodes.dat'
# strat_file = f'{cg_dir}/Preprocessor/C2VSimCG_Stratigraphy.dat'
gwdata = 'D:/gw/studies/gwdata/periodic_gwl.2025.07'
stations_file = gwdata + '/stations.csv'
measurements_file = gwdata + '/measurements.csv'
#output_file = gwdata + '/interpolated.feather'
output_file = gwdata + '/interpolated.finegrid.GSE.feather'
#%%
results = gwh_obs_interpolater.interpolate_observations_to_mesh(
    elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file)
#%%
import pyiwfm
# Load grid data
grid_data = pyiwfm.load_data(elements_file, nodes_file, strat_file)
results.iloc[:,1:]=results.iloc[:,1:].values-grid_data.stratigraphy.GSE.values
results.iloc[:,1:]=grid_data.stratigraphy.GSE.values-results.iloc[:,1:].values
results_reset = results.set_index('Time')
results_reset.to_feather(output_file)
#%%
pyiwfm.gwh_obs_interpolater.visualize_interpolated_results(elements_file, 
                                                           nodes_file, strat_file, output_file, title='Groundwater Level Interpolation')

# %%
# from cli
# pyiwfm gwh-obs-interpolater \
#     --elements_file D:/gw/studies/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Elements.dat \
#     --nodes_file D:/gw/studies/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Nodes.dat \
#     --strat_file D:/gw/studies/c2vsimfg_v1.5_model/Preprocessor/C2VSimFG_Stratigraphy.dat \
#     --stations_file D:/gw/observation_dataset/c2vsimfg_v1.5_gw_obs_20250516/c2vsimfg_v1.5_stn_20250516.csv \
#     --measurements_file D:/gw/observation_dataset/c2vsimfg_v1.5_gw_obs_20250516/c2vsimfg_v1.5_gw_obs_20250516.csv \
#     --output_file D:/gw/observation_dataset/c2vsimfg_v1.5_gw_obs_20250516/c2vsimfg_v1.5_gw_obs_20250516_interpolated.feather

# %%
import pyiwfm
# Load grid data
grid_data = pyiwfm.load_data(elements_file, nodes_file, strat_file)

# Load observation stations and measurements
stations = pyiwfm.load_obs_stations(stations_file)
measurements = pyiwfm.load_obs_measurements(measurements_file)

# %%
if 'site_code' in stations.columns:
    station_id='site_code'
    if 'date' in measurements.columns:
        time_col='date'
        value_col='gwe'
    else:
        time_col='msmt_date'
        value_col='gse_gwe'
elif 'SITE_CODE' in stations.columns:
    station_id='SITE_CODE'
    time_col='MSMT_DATE'
    value_col='GSE_GWE'
elif 'Calibration_ID' in stations.columns:
    station_id='Calibration_ID'
    time_col='Date_'
    value_col='Value_'
else:
    print('Obs stations file: ', stations_file)
    print('Header columns:', stations.columns.tolist())
    raise ValueError("The stations file must contain 'site_code' or 'Calibration_ID' columns for identification.")

#%%
stations = stations.to_crs('EPSG:26910')  # Convert to the same CRS as the grid data
# Prepare data
from pyiwfm.gwh_obs_interpolater import prepare_measurements
merged_data = prepare_measurements(measurements, stations, station_id=station_id, time_col=time_col)

# %%
dfo=merged_data.reset_index()
# Remove duplicates, keeping only the first occurrence
dfo = dfo.drop_duplicates(subset=[time_col, station_id], keep='first')
dfo=dfo.set_index(time_col)
#%%
dt = pd.Timestamp('2001-03-01')
gwh = dfo.loc[dt - pd.DateOffset(years=1):dt].pivot(columns=station_id, values=value_col)
gwh = gwh.interpolate(method='linear', axis=0)
gwh = gwh.ffill().bfill()  # Fill any remaining NaNs
gwh = gwh.mean(axis=0)
gwh=gwh.reset_index()
gwh.columns=['SITE_CODE', 'GSE_GWE']
#%%
import pandas as pd
dfm=pd.merge(gwh,stations, on='SITE_CODE')

df=pd.merge(stations, gwh)[[station_id, 'geometry', 'GSE_GWE']]

df=df.to_crs('EPSG:26910')
df.geometry.x
df.geometry.y
df.GSE_GWE

# %%
pyiwfm.gwh_obs_interpolater.interpolate_observations_to_mesh(
    elements_file, nodes_file, strat_file, 
    stations_file, measurements_file, output_file)
# %%
pyiwfm.gwh_obs_interpolater.visualize_interpolated_results(elements_file, nodes_file, strat_file, output_file, title='Groundwater Level Interpolation')

# %%
