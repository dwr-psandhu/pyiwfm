import pytest
from pyiwfm import obsreader


@pytest.mark.parametrize("stations_file", ["data/gwdata/periodic_gwl/stations.csv"])
def test_read_stations(stations_file):
    gdf = obsreader.load_obs_stations(stations_file)
    assert len(gdf) > 10000  # it should have lots of stations


@pytest.mark.parametrize("stations_file, measurements_file", [("data/gwdata/periodic_gwl/stations.csv", "data/gwdata/periodic_gwl/measurements.csv")])
def test_read_measurements(stations_file, measurements_file):
    gdf = obsreader.load_obs_stations(stations_file)
    assert len(gdf) > 10000  # it should have lots of stations
    mdf = obsreader.load_and_merge_observations(gdf, measurements_file)
    assert len(mdf) > 100000 # it has even more
