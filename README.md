# SnowDensityAI
SnowDensityAI: statistical and machine learning model for snow density and snow water equivalent prediction


## Benchmarks

* RMSE

![alt text](https://github.com/Ibrahim-Ola/snow_density_ai/blob/main/plots/rmse_model_comparison.png)

<!-- * $R^2$

![alt text](https://github.com/Ibrahim-Ola/snow_density_ai/blob/main/plots/rsq_model_comparison.png) -->

## Software and hardware list

| Software used | Link to the software  | Hardware specifications  | OS required |
|:---:  |:---:  |:---:  |:---:  |
| Python 3.11.5 | [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv) | This code should work on any recent PC/Laptop | Linux (any), MacOS, Windows|

## Installation

To use this package, you need to have Python installed. I recommend using the [pyenv](https://github.com/pyenv/pyenv) utility program. `pyenv` allows you to install different versions of Python and seamlessly switch between them.

### 1. Install `pyenv`

Please follow the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) to install `pyenv` for your operation system (OS).

Setup your virtual environment if you want or otherwise move to step 2.

```bash
pyenv install 3.11.5
mkdir density_preds
cd density_preds
pyenv local 3.11.5
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 3. Clone the Repository

```bash
git clone https://github.com/Ibrahim-Ola/snow_density_ai.git
cd snow_density_ai
```

### 4. Install Source Code 

```bash
pip install .
```

## Usage

```python
# Load libraries
from snowai.density import (
    JonasDensity, 
    PistochiDensity, 
    SturmDensity,
    MachineLearningDensity
)
import pandas as pd

# Create df

date=["2012-02-06", "2017-04-27", "2007-12-27"]
depth_cm=[30.48, 134.62, 149.86]
month=[2, 4, 12]
elevation_m=[652.272, 2855.976, 2743.200]
snow_class=['Ephemeral', 'Taiga', 'Taiga']


df_ = pd.DataFrame({
    'date': date,
    'depth_cm': depth_cm,
    'month': month,
    'elevation_m': elevation_m,
    'snow_class': snow_class
})

df=df_.assign(depth_m = df_['depth_cm'] / 100)


# Statistical models

## Predict density using Jonas model
jonas=JonasDensity(return_type='pandas')

jonas.predict(
    data=df,
    snow_depth='depth_m',
    month='month',
    elevation='elevation_m'
)

# Predict density using Pistochi model
pistochi=PistochiDensity(return_type='pandas')

pistochi.predict(
    data=df,
    DOY='date'
)

## Predict density using Sturm model
sturm=SturmDensity(return_type='pandas')

sturm.predict(
    data=df,
    DOY='date',
    snow_class='snow_class',
    snow_depth='depth_cm'
)

## Predict with ML model
ml=MachineLearningDensity(return_type='pandas') ## This will download the ml model the first time

ml.predict(
    data=df,
    snow_class='snow_class',
    snow_depth='depth_cm',
    elevation='elevation_m',
    tavg='tavg',
    tmin='tmin',
    tmax='tmax',
    doy='date'
)
```