This is a general example of useful azure SDKv2 on data operations with Azure Machine Learning. 

The workflow of this repo is:

1. Create a secrets.json file in the secrets/ folder according to the example_secrets.json file.
2. Open mltables_and_files.ipynb file for understand how to make the local base files for exercises.
3. setup.sh must execute on azure bash terminal o local bash terminal previously logged with azure cli login.
4. Execute data_ops_with_SDKv2.py file
5. Verify on https://portal.azure.com/ that all data assets and jobs exists or running, respectively.

Note. The account_key for storage account only can be retrieved manually from https://portal.azure.com/ retrieve it and saved it on secrets.json.