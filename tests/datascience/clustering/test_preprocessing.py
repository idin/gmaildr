import numpy as np
from sklearn.pipeline import Pipeline
from gmaildr.datascience.clustering.preprocessing import make_preprocessor


def test_make_preprocessor():
    # default returns a Pipeline with imputer and scaler
    pp = make_preprocessor()
    assert isinstance(pp, Pipeline)
    assert {"imputer", "scaler"} <= set(pp.named_steps.keys())

    # when both steps are disabled, returns None
    assert make_preprocessor(impute=False, scale=False) is None
