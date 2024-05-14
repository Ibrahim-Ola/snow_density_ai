
import datetime
import pandas as pd
from .conversion_utils import ConvertData, OutOfBoundsError


def validate_DOY(x: int | float | str | pd.Timestamp | datetime.datetime, origin: int = None) -> int:

    """
    Validates or converts an input to a day of the year (DOY).
    Accepts integer, float, string, datetime.datetime, or pd.Timestamp inputs.
    If the input is an integer, float, or a string of integer it must be between 1 and 366. 
    If the input is a string, it must be convertible to a valid date.
    """

    try:
        float_x = float(x)
    except:
        pass

    else:
        if float_x.is_integer():
            doy = int(float_x)
            if doy >= 1 and doy <= 366:
                return doy
            else:
                raise OutOfBoundsError(f"DOY must be between 1 and 366. Got {doy}.")
        else:
            raise ValueError(f"DOY must be a whole number. Got {x}.")

    if isinstance(x, (str, pd.Timestamp, datetime.datetime)):
        try:
            timestamp = pd.Timestamp(x) if isinstance(x, str) else x

            if origin < 1 or origin > 12:
                raise OutOfBoundsError(f"Origin must be between 1 and 12. Got {origin}.")

            converter=ConvertData()
            return converter.date_to_DOY(date=timestamp, origin=origin, algorithm='default')
        except ValueError as e:
            raise ValueError(f"Could not convert {x} to a valid DOY. {e}")
    else:
        raise TypeError(f"Input type is not supported. Expected types are int, float, str, datetime.datetime, or pd.Timestamp, got {type(x).__name__}.")