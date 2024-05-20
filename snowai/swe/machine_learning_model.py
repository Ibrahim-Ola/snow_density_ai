import numpy as np
import pandas as pd
from ..density import MachineLearningDensity


class MachineLearningSWE(MachineLearningDensity):
    
    def __init__(self, return_type: str = 'numpy'):
        super().__init__()

        self.return_type = return_type

    def predict(self, input_data: pd.DataFrame, **kwargs) -> np.ndarray | pd.Series:
        """
        A function to compute snow water equivalent using the machine learning model.
        """
        
        # validate return type
        if self.return_type.lower() not in ['numpy', 'pandas']:
            raise ValueError("Unsupported return type. Choose either 'numpy' or 'pandas'.")
        
        # preprocess and predict
        density_preds = super().predict(data=input_data, **kwargs)
        snow_depth = input_data[kwargs.get('snow_depth')].to_numpy()

        SWE=density_preds * snow_depth

        if self.return_type.lower() == 'pandas':
            return pd.Series(SWE, index=input_data.index)
        return SWE
