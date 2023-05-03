import io
import logging
import os
from typing import Dict

import azure.functions as func
import pandas as pd
import requests

app = func.FunctionApp()


def detect_anomalies(
    df: pd.DataFrame, maxAnomalyRatio=0.25, sensitivity=95, granularity="monthly"
) -> Dict:
    anomaly_detection_url = os.environ["ANOMALYENDPOINT"]
    key = os.environ["OCP_APIM_SUB"]
    headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}

    data = {
        "series": [
            {"timestamp": str(date), "value": float(value)}
            for date, value in zip(df["date"], df["value"])
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
@app.route(route="anomalydetection", auth_level=func.AuthLevel.FUNCTION)
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
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")

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
