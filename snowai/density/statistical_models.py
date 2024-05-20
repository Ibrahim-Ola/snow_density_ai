
"""
Created on Tue Jan  17 11:15 2024

This script contains codes to compute snow density using three statistical models:

    1. Sturm et al. (2010) - DOI: https://doi.org/10.1175/2010JHM1202.1
    2. Jonas et al. (2009) - DOI: https://doi.org/10.1016/j.jhydrol.2009.09.021
    3. Pistochi A. (2016) - DOI: https://doi.org/10.1016/j.ejrh.2016.03.004

Author: Ibrahim Alabi
Email: ibrahimolalekana@u.boisestate.edu
Institution: Boise State University
"""

## Import libraries
import numpy as np
import pandas as pd
from ..utils.xgboost_utils import validate_DOY
from ..utils.jonas_model_utils import jonas_model_params, validate_month
from ..utils.sturm_model_utils import sturm_model_params, validate_snow_class, validate_SturmDOY



class SturmDensity:

    """
    A class for computing snow density using the Sturm Equation.
    """

    def __init__(self, return_type: str = 'numpy'):
        """Initialize the SturmDensity class."""
        
        self.return_type = return_type

    def rho(self, h: np.ndarray, doy: np.ndarray, rho_max: int, rho_0: int, k1: int, k2: int) -> np.ndarray:

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * h (np.ndarray): The snow depth in cm.
            * doy (np.ndarray): The day of the year. See link to original paper in the preamble for more information on how to compute doy. 
            * rho_max (float): A constant in g/cm^3. See link to original paper in the preamble.
            * rho_0 (float): A constant in g/cm^3. See link to original paper in the preamble.
            * k1 (float): A constant. See link to original paper in the preamble.
            * k2 (float): A constant. See link to original paper in the preamble.

        Returns:
        ========
            * np.ndarray: The function returns the snow density in kg/m^3.
        """

        density_est = (rho_max - rho_0) * (1 - np.exp(-k1 * h - k2 * doy)) + rho_0
        return density_est

    def predict(
        self,
        data: pd.DataFrame, 
        snow_depth: str, 
        DOY: str, 
        snow_class: str
    ) -> float:

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * data (pd.DataFrame): Input dataset containing the required columns.
            * snow_depth (str): Column name for snow depth in cm.
            * DOY (str): The column name for the day of the year.  See link to original paper in the preamble for more information on how to compute DOY. 
            * snow_class (str): The column name for the snow type. Must be one of 'alpine', 'maritime', 'prairie', 'tundra' or 'taiga'.

        Returns:
        ========
            * np.ndarray or pd.Series: The snow density in g/cm^3
        """

        #vaidate return type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Invalid return type. Must be either 'numpy' or 'pandas'.")

        ## Extract the required columns
        try:
            snow_depth = data[snow_depth].to_numpy()
            DOY = data[DOY].to_numpy()
            snow_class = data[snow_class].to_numpy()
        except KeyError as e:
            raise ValueError(f"Missing required column: {e.args[0]}")
        
        # Check for NaN values in the extracted columns
        if np.isnan(snow_depth).any() or np.isnan(DOY).any() or np.isnan(snow_class).any():
            raise ValueError("Input data contains NaN values.")

        snow_class = validate_snow_class(snow_class)
        DOY = validate_SturmDOY(DOY)


        density = self.rho(
                h=snow_depth,
                doy=DOY,
                rho_max=sturm_model_params[snow_class]['rho_max'],
                rho_0=sturm_model_params[snow_class]['rho_0'],
                k1=sturm_model_params[snow_class]['k1'],
                k2=sturm_model_params[snow_class]['k2']
            )
        
        if self.return_type.lower() == 'numpy':
            return density
        else:
            return pd.Series(density, index=data.index)
    
class JonasDensity:

    """
    A class for computing snow density using the Jonas Model.
    """

    def __init__(self, return_type: str = 'numpy'):
        """Initialize the JonasDensity class."""
        
        self.return_type = return_type

    def rho(self, h, a, b):

        """
        A function to compute snow density using the Jonas Model.

        Parameters:
        ===========
            * h (float): The snow depth in meters.
            * a (float): A constant.
            * b (float): A constant.

        Returns:
        ========
            * The function returns the snow density in kg/m^3.
        """

        density_est = (a * h) + b
        return density_est

    def predict(
        self,
        data: pd.DataFrame, 
        snow_depth: str,
        month: str,
        elevation: str
    ) -> np.ndarray | pd.Series:

        """
        A function to compute snow density using the Jonas Model.

        Parameters:
        ===========
            * data (pd.DataFrame): Input dataset containing the required columns.
            * snow_depth (str): Column name for snow depth in cm.
            * month (str): The column name for the month.
            * elevation (str): The column name for the elevation in meters.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """

        #vaidate return type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Invalid return type. Must be either 'numpy' or 'pandas'.")
        
        ## Extract the required columns
        try:
            snow_depth = data[snow_depth].to_numpy()
            month = data[month].to_numpy()
            elevation = data[elevation].to_numpy()
        except KeyError as e:
            raise ValueError(f"Missing required column: {e.args[0]}")
        
        # Check for NaN values in the extracted columns
        if np.isnan(snow_depth).any() or np.isnan(month).any() or np.isnan(elevation).any():
            raise ValueError("Input data contains NaN values.")
        

        # Validate month
        month = validate_month(month)

        elevation_ = np.where(
            elevation < 1400, '<1400m',
            np.where(elevation < 2000, '[1400, 2000)m', '>=2000m')
        )

        # Initialize arrays for parameters a and b
        a = np.full_like(month, np.nan, dtype=float)
        b = np.full_like(month, np.nan, dtype=float)

        # Create a function to map parameters
        def get_params(month, elev_cat):
            if pd.isna(month) or month not in jonas_model_params:
                return np.nan, np.nan
            params = jonas_model_params[month][elev_cat]
            return params['a'], params['b']

        # Vectorize the get_params function
        vec_get_params = np.vectorize(get_params, otypes=[float, float])

        # Apply the function to get a and b
        a, b = vec_get_params(month, elevation_)

        # Compute density
        density = self.rho(
            h=snow_depth,
            a=a,
            b=b
        )

        density /= 1000  # Convert to g/cm^3
        
        if self.return_type.lower() == 'numpy':
            return density
        else:
            return pd.Series(density, index=data.index)
    
class PistochiDensity:

    def __init__(self, return_type: str = 'numpy'):
        """Initialize the PistochiDensity class."""
        
        self.return_type = return_type

    def predict(self, data: pd.DataFrame, DOY: str) -> float:

        """
        A function to compute snow density using the Pistochi Model.

        Parameters:
        ===========
            * DOY (int | float | str | pd.Timestamp | datetime.datetime): The day of the year.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """

        #vaidate return type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Invalid return type. Must be either 'numpy' or 'pandas'.")

        ## Extract the required columns
        try:
            DOY = data[DOY].to_numpy()
        except KeyError as e:
            raise ValueError(f"Missing required column: {e.args[0]}")
        
        # Check for NaN values in the extracted columns
        if np.isnan(DOY).any():
            raise ValueError("Input data contains NaN values.")
        

        DOY = validate_DOY(DOY, origin=11)
        density_est = 200 + (DOY + 61)

        if self.return_type.lower() == 'numpy':
            return density_est/1000
        
        else:
            return pd.Series(density_est/1000, index=data.index)