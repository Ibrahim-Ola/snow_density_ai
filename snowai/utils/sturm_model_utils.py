
## Import libraries
import datetime
import numpy as np
import pandas as pd
from .conversion_utils import ConvertData, OutOfBoundsError

# Constants for snow classes
VALID_SNOW_CLASSES = ['alpine', 'maritime', 'prairie', 'tundra', 'taiga']


alpine_params = {
    'rho_max': 0.5975,
    'rho_0': 0.2237,
    'k1': 0.0012,
    'k2': 0.0038
}

maritime_params = {
    'rho_max': 0.5979,
    'rho_0': 0.2578,
    'k1': 0.0010,
    'k2': 0.0038
}

prairie_params = {
    'rho_max': 0.5940,
    'rho_0': 0.2332,
    'k1': 0.0016,
    'k2': 0.0031
}

tundra_params = {
    'rho_max': 0.3630,
    'rho_0': 0.2425,
    'k1': 0.0029,
    'k2': 0.0049
}


taiga_params = {
    'rho_max': 0.2170,
    'rho_0': 0.2170,
    'k1': 0.0000,
    'k2': 0.0000
}

sturm_model_params ={
    'alpine': alpine_params,
    'maritime': maritime_params,
    'prairie': prairie_params,
    'tundra': tundra_params,
    'taiga': taiga_params
}

def validate_snow_class(snow_class: str) -> str:
    """
    A function to validate the snow class.
    """

    if snow_class.lower() not in (s.lower() for s in VALID_SNOW_CLASSES):
        return np.nan
    return snow_class.lower()


def validate_SturmDOY(x: int | float | str | pd.Timestamp | datetime.datetime) -> int | float:
    """
    Validates and converts input into the Sturm et al. (2010) Day of Year (DOY).
    Handles integer, string representations of dates, and datetime objects.
    Returns NaN for out-of-range DOY or dates in excluded months (July to September).

    Sturm et al. (2010) - DOI: https://doi.org/10.1175/2010JHM1202.1

    Parameters:
        x (int, str, pd.Timestamp, datetime.datetime): The input to validate and convert.

    Returns:
        int or NaN: The Sturm DOY or NaN if the input is invalid or in the excluded range.
    """
    MIN_DOY = -92
    MAX_DOY = 182
    EXCLUDED_MONTHS = range(7, 10)  # July, August, September

    try:
        float_x = float(x)
    except:
        pass

    else:
        if float_x.is_integer():
            doy = int(float_x)
            if doy >= MIN_DOY and doy <= MAX_DOY:
                return doy
            else:
                raise OutOfBoundsError(f"DOY must be between {MIN_DOY} and {MAX_DOY}. Got {doy}.")
        else:
            raise ValueError(f"DOY must be a whole number. Got {x}.")
    
    if isinstance(x, (str, pd.Timestamp, datetime.datetime)):
        try:
            timestamp = pd.Timestamp(x) if isinstance(x, str) else x

            if timestamp.month in EXCLUDED_MONTHS:
                return np.nan
            else:
                converter=ConvertData()
                return converter.date_to_DOY(date=timestamp, algorithm='Sturm')
        except ValueError as e:
            raise ValueError(f"Could not convert {x} to a valid DOY. {e}")
    else:
        raise TypeError(f"Input type is not supported. Expected types are int, float, str, datetime.datetime, or pd.Timestamp, got {type(x).__name__}.")