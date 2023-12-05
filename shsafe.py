from flask import Flask, render_template, request

## Import necessary modules
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta


app = Flask(__name__)

@app.route('/')
def get_data():
    return render_template('input.html')

@app.route("/")
def hello():
    return "<html><body><h1>Hello Best Bike App!</h1></body></html>\n"


@app.route('/', methods=["POST"])
def handle_data():
    path = request.form['path']

    try:
        # Retrieve the connection string for use with the application.
        connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Retrieve the container name 
        container_name = os.environ['CONTAINER_NAME']
        container_client = blob_service_client.get_container_client(container_name)

        # Enter the relative file path
        path_to_blob = path

        # Create a blob client
        filename = os.path.basename(path_to_blob)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

        # Display blob upload message
        #print("<html><body><p>\nUploading to Azure Storage as blob:\n\t</p></body></html>" + filename)

        # Upload the created file
        with open(file=path_to_blob, mode="rb") as data:
            blob_client.upload_blob(data)
        
        #print('<html><body><p>Upload complete !!</p></body></html>\n')
        #print('<html><body><p>Generating download link  ... Link valid for only 24 hours !</p></body></html>\n')
        

        ## Let's get the Blob content which was just uploaded to the container
        blob_client = container_client.get_blob_client(filename)
        expiry=datetime.utcnow() + timedelta(days=1)

        # Generate a SAS token for the blob container
        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=container_name,
            blob_name=blob_client.blob_name,
            account_key=os.environ['ACCESS_KEY'],
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )
        
        ##Create a URL for our generated SAS token
        blob_sas_url = "{}?{}".format(blob_client.url, sas_token)
        dounload_link = "Your secured download link is :\n{}".format(blob_sas_url)
        return dounload_link

    except Exception as ex:
        print('Exception:')
        print(ex)

    
    





if __name__ == '__main__':
    app.run()
