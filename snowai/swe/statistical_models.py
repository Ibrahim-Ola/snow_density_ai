
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


import argparse
import numpy as np
import pandas as pd
from typing import Optional, Any
from ..utils.hill_model_utils import swe_acc_and_abl, SWE_Hill
from ..utils.sturm_model_constants import VALID_SNOW_CLASSES
from ..density import (
    SturmDensity, 
    JonasDensity, 
    PistochiDensity
)


class HillSWE:
    def __init__(self):
        """Initialize the HillSWE class."""
        pass

    def compute_swe(self, pptwt: float, TD: float, DOY: int, snow_depth: float) -> Optional[float]:
        """
        Compute the snow water equivalent (SWE) based on precipitation weight, temperature difference, day of the year, and height or depth parameter.

        Parameters:
        ===========
            * pptwt (float): Winter precipitation in mm.
            * TD (float): Temperature difference degree celcius.
            * DOY (int): Day of the year (with October 1 as the origin).
            * snow_depth (float): Snow depth in mm.

        Returns:
        ========
            * Optional[float]: The computed snow water equivalent (cm) as a float, or None if any input is NaN.

        Raises:
        =======
            ValueError: If any of the inputs are not valid (e.g., NaN values).
        """
        # Check if any input is missing or not a number, return None if so
        if pd.isna(pptwt) or pd.isna(TD) or pd.isna(DOY) or pd.isna(snow_depth):
            return None  

        # Calculate accumulated and ablated SWE using provided formulas
        swe_preds = swe_acc_and_abl(pptwt, TD, DOY, snow_depth)

        # Calculate final SWE using the Hill model
        swe = SWE_Hill(swe_preds['swe_acc'], swe_preds['swe_abl'], DOY)

        return swe / 10  # Adjusted to convert to cm (orginally in mm)


class SWE_Models(HillSWE):
    def __init__(self, algorithm: str = 'default', **kwargs: Any):
        """
        Initialize the SWE model with a specified algorithm and additional keyword arguments.

        Parameters:
        ===========
            * algorithm (str): The name of the algorithm to use for SWE calculation.
            * kwargs (Any): Additional parameters specific to each algorithm.
        """
        super().__init__()
        self.algorithm = algorithm
        self.kwargs = kwargs

    def calculate_swe(self) -> float:
        """
        Calculate the snow water equivalent (SWE) based on the chosen algorithm and parameters.

        Returns:
        ========
            * float: The calculated snow water equivalent.

        Raises:
        =======
            * ValueError: If an unsupported algorithm is specified.
        """
        if self.algorithm.lower() == 'default':
            depth = self.kwargs.get('snow_depth', np.nan)
            density = self.kwargs.get('snow_density', np.nan)
            return self.default_SWE(depth, density)
        
        elif self.algorithm.lower() == 'hill':
            return self.compute_swe(**self.kwargs)
        
        elif self.algorithm.lower() == 'sturm':
            depth = self.kwargs.get('snow_depth', np.nan)
            DOY = self.kwargs.get('DOY', np.nan)
            snow_class = self.kwargs.get('snow_class', np.nan)
            density = SturmDensity().compute_density(snow_depth=depth, DOY=DOY, snow_class=snow_class)
            return self.default_SWE(depth, density)

        elif self.algorithm.lower() == 'jonas':
            depth = self.kwargs.get('snow_depth', np.nan)
            month = self.kwargs.get('month', np.nan)
            elevation = self.kwargs.get('elevation', np.nan)
            density = JonasDensity().compute_density(snow_depth=depth, month=month, elevation=elevation)
            return self.default_SWE(depth*100, density)

        elif self.algorithm.lower() == 'pistochi':
            density = PistochiDensity().compute_density(DOY=self.kwargs.get('DOY', np.nan))
            depth = self.kwargs.get('snow_depth', np.nan)
            return self.default_SWE(depth, density)
        
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def default_SWE(self, snow_depth: float, snow_density: float) -> float:
        """
        Calculate snow water equivalent using depth and density - the default algorithm.

        Parameters:
        ===========
            * depth (float): The depth of the snow in cm.
            * density (float): The density of the snow in g/cm^3.

        Returns:
        ========
            * float: The calculated snow water equivalent.
        """
        return snow_depth * snow_density