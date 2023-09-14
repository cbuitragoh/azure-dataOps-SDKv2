from azure.mgmt.resource import ResourceManagementClient
from azure.ai.ml.entities import Data, Environment
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import Input, Output
from azure.ai.ml import command
from azure.ai.ml.entities import AzureBlobDatastore
from azure.ai.ml.entities import AccountKeyConfiguration
from azure.storage.blob import BlobServiceClient
from authorization import ml_client, credential, subscription_id, resource_group
import json
import time


# load account key. remember that before: retrieve account_key 
# from azure portal and saved on secrets.json. 
# load compute cluster name for job executions

with open("./secrets/secrets.json") as f:
    secrets = json.load(f)
    account_key = secrets["account_key"]
    compute_cluster = secrets["compute_cluster_name"]


######## CREATE CONTAINER ON STORAGE ACCOUNT ##########

# create manager client and retrieve the account name
mg_client= ResourceManagementClient(
    credential=credential,
    subscription_id=subscription_id
)

resources = mg_client.resources.list_by_resource_group(
    resource_group_name=resource_group
)

try:
    for resource in resources:
        if resource.type == "Microsoft.Storage/storageAccounts":
            account_name = resource.name
except Exception as e:
    print(e)

#create new container on storage account for save data
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net/",
    credential=credential
)

container_name = "training"
container_client = blob_service_client.create_container(container_name)

#pause before next action
print("container successfully created!")
time.sleep(30)


#################### CREATE DATASTORE #####################

#set variables for create datastore on azure
datastore_path = 'azureml://datastores/blob_training_data/paths/data-asset-path/'

#define DataStore
store = AzureBlobDatastore(
    name="blob_training_data",
    description="Blob Storage for training data in taxi project",
    account_name=account_name,
    container_name="training", 
    credentials=AccountKeyConfiguration(
        account_key=account_key
    ),
)

#create store
ml_client.create_or_update(store)
print("datastore successfully created!")

#pause before next action
time.sleep(30)


############# CREATE DIFFERENT ASSESTYPES ################

data_values = {
    "paths" : [datastore_path, "./nyc_taxi/", "./nyc_taxi/taxis.csv"],
    "types" : [AssetTypes.URI_FOLDER, AssetTypes.MLTABLE, AssetTypes.URI_FILE],
    "names" : ["data_training", "ml_table_training", "data_training_csv"],
    "descriptions" : [
        "This is a new datastore for training models",
        "ml table that contains url endpoints of parquet files with training data",
        "taxi data for training new models"
    ]
}

try:
    for value in range(len(data_values["paths"])):
        data = Data(
            path=data_values["paths"][value],
            type=data_values["types"][value],
            name=data_values["names"][value],
            description=data_values["descriptions"][value]
        )
        ml_client.data.create_or_update(data=data)
        time.sleep(10)
except Exception as e:
    print(e)

print("data from different AssetsType successfully created!")
#pause before next action
time.sleep(30)

###################### EXECUTE JOB ########################

# configure input and output
my_job_inputs = {
    "local_data": Input(type=AssetTypes.URI_FILE, path="azureml:data_training_csv:1")
}

my_job_outputs = {
    "datastore_data": Output(type=AssetTypes.URI_FOLDER, path="azureml://datastores/blob_training_data/paths/data-asset-path/")
}

# configure job
job = command(
    code="./src",
    command="python move_data.py --input_data ${{inputs.local_data}} --output_datastore ${{outputs.datastore_data}}",
    inputs=my_job_inputs,
    outputs=my_job_outputs,
    environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
    compute=compute_cluster,
    display_name="move-taxi-data",
    experiment_name="classification-taxis"
)

# submit job
ml_client.create_or_update(job)
print("job successfully raised!")

#pause before next action
time.sleep(30)

############### CREATE CUSTOMIZED ENVIRONMENT ####################

env_docker_image = Environment(
    name="sklearn-for-taxi-classification",
    image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04",
    description="environment created for training taxi classification models",
    conda_file="./env/conda_dependencies.yml"
)
ml_client.environments.create_or_update(env_docker_image)
print("environment successfully created!")
#pause before next action
time.sleep(30)


############## EXECUTE JOB ON CUSTOM ENVIRONMENT ###################

#retrieve data asset properties
data_asset = ml_client.data.get(name="ml_table_training", version="1")

job2 = command(
    code="./src",
    command="python load_data.py --input ${{inputs.green}}",
    inputs={"green": Input(type="mltable", path=data_asset.id)},
    environment="azureml:sklearn-for-taxi-classification:1",
    compute=compute_cluster,
    display_name="load-data-from-ml-table",
    experiment_name="second-classification"
)

ml_client.create_or_update(job2)
print("job2 successfully raised!")

#pause before next action
time.sleep(30)

job3 = command(
    name="start-light",
    code="./src",
    command="python load_data.py --input ${{inputs.green}}",
    inputs={"green": Input(type="mltable", path=data_asset.id)},
    environment=Environment(
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
        conda_file="./env/conda_dependencies.yml"
    ),
    compute=compute_cluster,
    display_name="load-data-on-new-environment",
    experiment_name="second-classification"
)

ml_client.create_or_update(job3)
print("All data process sucessfully executed!")