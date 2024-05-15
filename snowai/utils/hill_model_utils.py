
import warnings
import numpy as np
from typing import Dict

def swe_acc_and_abl(pptwt: float, TD: float, DOY: int, h: float) -> Dict[str, float]:
    """
    Calculate accumulated and ablated snow water equivalent using Hill et al. (2019).

    Parameters:
    ===========
        * pptwt (float): Winter precipitation in mm.
        * TD (float): Temperature difference degree celcius.
        * DOY (int): Day of the year (with October 1 as the origin).
        * h (float): Snow depth in mm.

    Returns:
    ========
        * Dict[str, float]: A dictionary with keys 'swe_acc' and 'swe_abl' representing
                            accumulated (mm) and ablated (mm) snow water equivalent, respectively.
    """

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            A, a1, a2, a3, a4 = 0.0533, 0.9480, 0.1701, -0.1314, 0.2922
            B, b1, b2, b3, b4 = 0.0481, 1.0395, 0.1699, -0.0461, 0.1804

            swe_acc = (A * h ** a1) * (pptwt ** a2) * (TD ** a3) * (DOY ** a4)
            swe_abl = (B * h ** b1) * (pptwt ** b2) * (TD ** b3) * (DOY ** b4)

            return {'swe_acc': swe_acc, 'swe_abl': swe_abl}
        
    except RuntimeWarning as e:
        return {'swe_acc': np.nan, 'swe_abl': np.nan}
    
    except Exception as e:
        return {'swe_acc': np.nan, 'swe_abl': np.nan}
    

def SWE_Hill(swe_acc: float, swe_abl: float, DOY: int, DOY_: int = 180) -> float:
    """
    Compute the snow water equivalent on a particular day using Hill et al. (2019)'s model.

    Parameters:
    ===========
        * swe_acc (float): Accumulated snow water equivalent (mm).
        * swe_abl (float): Ablated snow water equivalent (mm).
        * DOY (int): Day of the year (with October 1 as the origin).
        * DOY_ (int): Day of peak SWE, default is 180.

    Returns:
    ========
        * float: Computed snow water equivalent for the given day (mm).
    """
    first = swe_acc * 0.5 * (1 - np.tanh(0.01 * (DOY - DOY_)))
    second = swe_abl * 0.5 * (1 + np.tanh(0.01 * (DOY - DOY_)))
    return first + second