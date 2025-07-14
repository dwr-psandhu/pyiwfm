import pyiwfm
import shapely.geometry
import geopandas as gpd
import pandas as pd
import numpy as np
from pyiwfm.meshcalc import build_least_squares_system
import os
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

def prepare_measurements(measurements, stations, station_id='Calibration_ID', time_col='Date_', value_col='Value_'):
    """
    Merge measurements with station coordinates and prepare for interpolation.
    
    Parameters:
    -----------
    measurements : DataFrame
        DataFrame containing measurements with SITE_CODE and MSMT_DATE
    stations : GeoDataFrame
        GeoDataFrame containing station information with SITE_CODE and geometry
        
    Returns:
    --------
    DataFrame
        Merged DataFrame with measurements and coordinates
    """
    # Convert stations to same CRS as the grid nodes
    stations = stations.to_crs('EPSG:26910')
    
    # Extract coordinates from stations
    stations_coords = pd.DataFrame({
        station_id: stations[station_id],
        'x': stations.geometry.x,
        'y': stations.geometry.y
    })
    
    # Merge measurements with station coordinates
    merged_data = measurements.merge(stations_coords, on=station_id, how='inner')
    
    # Sort by date
    merged_data = merged_data.sort_values(time_col)

    # drop duplicates to ensure unique station-date pairs
    merged_data = merged_data.drop_duplicates(subset=[station_id, time_col], keep='first')
    merged_data=merged_data.set_index(time_col)
    
    return merged_data

def get_measurements_at_time(merged_data, date_range_tuple, stations, station_id='Calibration_ID', time_col='Date_', value_col='Value_'):
    """
    Get measurements at a specific date or interpolate between surrounding dates.
    
    Parameters:
    -----------
    merged_data : DataFrame
        DataFrame containing measurements with MSMT_DATE, x, y, and GSE_GWE
    target_date : datetime
        Target date for which to get or interpolate measurements
        
    Returns:
    --------
    numpy.ndarray, numpy.ndarray, numpy.ndarray
        Arrays containing x coordinates, y coordinates, and interpolated values
    """
    gwh = merged_data.loc[date_range_tuple[0]:date_range_tuple[1]].pivot(columns=station_id, values=value_col)
    gwh = gwh.interpolate(method='linear', axis=0)
    gwh = gwh.ffill().bfill()  # Fill any remaining NaNs
    gwh = gwh.mean(axis=0)
    gwh = gwh.reset_index()
    gwh.columns = [station_id, value_col]
    # Merge with stations to get coordinates
    df = pd.merge(stations, gwh)[[station_id, 'geometry', value_col]]
    return df.geometry.x.values, df.geometry.y.values, df[value_col].values

def spatial_interpolation(grid_data, x_obs, y_obs, obs_vals, reg_weight=1e-3):
    """
    Perform spatial interpolation of observation values to mesh nodes.
    
    Parameters:
    -----------
    grid_data : namedtuple
        Contains elements and nodes data
    x_obs, y_obs : numpy.ndarray
        Arrays of x and y coordinates of observation points
    obs_vals : numpy.ndarray
        Array of observation values
    reg_weight : float, optional
        Regularization weight for the least squares system
        
    Returns:
    --------
    numpy.ndarray
        Interpolated values at mesh nodes
    """
    # Convert elements dataframe to array of triangle vertex indices
    elements_array = grid_data.elements.values[:, :3].astype(int) - 1  # Convert to 0-based indexing
    
    # Prepare observation points
    obs_points = np.column_stack((x_obs, y_obs))
    
    # Build and solve the least squares system
    node_values = build_least_squares_system(
        grid_data.nodes.values, 
        elements_array, 
        obs_points, 
        obs_vals,
        reg_weight=reg_weight
    )
    
    return node_values

