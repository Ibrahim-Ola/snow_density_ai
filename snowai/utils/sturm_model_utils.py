
## Import libraries
import datetime
import numpy as np
import pandas as pd
from pandas import Timestamp
from .conversion_utils import ConvertData
from ._other_utils import OutOfBoundsError

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

def validate_snow_class(snow_classes: np.ndarray | list | pd.Series) -> np.ndarray:
    """
    A function to validate snow classes. This function accepts numpy arrays, lists, or pandas Series of snow classes and returns an array of validated snow classes.
    It consistently returns a numpy array regardless of the input type.

    Parameters:
    ===========
        * snow_classes (np.ndarray | list | pd.Series): Array, list, or Series of snow classes as strings.

    Returns:
    ========
        * np.ndarray: Array where valid classes are returned in lowercase and invalid classes are replaced with np.nan.
    """

    # Convert input to a NumPy array if it isn't already (handles lists and pandas Series seamlessly)
    if not isinstance(snow_classes, np.ndarray):
        snow_classes = np.asarray(snow_classes, dtype=str)

    # Convert all entries to lowercase
    lower_classes = np.char.lower(snow_classes)

    # Create a mask of valid entries
    valid_mask = np.isin(lower_classes, [s.lower() for s in VALID_SNOW_CLASSES])

    # Apply mask and replace invalid entries with np.nan
    validated_classes = np.where(valid_mask, lower_classes, np.nan)

    return validated_classes

def validate_SturmDOY(x: pd.Series | np.ndarray | list) -> np.ndarray:
    """
    Validates numeric inputs directly within bounds or converts date-like inputs into the Sturm et al. (2010) Day of Year (DOY).
    Returns NaN for out-of-range DOY or dates in excluded months (July to September).

    Sturm et al. (2010) - DOI: https://doi.org/10.1175/2010JHM1202.1

    Parameters:
        x (pd.Series | np.ndarray | list): The input to validate and convert.

    Returns:
        np.ndarray: The Sturm DOY or NaN if the input is invalid or in the excluded range.
    """
    MIN_DOY = -92
    MAX_DOY = 182

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
            validated_doy=converter.date_to_DOY(dates, origin=10, algorithm='Sturm')
            return validated_doy
        
        else:
            raise ValueError("Input contains no valid DOY or dates.")