from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
import os
import json

#load credential from azure
credential = DefaultAzureCredential()

#load subscription_id
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

#load resource group name and workspace name
with open("./secrets/secrets.json") as f:
    secrets = json.load(f)
    resource_group = secrets["resource_group"]
    workspace = secrets["workspace_name"]

ml_client = MLClient(credential=credential,
                     subscription_id=subscription_id,
                     resource_group_name=resource_group,
                     workspace_name=workspace)

print("ml_client successfully created!")