def interpolate_obs_to_mesh(grid_data, merged_data, date_range, output_file, reg_weight=1e-3, station_id='Calibration_ID', time_col='Date_', value_col='Value_'):
    """
    Interpolate observations to mesh nodes for a range of dates and save the results.
    
    Parameters:
    -----------
    grid_data : namedtuple
        Contains elements and nodes data
    merged_data : DataFrame
        DataFrame containing measurements with MSMT_DATE, x, y, and GSE_GWE
    date_range : list or array
        List of dates for which to perform interpolation
    output_file : str
        Path to save the output as a feather file
    reg_weight : float, optional
        Regularization weight for the least squares system
        
    Returns:
    --------
    DataFrame
        DataFrame containing interpolated values at nodes for each date
    """
    # Create empty DataFrame columns dictionary first
    node_columns = {str(node_id): pd.Series(np.nan, index=date_range) for node_id in grid_data.nodes.index}
    
    # Create DataFrame all at once to avoid fragmentation
    results = pd.DataFrame(node_columns, index=date_range)
    
    # Perform interpolation for each date
    for date in date_range:
        print(f"Processing date: {date}")
        
        # Get measurements at the current date (with temporal interpolation)
        x_obs, y_obs, obs_vals = get_measurements_at_time(merged_data, date, station_id=station_id, time_col=time_col, value_col=value_col)
        
        # Skip if no data available for this date
        if len(x_obs) < 3:  # Need at least 3 points for meaningful interpolation
            print(f"  Skipping date {date}: insufficient data points ({len(x_obs)})")
            continue
        print(f"  Found {len(x_obs)} observation points for date {date}")
        try:
            # Perform spatial interpolation
            print(f"  Interpolating values for date {date}...")
            node_values = spatial_interpolation(grid_data, x_obs, y_obs, obs_vals, reg_weight)
            print(f"  Interpolation complete for date {date}.")
            # Store results - update entire row at once
            results.loc[date] = dict(zip([str(i) for i in grid_data.nodes.index], node_values))
                
        except Exception as e:
            print(f"  Error processing date {date}: {str(e)}")
    
    # Save results to feather file
    results_reset = results.reset_index()
    results_reset.rename(columns={'index': 'Time'}, inplace=True)
    results_reset.to_feather(output_file)
    
    return results

def interpolate_using_obs_delaunay(grid_data, merged_data, stations, date_range, output_file, station_id='Calibration_ID', time_col='Date_', value_col='Value_'):
    """
    Interpolate observations to mesh nodes using Delaunay triangulation of observation stations.
    This approach first creates a triangular mesh from the observation stations, then uses
    linear interpolation to find values at grid nodes.
    
    Parameters:
    -----------
    grid_data : namedtuple
        Contains elements and nodes data
    merged_data : DataFrame
        DataFrame containing measurements with time, x, y, and value columns
    date_range : list or array
        List of dates for which to perform interpolation
    output_file : str
        Path to save the output as a feather file
    time_col : str, optional
        Column name for the time values
    value_col : str, optional
        Column name for the observation values
        
    Returns:
    --------
    DataFrame
        DataFrame containing interpolated values at nodes for each date
    """
    # Create empty DataFrame to store results
    node_columns = {str(node_id): pd.Series(np.nan, index=date_range) for node_id in grid_data.nodes.index}
    results = pd.DataFrame(node_columns, index=date_range)
    
    # Get grid node coordinates
    grid_node_coords = grid_data.nodes.values
    
    # Process each date
    for date in date_range:
        print(f"Processing date: {date}")
        # lets get the range of dates from the year before to the month of the date
        min_date = date - pd.DateOffset(years=1)
        max_date = date + pd.DateOffset(months=1)
        # Get data for the current date (with temporal interpolation) for the month
        x_obs, y_obs, obs_vals = get_measurements_at_time(
            merged_data, (min_date, max_date), stations, station_id=station_id, time_col=time_col, value_col=value_col
        )
        
        # Skip if insufficient data
        if len(x_obs) < 3:
            print(f"  Skipping date {date}: insufficient data points ({len(x_obs)})")
            continue
            
        try:
            # Create observation points array
            obs_points = np.column_stack((x_obs, y_obs))
            
            # Create Delaunay triangulation of observation points
            try:
                
                if np.isnan(obs_vals).any():
                    valid_mask = ~np.isnan(obs_vals)
                    clean_obs_points = obs_points[valid_mask]
                    clean_obs_vals = obs_vals[valid_mask]
                else:
                    clean_obs_points = obs_points
                    clean_obs_vals = obs_vals                    
                # Try to create Delaunay triangulation
                tri = Delaunay(clean_obs_points)
                # Create interpolator using the triangulation
                interpolator = LinearNDInterpolator(tri, clean_obs_vals)
                # Re-create interpolators with clean data
                nearest_interpolator = NearestNDInterpolator(clean_obs_points, clean_obs_vals)
                
                # Interpolate values at grid nodes
                interpolated_values = interpolator(grid_node_coords)
                
                # Handle points outside the triangulation using nearest neighbor
                mask = np.isnan(interpolated_values)
                if np.any(mask):
                    interpolated_values[mask] = nearest_interpolator(grid_node_coords[mask])
                    
            except Exception as e:
                print(f"  Error creating triangulation: {str(e)}. Using nearest neighbor interpolation.")
                # Fallback to nearest neighbor interpolation
                nearest_interpolator = NearestNDInterpolator(obs_points, obs_vals)
                interpolated_values = nearest_interpolator(grid_node_coords)
            
            # Store results
            if value_col in ['gse_gwe', 'GSE_GWE']:
                interpolated_values = grid_data.stratigraphy.GSE.values - interpolated_values

            results.loc[date] = dict(zip([str(i) for i in grid_data.nodes.index], interpolated_values))
                
        except Exception as e:
            print(f"  Error processing date {date}: {str(e)}")
    
    # Save results to feather file
    results_reset = results.reset_index()
    results_reset.rename(columns={'index': 'Time'}, inplace=True)
    results_reset.index = pd.to_datetime(results_reset.index)+pd.offsets.MonthEnd(0)  # Ensure time is at month end
    results_reset.to_feather(output_file)
    
    return results_reset

