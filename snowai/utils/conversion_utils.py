# -*- coding: utf-8 -*-
"""
Created on Tue Jan  10 22:47 2024

This script contains functions for converting data from one unit to another.

Author: Ibrahim Alabi
Email: ibrahimolalekana@u.boisestate.edu
Institution: Boise State University (CryoGars Lab)
"""


import rioxarray
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer
from ._other_utils import (
    get_cache_path,
    OutOfBoundsError,
    datetime_to_WaterYear, 
    ensure_file_available,
    datetime_to_SturmWaterYear, 
)


class ConvertData:

    """
    This class contains functions for converting data from one unit to another.
    """

    def __init__(self):
        pass

    @staticmethod
    def date_to_DOY(dates: pd.Series | np.ndarray | list[str | pd.Timestamp], origin: int = 10, algorithm: str = "default") -> np.ndarray:
        """
        A function to convert a datetime or pandas Timestamp object to a day of year (DOY) number.
        
        Parameters:
        ===========
            * date (datetime.datetime | pd.Timestamp): The date to convert.
            * origin (int): The origin of the water year. Defaults to October 1st.
            * algorithm (str): The algorithm to use for the conversion. Defaults to "default".
        
        Returns:
        ========
            * DOY (int | float): The day of the water year, or np.nan for dates outside the valid months.
        """

        if not isinstance(dates, pd.Series):
            dates = pd.Series(dates)
        
        if algorithm == "default":
            return datetime_to_WaterYear(dates=dates, origin=origin)
        
        elif algorithm == "Sturm":
            return datetime_to_SturmWaterYear(dates=dates, origin=origin)

        else:
            raise ValueError("Invalid algorithm. Choose between 'default' and 'Sturm'.")

    @staticmethod
    def fah_to_cel(temp_in_fahrenheit: float | list[float] | np.ndarray) -> np.ndarray:

        """
        Converts fahrenheit to celsius
        
        Parameters:
        ===========
            * temp_in_fahrenheit (float | list[float] | np.ndarray): temperature in fahrenheit.

        Returns:
        ========
            * temp_in_celsius (float): temperature in celsius.
        """

        # Convert input to a numpy array if it isn't already one
        if not isinstance(temp_in_fahrenheit, np.ndarray):
            temp_in_fahrenheit = np.array(temp_in_fahrenheit)

        temp_in_celsius = (temp_in_fahrenheit - 32) * (5/9)

        return temp_in_celsius

    @staticmethod
    def inches_to_metric(inches: float | list[float] | np.ndarray, unit: str) -> np.ndarray:
        """
        Converts inches to a specified metric unit (meters, cm, or mm).
        
        Parameters:
        ===========
            * inches (float | list[float] | np.ndarray): The measurement in inches to convert.
            * unit (str): The unit to convert to ("meters", "cm", or "mm").
        
        Returns:
        ========
            * np.ndarray: The converted measurement in the specified unit.
        
        Raises:
        =======
            * ValueError: If the specified unit is not recognized.
        """
        conversion_factors = {
            'meters': 0.0254,
            'cm': 2.54,
            'mm': 25.4
        }
        
        if unit not in conversion_factors:
            raise ValueError(f"Invalid unit. Choose 'meters', 'cm', or 'mm'.")
        
        # Convert input to a numpy array if it isn't already one
        if not isinstance(inches, np.ndarray):
            inches = np.array(inches)
        
        # Calculate the conversion
        return inches * conversion_factors[unit]

    
    
    @staticmethod
    def feet_to_m(measurement_in_feet: float | list[float] | np.ndarray) -> np.ndarray:
        """
        Converts feet to meters.

        Parameters:
        ===========
            * measurement_in_feet: Can be a single float, a list of floats, or a numpy ndarray of floats.

        Returns:
        ========
            * measurement_in_m: Measurement in meters, corresponding to the input dimensions, as a numpy ndarray.
        """
        # Convert input to a numpy array if it isn't already one
        if not isinstance(measurement_in_feet, np.ndarray):
            measurement_in_feet = np.array(measurement_in_feet)

        return measurement_in_feet * 0.3048
    
    
    @staticmethod
    def get_snow_class(lons: np.ndarray | pd.Series, lats: np.ndarray | pd.Series, raster: xr.DataArray = None) -> np.ndarray:
        
        """
        Get the snow class for given longitudes and latitudes.

        Parameters:
        ===========
            * lons (np.ndarray): Longitudes of the SNOTEL sites.
            * lats (np.ndarray): Latitudes of the SNOTEL sites.
            * raster (xr.DataArray): The pre-loaded snow classification raster.

        Returns:
        ========
            * np.ndarray: Snow classes based on the closest pixels' values or raises a OutOfBoundsError if coordinates are outside the raster bounds.
        """


        if raster is None:
            ensure_file_available(filename="SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc")
            cache_path = get_cache_path(filename="SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc")
            raster = rioxarray.open_rasterio(cache_path)
        
        snow_class_dict=dict(
            zip(
                raster.attrs['flag_values'],
                raster.attrs['flag_meanings'].split(' '))
        )

        # Convert pandas Series to numpy arrays if necessary
        if isinstance(lons, pd.Series):
            lons = lons.to_numpy()
        if isinstance(lats, pd.Series):
            lats = lats.to_numpy()

        # Transform coordinates to the raster CRS
        transformer = Transformer.from_crs(crs_from="epsg:4326", crs_to=raster.rio.crs, always_xy=True)
        xs, ys = transformer.transform(xx=lons, yy=lats)

        # Check if the transformed coordinates are within the raster bounds
        if np.any(xs < raster.x.min().item()) or np.any(xs > raster.x.max().item()) or np.any(ys < raster.y.min().item()) or np.any(ys > raster.y.max().item()):
            raise OutOfBoundsError("Some provided coordinates are outside North America.")
        
        
        # Sample the raster at the given coordinates
        snow_classes = raster.sel(x=xr.DataArray(xs, dims='points'), y=xr.DataArray(ys, dims='points'), method="nearest").values[0]

        # Map snow classes to understandable labels
        snow_classes_mapped = np.vectorize(lambda sc: snow_class_dict[float(sc)])(snow_classes)

        new_old_mappings = {
            "montane_forest": "alpine",
            "boreal_forest": "taiga"
        }

        vectorized_mapping = np.vectorize(lambda sc: new_old_mappings.get(sc, sc))
        updated_snow_classes = vectorized_mapping(snow_classes_mapped)

        return updated_snow_classes.ravel()