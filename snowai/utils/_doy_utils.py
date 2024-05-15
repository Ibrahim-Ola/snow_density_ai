
import datetime
import numpy as np
import pandas as pd



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