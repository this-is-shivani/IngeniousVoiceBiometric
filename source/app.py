import pickle
from flask import Flask, request, render_template, jsonify
from random import randint
from voice_biometric.enrollment import doEnrollment
from voice_biometric.verification import doVerification
import os   
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

#Setting azure storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=voicebiometric;AccountKey=NHxR+JgIRAVzFNhV0luc5XHw/S3e+LKKhzEV38688QURYCmSnm2QYWpQEmozvAnSgYN+7QS2B0g/+AStV07cmw==;EndpointSuffix=core.windows.net"
container_name = "models" # container name in which images will be store in the storage account
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account
try:
    container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored
    container_client.get_container_properties() # get properties of the container to force exception to be thrown if container does not exist
except Exception as e:
    container_client = blob_service_client.create_container(container_name) # create a container in the storage account if it does not exist


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/enrollment")
def enrollment():
    return render_template('enrollment.html')


@app.route("/verification")
def verification():
    return render_template('verification.html')


@app.route("/enroll", methods=["POST", "GET"])
def enroll():
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        if(request.form['userid']+".pkl" == blob.name):
            return jsonify({"status":"failure", "desc":"User ID already registered"})
    if request.method == 'POST':
        form_data = dict()
        form_data['userId'] = request.form['userid']
        # save audio file
        request_file = request.files["inputfile1"]
        file_name = str(randint(0, 1000)) + ".wav"
        request_file.save(file_name)
        form_data['inputFile1'] = file_name

        request_file = request.files["inputfile2"]
        file_name = str(randint(0, 1000)) + ".wav"
        request_file.save(file_name)
        form_data['inputFile2'] = file_name

        request_file = request.files["inputfile3"]
        file_name = str(randint(0, 1000)) + ".wav"
        request_file.save(file_name)
        form_data['inputFile3'] = file_name
    # do enrollment
    pkl_file = doEnrollment(form_data)
    # Upload file
    fileobj = open(pkl_file, 'rb')
    try:
        container_client.upload_blob(pkl_file, fileobj) # upload the file to the container using the filename as the blob name
    except Exception as e:
            print(e)
    # give response
    return render_template("enrollment_success.html")


@app.route("/verify", methods=["POST"])
def verify():
    flag = 0
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        if(request.form['userid']+".pkl" == blob.name):
            flag = 1
    if(flag==0):
        return jsonify({"status":"failure","desc":"User ID has not been enrolled yet"})
    if request.method == 'POST':
        form_data = dict()
        form_data['userId'] = request.form['userid']
        # save audio files
        request_file = request.files["inputfile"]
        file_name = str(randint(0, 1000)) + ".wav"
        request_file.save(file_name)
        form_data['inputFileName'] = file_name
    # get score
    predictedId, predictedScore = doVerification(form_data)
    # give response
    if predictedId == form_data['userId']:
        return render_template("verification_success.html",score=predictedScore)
    else:
        return render_template("verification_fail.html")


if __name__ == "__main__":
    app.run(debug=True)
