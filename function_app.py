import io
import logging
import os
from typing import Dict

import azure.functions as func
import pandas as pd
import requests

app = func.FunctionApp()

# Make sure that the required environment variables are set
if "ANOMALYENDPOINT" not in os.environ:
    raise ValueError(
        "ANOMALYENDPOINT environment variable is not set. This is the URL of the Anomaly Detector API."
    )
if "OCP_APIM_SUB" not in os.environ:
    raise ValueError(
        "OCP_APIM_SUB environment variable is not set. This is the subscription key for the Anomaly Detector API."
    )
if "AzureWebJobsFeatureFlags" not in os.environ:
    raise ValueError(
        "AzureWebJobsFeatureFlags environment variable is not set. The key should be set to `EnableWorkerIndexing` to enable V2 Python models."
    )


def detect_anomalies(
    df: pd.DataFrame, maxAnomalyRatio=0.25, sensitivity=95, granularity="monthly"
) -> Dict:
    """Detect anomalies in a time series using the Anomaly Detector API.

    Args:
        df (pd.DataFrame): The time series data to analyze.
        maxAnomalyRatio (float, optional): The maximum ratio of anomalies that can be detected. Defaults to 0.25.
        sensitivity (int, optional): The sensitivity of the anomaly detection algorithm. Defaults to 95.
        granularity (str, optional): The granularity of the time series data. Defaults to "monthly".

    Returns:
        Dict: The results of the anomaly detection.
    """

    # Check if granularity is valid
    if granularity not in [
        "secondly",
        "minutely",
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "Yearly",
    ]:
        raise ValueError(
            "Invalid granularity. Must be one of: secondly, minutely, hourly, daily, weekly, monthly, Yearly"
        )

    anomaly_detection_url = os.environ["ANOMALYENDPOINT"]
    key = os.environ["OCP_APIM_SUB"]
    headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}

    data = {
        "series": [
            {"timestamp": str(month), "value": float(value)}
            for month, value in zip(df["month"], df["value"])
        ],
        "maxAnomalyRatio": maxAnomalyRatio,
        "sensitivity": sensitivity,
        "granularity": granularity,
    }
    logging.info(data)

    response = requests.post(
        anomaly_detection_url + "anomalydetector/v1.0/timeseries/entire/detect",
        headers=headers,
        json=data,
    )
    response.raise_for_status()

    return response.json()


@app.function_name(name="AnomalyDetection")
@app.route(route="anomalydetection", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Get the body of the request as bytes
    req_body = req.get_body()

    # Convert the binary body to a string
    req_body_str = req_body.decode("utf-8")
    logging.info(req_body_str)

    # Parse the string as a Pandas DataFrame
    df = pd.read_csv(io.StringIO(req_body_str), sep=";")

    # Convert the date column to a datetime object
    # df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
    df["month"] = pd.to_datetime(df["month"], format="%b-%y")

    # Send data to the anomaly detection service and receive the results
    results = detect_anomalies(df)

    # Parse the results and merge them with the original data
    anomaly_df = pd.DataFrame(results)
    enriched_df = df.join(anomaly_df)

    # Convert the enriched data to a CSV file and return it as the response body
    response = func.HttpResponse(
        enriched_df.to_csv(index=False, sep=";"),
        mimetype="text/csv",
        status_code=200,
    )

    return response
