
import os
import gdown
import datetime
import numpy as np
import pandas as pd
from platformdirs import user_cache_dir

class OutOfBoundsError(Exception):
    """Exception raised when coordinates are outside the raster bounds."""
    pass

def datetime_to_SturmWaterYear(date: datetime.datetime | pd.Timestamp, origin: int =10) -> int | float:
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
    

def datetime_to_WaterYear(date: datetime.datetime | pd.Timestamp, origin : int = 10) -> int:
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

def get_cache_path(filename="SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc"):
    """
    Returns the path to the cached file, ensuring the cache directory exists.
    """
    cache_dir = user_cache_dir(appname="CroGarsAI", appauthor="BoiseStateUniversity", opinion=False)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return os.path.join(cache_dir, filename)

def ensure_raster_available():
    """
    Ensures that the necessary raster file is available in the cache,
    downloading it if necessary, but only after user consent.
    """
    cache_path = get_cache_path()
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
