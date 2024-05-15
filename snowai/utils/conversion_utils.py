# -*- coding: utf-8 -*-
"""
Created on Tue Jan  10 22:47 2024

This script contains functions for converting data from one unit to another.

Author: Ibrahim Alabi
Email: ibrahimolalekana@u.boisestate.edu
Institution: Boise State University (CryoGars Lab)
"""

import os
import gdown
import datetime
import rioxarray
import numpy as np
import pandas as pd
from pyproj import Transformer
from ._other_utils import (
    get_cache_path,
    OutOfBoundsError,
    datetime_to_WaterYear, 
    ensure_raster_available,
    datetime_to_SturmWaterYear, 
)




class ConvertData:

    """
    This class contains functions for converting data from one unit to another.
    """

    def __init__(self):
        pass

    @staticmethod
    def date_to_DOY(date: datetime.datetime | pd.Timestamp, origin: int = 10, algorithm: str = "default") -> int | float:
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

        if not isinstance(date, (datetime.datetime, pd.Timestamp)):
            raise TypeError(f"Expected date to be a datetime.datetime or pd.Timestamp, got {type(date).__name__} instead.")
        
        if algorithm == "default":
            return datetime_to_WaterYear(date, origin)
        
        elif algorithm == "Sturm":
            return datetime_to_SturmWaterYear(date, origin)

        else:
            raise ValueError("Invalid algorithm. Choose between 'default' and 'Sturm'.")

    @staticmethod
    def fah_to_cel(temp_in_fahrenheit: float) -> float:

        """
        Converts fahrenheit to celsius
        
        Parameters:
        ===========
            * temp_in_fahrenheit (float): temperature in fahrenheit.

        Returns:
        ========
            * temp_in_celsius (float): temperature in celsius.
        """

        temp_in_celsius = (temp_in_fahrenheit - 32) * (5/9)

        return temp_in_celsius

    @staticmethod
    def inches_to_metric(inches: float, unit: str) -> float:
        """
        Converts inches to a specified metric unit (meters, cm, or mm).
        
        Parameters:
        ===========
            * inches (float): The measurement in inches to convert.
            * unit (str): The unit to convert to ("meters", "cm", or "mm").
        
        Returns:
        ========
            * float: The converted measurement in the specified unit.
        
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
        
        # Calculate the conversion
        return inches * conversion_factors[unit]

    
    
    @staticmethod
    def feet_to_m(measurement_in_feet: float) -> float:

        """
        Converts feet to meters
        
        Parameters:
        ===========
            * measurement_in_feet (float): measurement in feet.

        Returns:
        ========
            * measurement_in_m (float): measurement in meters.
        """

        measurement_in_m = measurement_in_feet * 0.3048

        return measurement_in_m
    
    @staticmethod
    def get_snow_class(lon: float, lat: float, raster: None) -> str:
        
        """
        Get the snow class for a given longitude and latitude.

        Parameters:
        ===========
            * lon (float): Longitude of the SNOTEL site.
            * lat (float): Latitude of the SNOTEL site.
            * raster (xr.core.dataarray.DataArray): The pre-loaded snow classification raster.

        Returns:
        ========
            * str: Snow class based on the closest pixel's value or raises an OutOfBoundsError if coordinates are outside the raster bounds.
        """


        if raster is None:
            ensure_raster_available()
            cache_path = get_cache_path()
            raster = rioxarray.open_rasterio(cache_path)
        
        snow_class_dict=dict(
            zip(
                raster.attrs['flag_values'],
                raster.attrs['flag_meanings'].split(' '))
        )

        # Transform coordinates to the raster CRS
        transformer = Transformer.from_crs(crs_from="epsg:4326", crs_to=raster.rio.crs, always_xy=True)
        x, y = transformer.transform(xx=lon, yy=lat)

        # Check if the transformed coordinates are within the raster bounds
        if not (raster.x.min().item() <= x <= raster.x.max().item()) or not (raster.y.min().item() <= y <= raster.y.max().item()):
            raise OutOfBoundsError("Provided coordinates are outside the raster bounds.")

        # Sample the raster at the given coordinates
        snow_class = raster.sel(x=x, y=y, method="nearest").values[0]

        # Return the snow class
        current_snow_class = snow_class_dict[float(snow_class)]

        new_old_mappings = {
            "montane_forest": "alpine",
            "boreal_forest": "taiga"
        }

        if current_snow_class in new_old_mappings.keys():
            current_snow_class = new_old_mappings[current_snow_class]

        return current_snow_class
