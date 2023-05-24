import io
import os
from typing import Dict

import azure.functions as func
import pandas as pd
import requests

import json

app = func.FunctionApp()

def detect_anomalies(df: pd.DataFrame, max_anomaly_ratio=0.25, sensitivity=95, granularity="monthly") -> Dict:
    """Detect anomalies in a time series using the Anomaly Detector API.

    Args:
        df (pd.DataFrame): The time series data to analyze.
        max_anomaly_ratio (float, optional): The maximum ratio of anomalies that can be detected. Defaults to 0.25.
        sensitivity (int, optional): The sensitivity of the anomaly detection algorithm. Defaults to 95.
        granularity (str, optional): The granularity of the time series data. Defaults to "monthly".

    Returns:
        Dict: The results of the anomaly detection.
    """

    anomaly_detection_url = os.environ["ANOMALYENDPOINT"]
    api_key = os.environ["OCP_APIM_SUB"]
    headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": api_key}

    data = {
        "series": [
            {"timestamp": str(month), "value": float(value)}
            for month, value in zip(df["month"], df["value"]) # type: ignore
        ],
        "maxAnomalyRatio": max_anomaly_ratio,
        "sensitivity": sensitivity,
        "granularity": granularity,
    }

    response = requests.post(
        anomaly_detection_url + "anomalydetector/v1.0/timeseries/entire/detect",
        headers=headers,
        json=data,
    )
    response.raise_for_status()

    return response.json()


@app.function_name(name="AnomalyDetection2")
@app.route(route="anomalydetection", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger function that detects anomalies in a time series using the Anomaly Detector API.

    Args:
        req (func.HttpRequest): The HTTP request.

    Returns:
        func.HttpResponse: The HTTP response.
    """

    # Get the request body
    req_body = req.get_body()
    req_body_str = req_body.decode("utf-8")

    # Parse the CSV data into a pandas DataFrame
    try:
        time_series_df = pd.read_csv(io.StringIO(req_body_str), sep=",")
    except pd.errors.EmptyDataError:
        return func.HttpResponse(
            "The request body is empty.", status_code=400, mimetype="text/plain"
        )

    # Convert the "month" column to a datetime object
    time_series_df["month"] = pd.to_datetime(time_series_df["month"], format="%b-%y")

    # Detect anomalies in the time series data
    anomaly_results = detect_anomalies(time_series_df)

    # Join the anomaly results with the original time series data
    anomaly_df = pd.DataFrame(anomaly_results)
    enriched_df = time_series_df.join(anomaly_df)

    # Check if any anomalies were detected
    anomaly_detected = any(enriched_df["isAnomaly"])

    # Convert the "month" column back to a string format
    enriched_df["month"] = pd.to_datetime(time_series_df["month"], format="%b-%y").dt.strftime("%b-%y")

    # Get the months with anomalies
    anomaly_months = enriched_df.loc[enriched_df["isAnomaly"], "month"].tolist()

    # Convert the enriched DataFrame to a CSV string
    csv_string = enriched_df.to_csv(index=False)

    # Return the response as a JSON object with the anomaly detection results and the enriched data as a CSV string
    response_body = {"anomaly_detected": anomaly_detected, "anomaly_months": anomaly_months, "enriched_data": csv_string}
    response = func.HttpResponse(
        json.dumps(response_body),
        mimetype="application/json",
        status_code=200,
    )

    return response