import logging
import os

import azure.functions as func
import pandas as pd
import requests
import io

app = func.FunctionApp()

# Learn more at aka.ms/pythonprogrammingmodel

# Get started by running the following code to create a function using a HTTP trigger.


def detect_anomalies(df):
    anomaly_detection_url = os.environ["ANOMALYENDPOINT"]
    key = os.environ["OCP_APIM_SUB"]
    headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": key}

    data = {
        "series": [
            {"timestamp": str(date), "value": float(value)}
            for date, value in zip(df["date"], df["value"])
        ],
        "maxAnomalyRatio": 0.25,
        "sensitivity": 95,
        "granularity": "monthly",
    }
    logging.info(data)

    # data = {"series": df}

    response = requests.post(
        anomaly_detection_url + "anomalydetector/v1.0/timeseries/entire/detect",
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    return response.json()


@app.function_name(name="AnomalyDetection")
@app.route(route="anomalydetection")
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    # The body of the request contains the content of a CSV file to be parsed.
    # It's plain text, so we need to convert it to a JSON object.
    req_body = req.get_body()

    # Convert the binary body to a string.
    req_body = req_body.decode("utf-8")
    logging.info(req_body)

    # The body of the request contains the content of a CSV file to be parsed
    # and analyzed for anomalies.
    # The CSV file is expected to have the following format:
    #   - The first row contains the column names. [date; value]
    #   - The first column contains the timestamp. [DD.MM.YYYY]
    #   - The second column contains the value to be analyzed. [float]
    #   - The CSV file is expected to be sorted by timestamp in ascending order.

    # The following code parses the string as a Pandas DataFrame.
    df = pd.read_csv(io.StringIO(req_body), sep=";")

    # Convert the date column to a datetime object.
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")

    # The following code sends the data to the anomaly detection service and
    # receives the results.
    # The body needs to be a JSON object with the following schema:
    # {"series": [list of dictionaries with the following schema:
    #  {"timestamp": str in the following format: "YYYY-MM-DDTHH:MM:SSZ, "value": float}]}
    # "maxAnomalyRatio": float,
    # "sensitivity": int,
    # "granularity": str in the following format: "minutely", "hourly", "daily", "weekly", "monthly"
    # }

    results = detect_anomalies(df)

    # The results have the following schema:
    # {"expectedValues": [list of floats],
    #  "isAnomaly": [list of booleans],
    #  "isNegativeAnomaly": [list of booleans],
    #  "isPositiveAnomaly": [list of booleans],
    #  "lowerMargins": [list of floats],
    #  "period": int,
    #  "upperMargins": [list of floats]}
    # }

    # The following code parses the results and merges it with the original data.
    anomaly_df = pd.DataFrame(results)
    enriched_df = df.join(anomaly_df)

    # The following code converts the enriched data to a CSV file and returns it
    # as the response body.
    response = func.HttpResponse(
        enriched_df.to_csv(index=False, sep=";"),
        mimetype="text/csv",
        status_code=200,
    )

    return response
