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
from snowai import density
```