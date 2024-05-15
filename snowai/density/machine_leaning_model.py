

import xgboost as xgb
from ..utils.xgboost_utils import download_model

class SnowDensityPredictor:
    def __init__(self, model_location: str = None):

        self.model_location = model_location

    def load_model(self):

        if self.model_location is None:
            self.model_location = download_model()

        xgb_model = xgb.Booster()
        xgb_model.load_model(self.model_location)  # Load model from Uiversal Binary JSON file

        return xgb_model

    def predict(self, input_data):
        return self.model.predict(input_data)