
"""
Created on Tue Jan  17 11:15 2024

This script contains codes to compute snow water equivalent (SWE) using four statistical models:

    1. Sturm et al. (2010) - DOI: https://doi.org/10.1175/2010JHM1202.1
    2. Jonas et al. (2009) - DOI: https://doi.org/10.1016/j.jhydrol.2009.09.021
    3. Pistochi A. (2016) - DOI: https://doi.org/10.1016/j.ejrh.2016.03.004
    4. Hill et al. (2019) - DOI: https://doi.org/10.5194/tc-13-1767-2019

Author: Ibrahim Alabi
Email: ibrahimolalekana@u.boisestate.edu
Institution: Boise State University
"""

## Import libraries
import numpy as np
import pandas as pd
from typing import Union, Any
from ..utils.hill_model_utils import swe_acc_and_abl, SWE_Hill
from ..density import (
    SturmDensity, 
    JonasDensity, 
    PistochiDensity
)


class HillSWE:
    def __init__(self, return_type: str = 'numpy'):
        """Initialize the HillSWE class."""
        
        self.return_type = return_type

    def predict(self, data: pd.DataFrame, pptwt: str, TD: str, DOY: str, snow_depth: str, DOY_ : int = 180) -> Union[np.ndarray, pd.Series]:
        """
        Compute the snow water equivalent (SWE) based on precipitation weight, temperature difference, day of the year, and height or depth parameter.

        Parameters:
        ===========
            * data (pd.DataFrame): Input dataset containing the required columns.
            * pptwt (str): Column name for winter precipitation in mm.
            * TD (str): Column name for temperature difference in degree Celsius.
            * DOY (str): Column name for day of the year (with October 1 as the origin).
            * snow_depth (str): Column name for snow depth in mm.
            * DOY_ (int): Day of peak SWE, default is 180.

        Returns:
        ========
             * np.ndarray or pd.Series: An array or series of computed snow water equivalent (cm) values.
        """

        # Validate return_type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Invalid return type. Choose either 'numpy' or 'pandas'.")
        
        try:
            pptwt = data[pptwt].to_numpy()
            TD = data[TD].to_numpy()
            DOY = data[DOY].to_numpy()
            snow_depth = data[snow_depth].to_numpy()
        except KeyError as e:
            raise ValueError(f"Missing required column: {e.args[0]}")
        
        
        # Check for NaN values in the extracted columns
        if np.isnan(pptwt).any() or np.isnan(TD).any() or np.isnan(DOY).any() or np.isnan(snow_depth).any():
            raise ValueError("Input data contains NaN values.")  

        # Calculate accumulated and ablated SWE using provided formulas
        swe_preds = swe_acc_and_abl(pptwt=pptwt, TD=TD, DOY=DOY, h=snow_depth)

        # Calculate final SWE using the Hill model
        swe = SWE_Hill(swe_acc=swe_preds['swe_acc'], swe_abl=swe_preds['swe_abl'], DOY=DOY, DOY_=DOY_)
        
        swe_cm = swe / 10  # Adjusted to convert to cm (orginally in mm)

        if self.return_type.lower() == 'numpy':
            return swe_cm
        else:
            return pd.Series(swe_cm, index=data.index)



class StatisticalModels(HillSWE):
    def __init__(self, algorithm: str = 'default', return_type='numpy'):
        """
        Initialize the SWE model with a specified algorithm and additional keyword arguments.

        Parameters:
        ===========
            * algorithm (str): The name of the algorithm to use for SWE calculation.
        """
        super().__init__()
        self.algorithm = algorithm
        self.return_type = return_type

    def predict(self, 
            data: pd.DataFrame,
            depth_col: str = None,
            density_col: str = None,
            **kwargs: Any
        ) -> np.ndarray | pd.Series:
        """
        Calculate the snow water equivalent (SWE) based on the chosen algorithm and parameters.

        Returns:
        ========
            * np.ndarray or pd.Series: An array or series of computed snow water equivalent (cm) values.

        Raises:
        =======
            * ValueError: If an unsupported algorithm is specified.
        """

        if self.algorithm.lower() == 'default':
            
            # Extract snow depth and density columns from the input data
            try:
                snow_depth = data[depth_col].to_numpy() if depth_col else data[kwargs.get('snow_depth')].to_numpy()
                snow_density = data[density_col].to_numpy() if density_col else data[kwargs.get('snow_density')].to_numpy()
            except KeyError as e:
                raise ValueError(f"Missing required column: {e.args[0]}")
            
            # Check for NaN values in the extracted columns          
            if np.isnan(snow_depth).any() or np.isnan(snow_density).any():
                raise ValueError("Input data contains NaN values.")
            
            SWE = self.default_SWE(snow_depth, snow_density)

            if self.return_type.lower() == 'pandas':
                return pd.Series(SWE, index=data.index)
            return SWE

        
        if self.algorithm.lower() == 'hill':
            SWE = super().predict(data, **kwargs)

            if self.return_type.lower() == 'pandas':
                return pd.Series(SWE, index=data.index)
            return SWE
        
        elif self.algorithm.lower() == 'sturm':
            density = SturmDensity(return_type='numpy').predict(data, **kwargs)
            depth = kwargs.get('snow_depth')

            if self.return_type.lower() == 'pandas':
                return pd.Series(self.default_SWE(depth, density), index=data.index)
            return self.default_SWE(depth, density)

            
        elif self.algorithm.lower() == 'jonas':
            density = JonasDensity(return_type='numpy').predict(data, **kwargs)
            depth = kwargs.get('snow_depth')
            
            if self.return_type.lower() == 'pandas':
                return pd.Series(self.default_SWE(depth, density), index=data.index)
            return self.default_SWE(depth, density)

        elif self.algorithm.lower() == 'pistochi':
            density = PistochiDensity(return_type='numpy').predict(data, **kwargs)
            depth = kwargs.get('snow_depth')
           
            if self.return_type.lower() == 'pandas':
                return pd.Series(self.default_SWE(depth, density), index=data.index)
            return self.default_SWE(depth, density)
        
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}. Choose either 'default', 'hill', 'sturm', 'jonas', or 'pistochi'.")
    
    def default_SWE(self, snow_depth: np.ndarray, snow_density: np.ndarray) -> np.ndarray:
        """
        Calculate snow water equivalent using depth and density - the default algorithm.

        Parameters:
        ===========
            * depth (str): snow depth in cm
            * density (str): Csnow density in g/cm^3

        Returns:
        ========
            * np.ndarray: An array of computed snow water equivalent (cm) values.
        """

        # Calculate SWE using the default algorithm
        SWE= snow_depth * snow_density
        return SWE