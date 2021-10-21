import pyposeidon.meteo as pmeteo
import pytest
import xarray as xr
import os
import numpy as np
import shutil

from . import DATA_DIR


METEO_NC = DATA_DIR / "meteo.nc"
ERA5_GRIB = DATA_DIR / "era5.grib"
DATASET = xr.Dataset(data_vars=dict(lat=(("node", [1, 2, 3]))))


def test_dispatch_meteo_source_unknown_object_raises():
    obj = 3
    with pytest.raises(ValueError) as exc:
        pmeteo.dispatch_meteo_source(obj=3)
    assert "Can't determine meteo_type" in str(exc)


def test_dispatch_meteo_source_unknown_string_raises():
    obj = "gibberish"
    with pytest.raises(ValueError) as exc:
        pmeteo.dispatch_meteo_source(obj=obj)
    assert f"Can't determine meteo_type from string: {obj}" in str(exc)


def test_dispatch_meteo_source_multiple_types_raises():
    obj = ["asdf", 123]
    with pytest.raises(ValueError) as exc:
        pmeteo.dispatch_meteo_source(obj=obj)
    assert "Multiple types in iterable:" in str(exc)


@pytest.mark.parametrize(
    "expected_func, meteo_source",
    [
        pytest.param(pmeteo.netcdf, METEO_NC, id="netcdf pathlib single"),
        pytest.param(pmeteo.netcdf, METEO_NC.as_posix(), id="netcdf str single"),
        pytest.param(pmeteo.netcdf, [METEO_NC], id="netcdf list pathlib"),
        pytest.param(pmeteo.netcdf, [METEO_NC.as_posix()], id="netcdf list str"),
        pytest.param(pmeteo.cfgrib, ERA5_GRIB, id="grib pathlib single"),
        pytest.param(pmeteo.cfgrib, ERA5_GRIB.as_posix(), id="grib str single"),
        pytest.param(pmeteo.cfgrib, [ERA5_GRIB], id="grib list pathlib"),
        pytest.param(pmeteo.cfgrib, [ERA5_GRIB.as_posix()], id="grib list str"),
        pytest.param(pmeteo.from_url, "https://example.com", id="https url"),
        pytest.param(pmeteo.from_url, "http://example.com", id="http url"),
        pytest.param(pmeteo.passthrough, DATASET, id="passthrough"),
    ],
)
def test_meteo_dispatch_netcdf(expected_func, meteo_source):
    func = pmeteo.dispatch_meteo_source(meteo_source)
    assert func is expected_func


@pytest.mark.parametrize(
    "meteo_source",
    [
        pytest.param(METEO_NC, id="netcdf"),
        pytest.param(ERA5_GRIB, id="grib"),
        pytest.param(DATASET, id="passthrough"),
    ],
)
def test_meteo_returns_dataset(meteo_source):
    meteo = pmeteo.meteo(meteo_source)
    assert isinstance(meteo, pmeteo.meteo)
    assert isinstance(meteo.Dataset, xr.Dataset)


def test_meteo_passthrough():
    original_meteo = pmeteo.meteo(DATASET)
    new_meteo = pmeteo.meteo(meteo_source=original_meteo.Dataset)
    assert new_meteo.Dataset.equals(original_meteo.Dataset)


@pytest.mark.xfail
def test_meteo_url():
    today = pd.to_datetime(datetime.datetime.today())
    url = "https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs{}/gfs_0p25_1hr_{:0>2d}z".format(
        today.strftime("%Y%m%d"), r[h]
    )
    meteo = pmeteo.meteo(meteo_source=url)
    assert isinstance(meteo.Dataset, xr.Dataset)


@pytest.mark.xfail
def test_meteo_default_arguments():
    meteo = pmeteo.meteo(meteo_source=None)
    assert isinstance(meteo.Dataset, xr.Dataset)
