# Anomaly Detection with Azure Logic Apps and Python

This repository contains Python code for an anomaly detection process that can be integrated with Azure Logic Apps. The process involves parsing a CSV file from any source (such as Sharepoint), processing the data using a Function App, and returning the aggregated data.

The anomaly detection process is designed to help businesses identify unusual patterns or trends in their data that may be indicative of potential issues or opportunities. By detecting anomalies in their data, businesses can take proactive measures to mitigate risks or capitalize on opportunities.

The Python code in this repository is optimized for use with Azure Functions, which allows for quick and easy deployment and scaling of the anomaly detection process. The code is written in a modular and reusable way, making it easy to integrate with other components of an overall data processing pipeline.

Overall, this repository is a valuable resource for businesses that want to harness the power of anomaly detection to improve their operations and gain a competitive edge.

## Pre-Requisites

- A Microsoft Azure account
- A [Cognitive Services Anomaly Detector resource](https://learn.microsoft.com/en-us/azure/cognitive-services/anomaly-detector/overview)

## Getting Started

### Function App

- Clone this repository to your local machine.
- Set up your Azure account and create a Cognitive Services Anomaly Detector resource.
- Create an Azure Function App, using Python (3.9+) and serverless hosting. Set region, monitoring, storage, and networking as you wish.
- When your function is deployed, add ANOMALYENDPOINT and OCP_APIM_SUB (your anomaly detector endpoint and key) under application settings in the function app configuration.
- Deploy the Python code to the Azure Function App.

### Logic App

- Create a Logic App in Azure and add the 'HTTP Request' action.
- Set the 'Method' field to 'POST' and add the URL of your function app in the 'URI' field.
- In the 'Body' field, add your CSV data of the format ("date";"value").
- Test the anomaly detection process.

## Configuration

Before you can run the function app, you need to set the following environment variables:

- ANOMALYENDPOINT: The endpoint URL for your Cognitive Services Anomaly Detector instance
- OCP_APIM_SUB: The subscription key for your Cognitive Services Anomaly Detector instance

## Contributions

Contributions are welcome! Please create a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
