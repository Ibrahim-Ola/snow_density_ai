
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
import datetime
import argparse
import numpy as np
import pandas as pd
from ..utils import validate_DOY
from ..utils.jonas_model_constants import jonas_model_params, validate_month, MONTH_MAPPING
from ..utils.sturm_model_constants import sturm_model_params, validate_snow_class, validate_SturmDOY, VALID_SNOW_CLASSES



class SturmDensity:

    """
    A class for computing snow density using the Sturm Equation.
    """

    def __init__(self):
        pass

    def rho(self, h, doy, rho_max, rho_0, k1, k2):

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * h (float): The snow depth in cm.
            * doy (int): The day of the year. See link to original paper in the preamble for more information on how to compute doy. 
            * rho_max (float): A constant in g/cm^3. See link to original paper in the preamble.
            * rho_0 (float): A constant in g/cm^3. See link to original paper in the preamble.
            * k1 (float): A constant. See link to original paper in the preamble.
            * k2 (float): A constant. See link to original paper in the preamble.

        Returns:
        ========
            * The function returns the snow density in kg/m^3.
        """

        density_est = (rho_max - rho_0) * (1 - np.exp(-k1 * h - k2 * doy)) + rho_0
        return density_est

    def compute_density(
        self, 
        snow_depth: float, 
        DOY: int | float | str | pd.Timestamp | datetime.datetime, 
        snow_class: str
    ) -> float:

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * snow_depth (float): The snow depth in cm.
            * DOY (int | float | str | pd.Timestamp | datetime.datetime): The day of the year. See link to original paper in the preamble for more information on how to compute DOY. 
            * snow_class (str): The snow type. Must be one of 'alpine', 'maritime', 'prairie', 'tundra' or 'taiga'.

        Returns:
        ========
            * The function returns the snow density in g/cm^3 or raises a ValueError if the snow class is not found.
        """


        # TODO: Remove the first check in the final package.

        if pd.isna(DOY):
            return np.nan

        snow_class = validate_snow_class(snow_class)
        DOY = validate_SturmDOY(DOY)

        if DOY is np.nan or snow_class is np.nan:
            return np.nan


        density = self.rho(
                h=snow_depth,
                doy=DOY,
                rho_max=sturm_model_params[snow_class]['rho_max'],
                rho_0=sturm_model_params[snow_class]['rho_0'],
                k1=sturm_model_params[snow_class]['k1'],
                k2=sturm_model_params[snow_class]['k2']
            )
        
        return density
    
class JonasDensity:

    """
    A class for computing snow density using the Jonas Model.
    """

    def __init__(self):
        pass

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

    def compute_density(
        self, 
        snow_depth: float,
        month: str,
        elevation: float
    ) -> float:

        """
        A function to compute snow density using the Jonas Model.

        Parameters:
        ===========
            * snow_depth (float): The snow depth in meters.
            * month (str): The month. Must be one of 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov' or 'dec'.
            * elevation (float): The elevation in meters.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """
        
        if elevation < 1400:
            elevation_ = '<1400m'
        elif elevation >= 1400 and elevation < 2000:
            elevation_ = '[1400, 2000)m'
        else:
            elevation_ = '>=2000m'

        month = validate_month(month)

        a = jonas_model_params[month][elevation_]['a']
        b = jonas_model_params[month][elevation_]['b']

        if a is None or b is None:
            return np.nan

        else:
            density = self.rho(
                h=snow_depth,
                a=a,
                b=b
            )
    
        
        return density/1000
    
class PistochiDensity:

    def __init__(self):
        pass

    def compute_density(self, DOY: int | float | str | pd.Timestamp | datetime.datetime) -> float:

        """
        A function to compute snow density using the Pistochi Model.

        Parameters:
        ===========
            * DOY (int | float | str | pd.Timestamp | datetime.datetime): The day of the year.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """
        DOY = validate_DOY(DOY, origin=11)
        density_est = 200 + (DOY + 61)
        return density_est/1000
    
if __name__ == "__main__":

    help_snow_class="The snow class. See Matthew Sturm and Glen E. Liston 2001."

    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Compute snow density using Statistical Models.')
    subparsers = parser.add_subparsers(dest='model', help='Choose the model of interest.')

    # Create the parser for the SturmDensity model
    parser_sturm = subparsers.add_parser('sturm', help='Sturm Density Model')
    parser_sturm.add_argument('--snow_depth', type=float, required=True, help='Snow depth in meters.')
    parser_sturm.add_argument('--DOY', required=True, help='Day of the year.')
    parser_sturm.add_argument('--snow_class', type=str, required=True, choices=VALID_SNOW_CLASSES, help=f'{help_snow_class}')


    # Create the parser for the JonasDensity model
    parser_jonas = subparsers.add_parser('jonas', help='Jonas Density Model')
    parser_jonas.add_argument('--snow_depth', type=float, required=True, help='Snow depth in meters.')
    parser_jonas.add_argument('--month', type=str, required=True, help=f"Month. Must be one of {', '.join(MONTH_MAPPING.keys())}.")
    parser_jonas.add_argument('--elevation', type=float, required=True, help='Elevation in meters.')

    # Create the parser for the PistochiDensity model
    parser_pistochi = subparsers.add_parser('pistochi', help='Pistochi Density Model')
    parser_pistochi.add_argument('--DOY', required=True, help='Day of the year.')

    args = parser.parse_args()

    if args.model.lower() == 'sturm':
        density = SturmDensity().compute_density(
            snow_depth=args.snow_depth,
            DOY=args.DOY,
            snow_class=args.snow_class
        )
        print(density)
    
    elif args.model.lower() == 'jonas':
        density = JonasDensity().compute_density(
            snow_depth=args.snow_depth,
            month=args.month,
            elevation=args.elevation
        )
        print(density)

    elif args.model.lower() == 'pistochi':
        density = PistochiDensity().compute_density(
            DOY=args.DOY
        )
        print(density)

    else:
        parser.print_help()
    