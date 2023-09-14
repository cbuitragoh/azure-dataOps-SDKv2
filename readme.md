This is a general example of useful azure SDKv2 on data operations with Azure Machine Learning. 

The workflow of this repo is:

1. Create the secrets/ folder and next the secrets.json file into this in according to the example_secrets.json file.
2. Open mltables_and_files.ipynb file for understand how to make the local base files for exercises.
3. setup.sh must execute on azure bash terminal o local bash terminal previously logged with azure cli login.
4. The account_key for storage account only can be retrieved manually from https://portal.azure.com/ Retrieve it and saved it on secrets.json
5. Execute data_ops_with_SDKv2.py file
6. Verify on https://portal.azure.com/ that all data assets and jobs exists or running, respectively.