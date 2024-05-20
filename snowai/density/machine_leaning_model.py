
import numpy as np
import pandas as pd
import xgboost as xgb
from ..utils import clean_cache
from ..utils.sturm_model_utils import validate_snow_class
from ..utils.xgboost_utils import download_model, load_preprocessor, validate_DOY

VALID_SNOW_CLASSES = ['alpine', 'maritime', 'prairie', 'tundra', 'taiga', 'ephemeral']

class MachineLearningDensity:
    def __init__(self, model_location: str = None, return_type: str = 'numpy'):
        self.model_location = model_location
        self.return_type = return_type
        self.model = self.load_model()

    def load_model(self):

        if self.model_location is None:
            self.model_location = download_model()

        xgb_model = xgb.Booster()
        xgb_model.load_model(self.model_location)  # Load model from Uiversal Binary JSON file
        
        return xgb_model
    
    def preprocess_data(self, input_data):
        preprocessor = load_preprocessor()
        return preprocessor.transform(input_data)

    def predict(
        self,
        data: pd.DataFrame,
        snow_class: str,
        elevation: str,
        snow_depth: str,
        tavg: str,
        tmin: str,
        tmax: str,
        doy: str
     ) -> np.ndarray | pd.Series:
        """
        A function to compute snow density using the machine learning model.
        """

        # validate retune type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Unsupported return type. Choose either 'numpy' or 'pandas'.")
        
        # Create a DataFrame from the input data
        try:
            input_data = pd.DataFrame(
                {
                    'Snow_Class': data[snow_class],
                    'Elevation': data[elevation],
                    'Snow_Depth': data[snow_depth],
                    'TAVG': data[tavg],
                    'TMIN': data[tmin],
                    'TMAX': data[tmax],
                    'DOY': data[doy]
                }
            )
        except KeyError as e:
            raise ValueError(f"Missing required column: {e.args[0]}")

        # Check for NaN values in the extracted columns
        if input_data.isna().any().any():
            raise ValueError("Input data contains NaN values.")
        
        # validate snow class and DOY

        data_for_preprocessing=(
            input_data
            .assign(
                Snow_Class=lambda x: validate_snow_class(x['Snow_Class'], VALID_SNOW_CLASSES),
                DOY=lambda x: validate_DOY(x['DOY'], origin=10)
            )
        )
        
        # Preprocess the input data
        preprocessed_data = self.preprocess_data(input_data=data_for_preprocessing)
        xgb_input = xgb.DMatrix(preprocessed_data)

        density = self.model.predict(xgb_input)

        if self.return_type.lower() == 'numpy':
            return density
        else:
            return pd.Series(density, index=data.index)
        
    
    def clear_cache(self):
        clean_cache('density')
