#! /usr/bin/sh

# Set the necessary variables
RESOURCE_GROUP=$(jq -r .resource_group ./secrets/secrets.json)
RESOURCE_PROVIDER="Microsoft.MachineLearning"
REGION="eastus"
WORKSPACE_NAME=$(jq -r .workspace_name ./secrets/secrets.json)
COMPUTE_CLUSTER=$(jq -r .compute_cluster_name ./secrets/secrets.json)

# Register the Azure Machine Learning resource provider in the subscription
echo "Register the Machine Learning resource provider:"
az provider register --namespace $RESOURCE_PROVIDER

# Create the resource group and workspace and set to default
echo "Create a resource group and set as default:"
az group create --name $RESOURCE_GROUP --location $REGION
az configure --defaults group=$RESOURCE_GROUP

echo "Create an Azure Machine Learning workspace:"
az ml workspace create --name $WORKSPACE_NAME 
az configure --defaults workspace=$WORKSPACE_NAME 

# Create compute cluster
echo "Creating a compute cluster with name: " $COMPUTE_CLUSTER
az ml compute create --name ${COMPUTE_CLUSTER} --size STANDARD_DS11_V2 --max-instances 2 --type AmlCompute 