
import numpy as np
import pandas as pd
from .conversion_utils import ConvertData
from ._other_utils import get_cache_path, ensure_file_available


def download_model():
    """
    Downloads the machine learning model.
    """

    ensure_file_available("density_model.ubj")
    return get_cache_path("density_model.ubj")


def validate_DOY(x: pd.Series | np.ndarray | list, origin: int = None) -> np.ndarray:
    """
    Validates numeric inputs directly within bounds or converts date-like inputs into Day of Year (DOY) with a particular origin (defaults to October 1).
    Returns NaN for out-of-range DOY or dates in excluded months (July to September).

    Parameters:
        x (pd.Series | np.ndarray | list): The input to validate and convert.

    Returns:
        np.ndarray: The Sturm DOY or NaN if the input is invalid or in the excluded range.
    """
    MIN_DOY = 1
    MAX_DOY = 366

    if not isinstance(x, pd.Series):
        x = pd.Series(x)
    

    # Process numeric inputs directly
    numeric = pd.to_numeric(x, errors='coerce')

    if not numeric.isna().all():
        validated_doy=np.where((numeric >= MIN_DOY) & (numeric <= MAX_DOY), numeric, np.nan)
        return validated_doy
    
    else:
        dates = pd.to_datetime(x, errors='coerce')

        if not dates.isna().all():
            converter=ConvertData()
            validated_doy=converter.date_to_DOY(dates=dates, origin=origin, algorithm='default')
            return validated_doy
        
        else:
            raise ValueError("Input contains no valid DOY or dates.")