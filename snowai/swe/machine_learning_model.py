
from ..density import MachineLearningDensity


class MachineLearningSWE(MachineLearningDensity):
    
    def __init__(self, snow_depth: float):
        super().__init__()

        self.snow_depth = snow_depth

    def predict(self, input_data):
        density=super().predict(input_data)  # Call the predict method from the superclass to get the density.
        return density * self.snow_depth  # Return the density multiplied by the snow depth to get the SWE.
