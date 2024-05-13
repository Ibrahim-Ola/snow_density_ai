"""
The :mod:`snowai.swe` module includes statistical and machine learning models for computing snow water equivalent.
"""

from .statistical_model import HillSWE, SWE_Models

__all__ = [
    'HillSWE',
    'SWE_Models'
]