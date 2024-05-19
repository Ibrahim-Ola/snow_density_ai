
import numpy as np
import pandas as pd
from typing import Dict


def swe_acc_and_abl(
    pptwt: np.ndarray | pd.Series,
    TD: np.ndarray | pd.Series,
    DOY: np.ndarray | pd.Series,
    h: np.ndarray | pd.Series
) -> Dict[str, np.ndarray]:
    """
    Calculate accumulated and ablated snow water equivalent using Hill et al. (2019).

    Parameters:
    ===========
        * pptwt (np.ndarray): Winter precipitation in mm.
        * TD (np.ndarray): Temperature difference degree Celsius.
        * DOY (np.ndarray): Day of the year (with October 1 as the origin).
        * h (np.ndarray): Snow depth in mm.

    Returns:
    ========
        * Dict[str, np.ndarray]: A dictionary with keys 'swe_acc' and 'swe_abl' representing
                                 accumulated (mm) and ablated (mm) snow water equivalent, respectively.
    """

    # Convert inputs to numpy arrays if they are pandas Series
    pptwt = np.asarray(pptwt)
    TD = np.asarray(TD)
    DOY = np.asarray(DOY)
    h = np.asarray(h)

    
    A, a1, a2, a3, a4 = 0.0533, 0.9480, 0.1701, -0.1314, 0.2922
    B, b1, b2, b3, b4 = 0.0481, 1.0395, 0.1699, -0.0461, 0.1804
    
    with np.errstate(all='ignore'):
        swe_acc = (A * h ** a1) * (pptwt ** a2) * (TD ** a3) * (DOY ** a4)
        swe_abl = (B * h ** b1) * (pptwt ** b2) * (TD ** b3) * (DOY ** b4)

        # Identify invalid computations and set them to np.nan
        swe_acc = np.where(np.isfinite(swe_acc), swe_acc, np.nan)
        swe_abl = np.where(np.isfinite(swe_abl), swe_abl, np.nan)

    return {'swe_acc': swe_acc, 'swe_abl': swe_abl}
    

def SWE_Hill(swe_acc: np.ndarray, swe_abl: np.ndarray, DOY: int, DOY_: int = 180) -> np.ndarray:
    """
    Compute the snow water equivalent on a particular day using Hill et al. (2019)'s model.

    Parameters:
    ===========
        * swe_acc (np.ndarray): Accumulated snow water equivalent (mm).
        * swe_abl (np.ndarray): Ablated snow water equivalent (mm).
        * DOY (int): Day of the year (with October 1 as the origin).
        * DOY_ (int): Day of peak SWE, default is 180.

    Returns:
    ========
        * np.ndarray: Computed snow water equivalent for the given day (mm).
    """
    first = swe_acc * 0.5 * (1 - np.tanh(0.01 * (DOY - DOY_)))
    second = swe_abl * 0.5 * (1 + np.tanh(0.01 * (DOY - DOY_)))
    return first + second