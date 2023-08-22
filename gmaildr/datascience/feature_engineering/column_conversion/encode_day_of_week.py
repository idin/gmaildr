import pandas as pd
from typing import Optional
from .convert_to_sin_cos import convert_to_sin, convert_to_cos

def _map_day_of_week_to_int(day_of_week) -> Optional[int]:
    if day_of_week is None:
        return None

    mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    key = day_of_week.lower()
    if key not in mapping:
        raise ValueError(f"Invalid day of week: {day_of_week}")
    return mapping[key]

def convert_day_of_week_to_int(values: pd.Series) -> pd.Series:
    return values.apply(_map_day_of_week_to_int)

def encode_day_of_week_to_sin(values: pd.Series) -> pd.Series:
    range_of_values = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range_of_values = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_sin(values, value_range=range_of_values)

def encode_day_of_week_to_cos(values: pd.Series) -> pd.Series:
    range_of_values = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range_of_values = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_cos(values, value_range=range_of_values)

def encode_day_of_week_to_sin_cos_series(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    range_of_values = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range_of_values = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_sin(values, value_range=range_of_values), convert_to_cos(values, value_range=range_of_values)


def encode_day_of_week_to_sin_cos(
    *,
    dataframe: pd.DataFrame,
    column: str,
    suffixes: tuple[str, str] = ('_sin', '_cos'),
    drop_original_columns: bool = True,
    in_place: bool = False
) -> Optional[pd.DataFrame]:
    if not in_place:
        dataframe = dataframe.copy()

    sin_col = column + suffixes[0]
    cos_col = column + suffixes[1]
    
    sin_series, cos_series = encode_day_of_week_to_sin_cos_series(dataframe[column])
    dataframe[sin_col] = sin_series
    dataframe[cos_col] = cos_series
    
    if drop_original_columns:
        dataframe.drop(columns=[column], inplace=True)

    return None if in_place else dataframe