def interpolate_observations_to_mesh(elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file):
    """
    Interpolate observation data to mesh nodes.
    """
    # Load grid data
    grid_data = pyiwfm.load_data(elements_file, nodes_file, strat_file)
    
    # Load observation stations and measurements
    stations = pyiwfm.load_obs_stations(stations_file)
    stations = stations.to_crs('EPSG:26910')  # Convert to the same CRS as the grid data
    measurements = pyiwfm.load_obs_measurements(measurements_file)

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
    
    # Prepare data
    merged_data = prepare_measurements(measurements, stations, station_id=station_id, time_col=time_col)
    #
    # Generate monthly date range based on the available data
    min_date = pd.Timestamp(merged_data.index.min().year, merged_data.index.min().month, 1)
    max_date = pd.Timestamp(merged_data.index.max().year, merged_data.index.max().month, 1)
    date_range = pd.date_range(start=min_date, end=max_date, freq='MS')

    # Interpolate observations to mesh nodes using the merged data
    results = interpolate_using_obs_delaunay(
        grid_data, merged_data, stations, date_range, output_file, 
        station_id=station_id, time_col=time_col, value_col=value_col
    )

    print(f"Interpolation complete. Results saved to {output_file}")
    return results

def cache_obs_interpolation_feather(file, df):
    """
    Cache observation interpolation results in feather format.
    
    Parameters:
    -----------
    file : str
        Output file path
    df : DataFrame
        DataFrame containing interpolated values
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file), exist_ok=True)
    
    # Save to feather file
    df.reset_index().to_feather(file)
    
def load_obs_interpolation_feather(file):
    """
    Load observation interpolation results from feather format.
    
    Parameters:
    -----------
    file : str
        Input file path
        
    Returns:
    --------
    DataFrame
        DataFrame containing interpolated values
    """
    df = pd.read_feather(file)
    if df.index.name != 'Time':
        if 'Time' in df.columns:
            df = df.set_index('Time')
        else:
            raise ValueError("The DataFrame does not have a 'Time' column to set as index or 'Time' index name.")
    return df


from pyiwfm.trimesh_animator import GWHeadAnimator, convertxy, build_panel
import panel as pn
pn.extension()


def build_gwh_animator(elements_file, nodes_file, strat_file, interpolated_file, title=''):
    # Example of how to load the results
    loaded_results = load_obs_interpolation_feather(interpolated_file)
    loaded_results = loaded_results.ffill().bfill()  # Fill any NaNs
    dfgwh = [loaded_results]
    # Load grid data
    grid_data = pyiwfm.load_data(elements_file, nodes_file, strat_file)
    #    
    dfn0 = convertxy(grid_data.nodes)
    dfgw0 = dfgwh[0]
    dfn0['z'] = dfgw0.iloc[0, :].values
    # make animator
    return GWHeadAnimator(grid_data.elements, dfn0, dfgwh, grid_data.stratigraphy, 
                          name='Groundwater Level %s Animator',
                          title=title)

def visualize_interpolated_results(elements_file, nodes_file, strat_file, interpolated_file, title='Groundwater Level Interpolation'):
    """
    Visualize the interpolated groundwater level results.
    
    Parameters:
    -----------
    elements_file : str
        Path to the elements file
    nodes_file : str
        Path to the nodes file
    strat_file : str
        Path to the stratigraphy file
    interpolated_file : str
        Path to the interpolated results file
    title : str, optional
        Title for the visualization panel
    """
    gwa = build_gwh_animator(elements_file, nodes_file, strat_file, interpolated_file, title)
    template = build_panel(gwa)
    pn.serve(template, show=True, title='Groundwater Level Interpolation')

def interpolate_observations(elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file):
    # Interpolate observations to mesh nodes
    results = interpolate_observations_to_mesh(
        elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file
    )
    
    # Cache results in feather format
    cache_obs_interpolation_feather(output_file, results)

def show_obs_interpolation(elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file):
    """
    Show the observation interpolation results using the new pivoted data format.
    """
    # Check if output file already exists
    if not os.path.exists(output_file):
        print(f"Output file {output_file} does not exist. Interpolating observations...")
        interpolate_observations(elements_file, nodes_file, strat_file, stations_file, measurements_file, output_file)
    
    # Load and visualize the results
    visualize_interpolated_results(
        elements_file, nodes_file, strat_file, output_file
    )

