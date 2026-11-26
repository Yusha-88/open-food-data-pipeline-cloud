import pipeline
import pandas as pd
import pytest

def test_check_url_response():
    assert pipeline.check_url_response("https://www.google.com") == True
    assert pipeline.check_url_response("https://www.google.com/%") == False


def test_load_df_to_database():
    # Create data frame
    test_data = {"nutriscore_score": [2.0]}
    numeric_cols=["nutriscore_score"]
    test_df = pd.DataFrame(test_data)
    assert pipeline.load_df_to_database([test_df], numeric_cols) == None
