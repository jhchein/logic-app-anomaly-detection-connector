# Anomaly Detection with Azure Logic Apps and Python

(_Created by GPT_)

This repository contains Python code for an anomaly detection process that can be integrated with Azure Logic Apps. The process involves parsing a CSV file from any source supported by your Logic App (such as Storage Accounts, Sharepoint or One Drive), processing the data using a Function App, and returning the aggregated data.

The anomaly detection process is designed to help businesses identify unusual patterns or trends in their data that may be indicative of potential issues or opportunities. By detecting anomalies in their data, businesses can take proactive measures to mitigate risks or capitalize on opportunities.

The Python code in this repository is optimized for use with Azure Functions, which allows for quick and easy deployment and scaling of the anomaly detection process. The code is written in a modular and reusable way, making it easy to integrate with other components of an overall data processing pipeline.

Overall, this repository is a valuable resource for businesses that want to harness the power of anomaly detection to improve their operations and gain a competitive edge.

## Pre-Requisites

- A Microsoft Azure account
- A [Cognitive Services Anomaly Detector resource](https://learn.microsoft.com/en-us/azure/cognitive-services/anomaly-detector/overview)

## Getting Started

### Function App

- Fork this repository and adjust the code to your needs.
- Create a Cognitive Services Anomaly Detector resource.
- Create an Azure Function App, using Python (3.9+) and serverless hosting. Set region, monitoring, storage, and networking as you wish (see [Best practices for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices))
  - Set continous integration from your forked repository.
  - When your Function App is deployed, go to Configuration -> application settings in the function app and add
    - `ANOMALYENDPOINT`: The endpoint URL for your Cognitive Services Anomaly Detector instance
    - `OCP_APIM_SUB`: The subscription key for your Cognitive Services Anomaly Detector instance
    - `AzureWebJobsFeatureFlags`: with the key `EnableWorkerIndexing` to enable V2 Python models.
- Change the `FUNCTION_APP_NAME` in `.github\workflows\main_logic-app-anomaly-detection-connector.yml` to your function app name.
- In the Function App go to 'Functions' and select the 'AnomalyDetector' function. Under 'Function Keys' copy the default Function Key.

### Logic App

- Create a Logic App in Azure, that parses a CSV file.
- Add the 'HTTP Request' action.
- Set the 'Method' field to 'POST' and add the URL of your function app in the 'URI' field.
- In the Header set the key `x-functions-key` with your Function Key as the value.
- In the 'Body' field, add the CSV data from the previous step ("date";"value").
- Test the anomaly detection process.

### Protecting your Function

To fully secure your function endpoints in production, you should consider implementing one of the [following function app-level security options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger?pivots=programming-language-python&tabs=python-v2%2Cin-process%2Cfunctionsv2#secure-an-http-endpoint-in-production). When using one of these function app-level security methods, you should set the HTTP-triggered function authorization level to `anonymous`.

## Contributions

Contributions are welcome! Please create a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
