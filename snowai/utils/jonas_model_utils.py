## Set Model Params

jonas_model_params = {
    'january': {'>=2000m': {"b": 206, "a": 52}, '[1400, 2000)m': {"b": 208, "a": 47}, '<1400m': {"b": 235, "a": 31}},
    'february': {'>=2000m': {"b": 217, "a": 46}, '[1400, 2000)m': {"b": 218, "a": 52}, '<1400m': {"b": 279, "a": 9}},
    'march': {'>=2000m': {"b": 272, "a": 26}, '[1400, 2000)m': {"b": 281, "a": 31}, '<1400m': {"b": 333, "a": 3}},
    'april': {'>=2000m': {"b": 331, "a": 9}, '[1400, 2000)m': {"b": 354, "a": 15}, '<1400m': {"b": 347, "a": 25}},
    'may': {'>=2000m': {"b": 378, "a": 21}, '[1400, 2000)m': {"b": 409, "a": 29}, '<1400m': {"b": 413, "a": 19}},
    'june': {'>=2000m': {"b": 452, "a": 8}, '[1400, 2000)m': {"b": None, "a": None}, '<1400m': {"b": None, "a": None}},
    'july': {'>=2000m': {"b": 470, "a": 15}, '[1400, 2000)m': {"b": None, "a": None}, '<1400m': {"b": None, "a": None}},
    'august': {'>=2000m': {"b": None, "a": None}, '[1400, 2000)m': {"b": None, "a": None}, '<1400m': {"b": None, "a": None}},
    'september': {'>=2000m': {"b": None, "a": None}, '[1400, 2000)m': {"b": None, "a": None}, '<1400m': {"b": None, "a": None}},
    'october': {'>=2000m': {"b": None, "a": None}, '[1400, 2000)m': {"b": None, "a": None}, '<1400m': {"b": None, "a": None}},
    'november': {'>=2000m': {"b": 206, "a": 47}, '[1400, 2000)m': {"b": 183, "a": 35}, '<1400m': {"b": 149, "a": 37}},
    'december': {'>=2000m': {"b": 203, "a": 52}, '[1400, 2000)m': {"b": 190, "a": 47}, '<1400m': {"b": 201, "a": 26}}
}

## Create Month Mapping

MONTH_MAPPING = {
    '1': 'january', '2': 'february', '3': 'march',
    '4': 'april', '5': 'may', '6': 'june',
    '7': 'july', '8': 'august', '9': 'september',
    '10': 'october', '11': 'november', '12': 'december',
    'jan': 'january', 'feb': 'february', 'mar': 'march',
    'apr': 'april', 'may': 'may', 'jun': 'june',
    'jul': 'july', 'aug': 'august', 'sep': 'september',
    'oct': 'october', 'nov': 'november', 'dec': 'december'
}


## Validate Month
def validate_month(month: str) -> str:
    """
    A function to validate the month. It accepts both numeric and short string representations.
    """
    
    # Convert numeric inputs to strings if necessary
    if isinstance(month, int):
        if 1 <= month <= 12:
            month = str(month)
        else:
            raise ValueError(f"Invalid month! Month integer must be between 1 and 12.")

    # Ensure the input is a string for further processing
    elif isinstance(month, str):
        month = month.strip().lower()  # Clean up the input string

        if month.isdigit():
            if 1 <= int(month) <= 12:
                month = str(int(month))
            else:
                raise ValueError(f"Invalid month! Month integer must be between 1 and 12.")

    else:
        raise ValueError(f"Month input must be an integer or string.")
    
    if month in MONTH_MAPPING:
        return MONTH_MAPPING[month]

    elif month in MONTH_MAPPING.values():
        return month

    else:
        raise ValueError(f"Invalid month! Please choose from: {', '.join(MONTH_MAPPING.keys())} or {', '.join(list(MONTH_MAPPING.values())[:12])}.")