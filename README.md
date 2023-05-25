# Anomaly Detection with Azure Logic Apps and Python

(_Created by GPT_)

This repository contains Python code for an anomaly detection process that can be integrated with Azure Logic Apps. The process involves parsing a CSV file from any source supported by your Logic App (such as Storage Accounts, SharePoint, or One Drive), processing the data using a Function App, and returning the aggregated data.

The Python code in this repository is optimized for use with Azure Functions, allowing for quick and easy deployment and scaling of the anomaly detection process. The code is modular and reusable, making it easy to integrate with other components of a data processing pipeline.

The anomaly detection process is designed to help businesses identify unusual patterns or trends in their data that may be indicative of potential issues or opportunities. By detecting anomalies in their data, businesses can take proactive measures to mitigate risks or capitalize on opportunities.

## Pre-Requisites

Before using this code, you'll need the following:

- A GitHub Account
- A Microsoft Azure Account, a subscription and contributor rights to 
create resource


## Getting Started

Here's how to get started with using this code.

### Setting up the Azure Function
1. Create a Cognitive Services Anomaly Detector resource.
2. Create an Azure Function App with Python (3.9+) and serverless hosting. You don't need CI/CD, we will do this manually. You can choose region, monitoring, storage, and networking as you like, following the [best practices for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices).
3. Go to your Function App `Configuration` > `Application settings` in the function app and add:
   - `ANOMALYENDPOINT`: The endpoint URL for your Cognitive Services Anomaly Detector instance from step 1.
   - `OCP_APIM_SUB`: The subscription key for your Cognitive Services Anomaly Detector instance from step 1.
   - `AzureWebJobsFeatureFlags`: with the key `EnableWorkerIndexing` to enable V2 Python models.

### Using GitHub Actions for Deployment
GitHub Actions is a powerful automation tool that allows you to automate tasks, such as building, testing and deploying code. We will use GitHub Actions to deploy your latest version of you Microsoft Function App to Azure.

1. Fork this repository.
2. *(Optional):* Adjust `function_app.py` to your needs. You might have a different schema or anomaly detection configuration.
3. Edit the GitHub Workflow `github\workflows\main_logic-app-anomaly-detection-connector.yml` 
   - set `FUNCTION_APP_NAME` to your function app name.
   - We will need permissions to deploy the App to Azure. Therefore follow these steps to [set your Function Publish profile](https://github.com/Azure/functions-action#using-publish-profile-as-deployment-credential-recommended) as a GitHub secret and then adjust the `publish profile` in the 'Deploy to Azure Functions' step. 
4. Run the GitHub Workflow. After your Function App is deployed, go to the Function App to 'Functions' and select the 'AnomalyDetector' (the name you gave it in `function_app.py`) function. Under 'Function Keys,' copy the default Function Key.

For more information about deploying with GitHub Actions, see [Deploying with GitHub Actions](https://docs.github.com/en/actions/deployment/about-deployments/deploying-with-github-actions) .

### Call the Connector from your Logic App
1. Create a Logic App in Azure that can parse a CSV file. You can use the suiting connector (e.g. OneDrive, SharePoint) for this purpose.
2. Add the 'HTTP Request' action.
3. Set the 'Method' field to 'POST' and enter the URL of your function app in the 'URI' field. You can find the URL of your function app in the Azure portal.
4. In the Header section, add a key named `x-functions-key` and set its value to your Function Key. You can find your Function Key in the Azure portal as well.
5. In the 'Body' field, paste the CSV data that you want to analyze. The comma serapated CSV data should have minimum two columns: "month" and "value". You can adjust the schema under `function_app.py`.
6. Run your Logic App and check the output of the 'HTTP Request' action. It should return a JSON object with the anomaly detection results `enriched_data`, the `anomaly_months` when anomalies were detected, and the `anomaly_detected` boolean if anomalies were detected.

## Best practices
### Protect Your Function
To fully secure your function endpoints in production, you should consider implementing one of the [following function app-level security options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger?pivots=programming-language-python&tabs=python-v2%2Cin-process%2Cfunctionsv2#secure-an-http-endpoint-in-production). When using one of these function app-level security methods, you should set the HTTP-triggered function authorization level to `anonymous`.

If you only call the Function from a Logic App, go to the Function App `Networking` > `Inbound Traffic` > `Access restriction` and add a Allow rule with Type `Service Tag` and Service Tag `Logic Apps`.

### Enable and add Automated Tests.
1. Set `ANOMALYENDPOINT` and `OCP_APIM_SUB` (endpoint and key of your Anomaly Detector) as [repository secrets](https://github.com/Azure/actions-workflow-samples/blob/master/assets/create-secrets-for-GitHub-workflows.md) in your freshly forked repository.
2. Edit the GitHub Workflow `github\workflows\main_logic-app-anomaly-detection-connector.yml` and under `jobs.build` uncomment the steps `install pytest`, `Set PYTHONPATH` and `Run pytest`
3. Add more tests to `tests\test_function_app.py`.

## Optional Steps
If you want to avoid adding secrets manually, you can [create an Azure Service Principal](https://github.com/Azure/actions-workflow-samples/blob/master/assets/create-secrets-for-GitHub-workflows.md) and add AZURE_CRENDENTIALS as a repository secret. 

You can then in `github\workflows\main_logic-app-anomaly-detection-connector.yml` uncomment the `Login to Azure` and `Set environment variables` steps.

## Contributions

Contributions are welcome! If you have changes to suggest, please create a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
