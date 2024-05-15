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
import argparse
import datetime
import rioxarray
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer
from platformdirs import user_cache_dir


class OutOfBoundsError(Exception):
    """Exception raised when coordinates are outside the raster bounds."""
    pass

class ConvertData:

    """
    This class contains functions for converting data from one unit to another.
    """

    def __init__(self):
        pass

    
    def datetime_to_SturmWaterYear(self, date: datetime.datetime | pd.Timestamp, origin: int =10) -> int | float:
        """
        A function to convert a datetime or pandas Timestamp object to a day of year (DOY) number using Sturm et al. (2010) algorithm. 
        DOI: https://doi.org/10.1175/2010JHM1202.1

        Note: Sturm et al. (2010) algorithm runs from -92 (1 October) to +181 (30 June) and +182 for a leap year.
        
        Parameters:
        ===========
            * date (datetime.datetime | pd.Timestamp): The date to convert.
        
        Returns:
        ========
            * DOY (int | float): The day of the water year or np.nan for dates between July 1 and September 30.
                                 The np.nan is specifically returned for dates that fall outside the defined operational range of the Sturm algorithm.
        """
        
        # determine if the month is valid for the algorithm
        if 7 <= date.month < 10:
            return np.nan
        
        # Normalize date to UTC
        if isinstance(date, pd.Timestamp):
            if date.tzinfo is not None:
                date = date.tz_convert('UTC')
            else:
                date = date.tz_localize('UTC')
        else:
            if date.tzinfo is not None:
                date = date.astimezone(datetime.timezone.utc)
            else:
                date = date.replace(tzinfo=datetime.timezone.utc)
        
        # Determine the reference date
        reference = datetime.datetime(date.year if date.month < origin else date.year + 1, 1, 1, tzinfo=datetime.timezone.utc)
        
        # Calculate the day of the year offset from the reference date
        delta = date - reference

        DOY = delta.days

        # Handle the skipping of 0 by adjusting DOY accordingly
        if DOY >= 0:
            DOY += 1
        
        return DOY
    

    def datetime_to_WaterYear(self, date: datetime.datetime | pd.Timestamp, origin : int = 10) -> int:
        """
        A function to convert a datetime or pandas Timestamp object to a day of year number where the origin is DOY 1.
        The origin defaults to October 1st.
        
        Parameters:
        ===========
            * date (datetime.datetime | pd.Timestamp): The date to convert.
        
        Returns:
        ========
            * DOY (int): The day of the water year.
        """

        # Normalize date to UTC
        if isinstance(date, pd.Timestamp):
            if date.tzinfo is not None:
                date = date.tz_convert('UTC')
            else:
                date = date.tz_localize('UTC')
        else:
            if date.tzinfo is not None:
                date = date.astimezone(datetime.timezone.utc)
            else:
                date = date.replace(tzinfo=datetime.timezone.utc)


        # Determine the start of the water year
        water_year_start = datetime.datetime(date.year if date.month >= origin else date.year - 1, origin, 1, tzinfo=datetime.timezone.utc)
        
        # Calculate the day of the year offset from October 1
        DOY = (date - water_year_start).days + 1
        
        return DOY
    
    def date_to_DOY(self, date: datetime.datetime | pd.Timestamp, origin: int = 10, algorithm: str = "default") -> int | float:
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
            return self.datetime_to_WaterYear(date, origin)
        
        elif algorithm == "Sturm":
            return self.datetime_to_SturmWaterYear(date, origin)

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
    def get_cache_path(filename="SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc"):
        """
        Returns the path to the cached file, ensuring the cache directory exists.
        """
        cache_dir = user_cache_dir(appname="CroGarsAI", appauthor="BoiseStateUniversity", opinion=False)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, filename)
    

    @staticmethod
    def ensure_raster_available():
        """
        Ensures that the necessary raster file is available in the cache,
        downloading it if necessary, but only after user consent.
        """
        cache_path = ConvertData.get_cache_path()
        if not os.path.exists(cache_path):
            print("Snow classification raster needs to be downloaded.")
            print("This file is approximately 2 GB in size and will be stored at: {}".format(cache_path))
            user_input = input("Do you want to proceed with the download? (yes/no): ")
            if user_input.lower() == 'yes':
                raster_url = "https://drive.google.com/file/d/1yhthVbkdBNm_pL5wl5YlwNaKN96iUGa8/view?usp=sharing" 
                print("Downloading now...")
                gdown.download(url=raster_url, output=cache_path, fuzzy=True, quiet=False)
                print("Download complete.")
            else:
                print("Download aborted. The application may not function properly without the raster data.")


    
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
            ConvertData.ensure_raster_available()
            cache_path = ConvertData.get_cache_path()
            raster = xr.open_dataarray(cache_path)
        
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
