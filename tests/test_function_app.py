import pandas as pd
from function_app import detect_anomalies
from dotenv import load_dotenv

try:
    load_dotenv()
except FileNotFoundError:
    print("No .env file found. Assuming environment variables are already set.")

def test_detect_anomalies():
    # Create a test DataFrame from the test.csv file
    test_df = pd.read_csv("tests/test.csv")

    test_df["month"] = pd.to_datetime(test_df["month"], format="%b-%y")

    # Call the detect_anomalies function with the test DataFrame
    result = detect_anomalies(test_df)

    # Check that the result is a dictionary
    assert isinstance(result, dict)

    # Check that the result contains the expected keys
    assert set(result.keys()) == {'isPositiveAnomaly', 'expectedValues', 'lowerMargins', 'upperMargins', 'isNegativeAnomaly', 'period', 'isAnomaly'}