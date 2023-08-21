import pytest

from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from gmaildr.data.email_dataframe.email_ml_dataframe import Email_ML_DataFrame
import pandas as pd

def test_passing_pandas_df_to_ml_df_should_fail():
    with pytest.raises(TypeError):
        Email_ML_DataFrame(pd.DataFrame())