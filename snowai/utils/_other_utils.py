
import os
import gdown
import numpy as np
import pandas as pd
from platformdirs import user_cache_dir

class OutOfBoundsError(Exception):
    """Exception raised when coordinates are outside the raster bounds."""
    pass

def datetime_to_SturmWaterYear(dates: pd.Series | np.ndarray | list[str | pd.Timestamp], origin: int = 10) -> np.ndarray:
    """
    
    A function to convert a series of datetime or pandas Timestamp objects to a day of year (DOY) number using Sturm et al. (2010) algorithm. 
        DOI: https://doi.org/10.1175/2010JHM1202.1
    
     Note: Sturm et al. (2010) algorithm runs from -92 (1 October) to +181 (30 June) and +182 for a leap year.

    Parameters:
    ===========
        * dates (pd.Series | np.ndarray | list[str | pd.Timestamp]): The series of dates to convert.
        * origin (int): The month that defines the start of the water year (defaults to October).

    Returns:
    ========
        * np.ndarray: The days of the water year or np.nan for dates between July 1 and September 30.
    """
    
    # Ensure the input is a pd.Series
    if not isinstance(dates, pd.Series):
        dates = pd.Series(dates)
    
    # Convert to datetime if not already
    dates = pd.to_datetime(dates, errors='coerce')


    # Exclude dates in July, August, and September
    valid_months_mask = ~dates.dt.month.isin([7, 8, 9])

    # Calculate reference date for each date based on whether the date's month is before or after October
    years_adjusted = np.where(dates.dt.month >= origin, dates.dt.year + 1, dates.dt.year)
    reference_dates = pd.to_datetime({
        'year': years_adjusted,
        'month': np.full_like(years_adjusted, 1),
        'day': np.full_like(years_adjusted, 1)
    })

    # Calculate the DOY from the reference date
    doys = (dates - reference_dates).dt.days

    # Adjust DOY based on the month condition and handle the range specifically for the Sturm algorithm
    adjusted_doys = np.where(valid_months_mask, doys, np.nan)
    adjusted_doys = np.where(adjusted_doys>=0, adjusted_doys+1, adjusted_doys)

    return adjusted_doys


def datetime_to_WaterYear(dates: pd.Series | np.ndarray | list[str | pd.Timestamp], origin: int = 10) -> np.ndarray:
    """
    
    A function to convert a series of datetime or pandas Timestamp objects to a day of year (DOY) number uwhere the origin is DOY 1. 

    Parameters:
    ===========
        * dates (pd.Series | np.ndarray | list[str | pd.Timestamp]): The series of dates to convert.
        * origin (int): The month that defines the start of the water year (defaults to October).

    Returns:
    ========
        * np.ndarray: The days of the water year.
    """
    
    # Ensure the input is a pd.Series
    if not isinstance(dates, pd.Series):
        dates = pd.Series(dates)
    
    # Convert to datetime if not already
    dates = pd.to_datetime(dates, errors='coerce')


    # Calculate reference date for each date based on whether the date's month is before or after October
    years_adjusted = np.where(dates.dt.month >= origin, dates.dt.year, dates.dt.year-1)

    reference_dates = pd.to_datetime({
        'year': years_adjusted,
        'month': np.full_like(years_adjusted, origin),
        'day': np.full_like(years_adjusted, 1)
    })

    # Calculate the DOY from the reference date
    doys = (dates - reference_dates).dt.days + 1

    return doys.to_numpy()


def get_cache_path(filename: str):
    """
    Returns the path to the cached file, ensuring the cache directory exists.
    """
    cache_dir = user_cache_dir(appname="CroGarsAI", appauthor="BoiseStateUniversity", opinion=False)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return os.path.join(cache_dir, filename)

def ensure_file_available(filename):
    """
    Ensures that the necessary file is available in the cache,
    downloading it if necessary, but only after user consent.
    """

    filenames_map={
        "SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc": "Snow Classification raster",
        "density_model.ubj": "Machine Learning Wegiths"
    }

    cache_path = get_cache_path(filename)

    file = filenames_map[filename]

    if not os.path.exists(cache_path):
        print(f"The {file} needs to be downloaded.")
        if file == "Snow Classification raster":
            print("This file is approximately 1.9 GB in size and will be stored at: {}".format(cache_path))
        
        else:
            print("This file is approximately 180 MB in size and will be stored at: {}".format(cache_path))
        
        user_input = input("Do you want to proceed with the download? (yes/no): ")
        if user_input.lower() == 'yes' or user_input.lower() == 'y' or user_input.lower() == 'true':
            if file == "Snow Classification raster":
                raster_url = "https://drive.google.com/file/d/1yhthVbkdBNm_pL5wl5YlwNaKN96iUGa8/view?usp=sharing"
            else:
                raster_url = "https://drive.google.com/file/d/11FwI4Y8IYGP_6m2evQIv4Tu2l7F6edCK/view?usp=sharing"
            print("Downloading now...")
            gdown.download(url=raster_url, output=cache_path, fuzzy=True, quiet=False)
            print("Download complete.")
        else:
            print("Download aborted. The application may not function properly without the raster data.")

def clean_cache(filename: str = None):
    """
    Clears the cache directory.
    """
    if filename == 'density':
        cache_file= get_cache_path("density_model.ubj")
    
    elif filename == 'snow_class':
        cache_file= get_cache_path("SnowClass_NA_300m_10.0arcsec_2021_v01.0.nc")

    else:
        raise ValueError("Invalid filename. Choose 'density' or 'snow_class'.")
    
    try:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"Cleared cached file at {cache_file}")
        else:
            print(f"No cached file found at {cache_file}")
    except Exception as e:
        print(f"Error deleting {cache_file}: {e}")

