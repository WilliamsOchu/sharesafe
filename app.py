## Import necessary modules
from flask import Flask, render_template, request
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

## Initiate the flask app
app = Flask(__name__)

## Establish a connection with Azure Key_Vault 
keyVaultName = os.environ["KEY_VAULT_NAME"]
KVUri = "https://{}.vault.azure.net".format(keyVaultName)
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KVUri, credential=credential)

## Display the app landing page
@app.route('/')
def get_data():
    return render_template('input.html')

## Upload file and Generate download link 

@app.route('/', methods=["POST"])
def handle_data():
    ## Get the file to be uploaded
    path = request.files.get("path")

    try:
        # Retrieve the connection string for use with the application.
        connect_str = secret_client.get_secret("azurestorageconnectstring").value
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        
        # Retrieve the container name 
        container_name = secret_client.get_secret('sgsharesafecontainer').value
        container_client = blob_service_client.get_container_client(container_name)
        
        # Establish the file location
        path_to_blob = path

        # Upload the created file
        container_client.upload_blob(path_to_blob.filename, path_to_blob)      
            
        ## Let's get the Blob content which was just uploaded to the container
        blob_client = container_client.get_blob_client(path_to_blob.filename)
        expiry=datetime.utcnow() + timedelta(days=1)

        # Generate a SAS token for the blob container
        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=container_name,
            blob_name=blob_client.blob_name,
            account_key=secret_client.get_secret('sgsharesafeaccesskey').value,
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )
        
        ##Create a URL for our generated SAS token
        blob_sas_url = "{}?{}".format(blob_client.url, sas_token)
        download_link = blob_sas_url
        return render_template('output.html', download_link=download_link)
               
    except Exception as ex:
        print('Exception:')
        print(ex)
       
if __name__ == '__main__':
    app.run(debug=True)
