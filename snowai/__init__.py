"""
The :mod:`snowai` module includes functions to compute snow density and SWE.
"""

PACKAGE_NAME = 'snowai'

def package_info():
    return f"This is the {PACKAGE_NAME} package."


__all__ = [
    'swe',
    'density'
]