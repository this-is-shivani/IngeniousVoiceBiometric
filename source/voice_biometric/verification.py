from speech_pre_processing.preProcessing import voicePreprocessing
from feature_extraction.mfcc import extractFeatures
import scipy.io.wavfile as wav
import pickle
from models.user import User
from scipy.special import softmax
from azure.storage.blob import BlobServiceClient
import numpy as np

#Setting azure storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=voicebiometric;AccountKey=NHxR+JgIRAVzFNhV0luc5XHw/S3e+LKKhzEV38688QURYCmSnm2QYWpQEmozvAnSgYN+7QS2B0g/+AStV07cmw==;EndpointSuffix=core.windows.net"
container_name = "models" # container name in which images will be store in the storage account
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account
try:
    container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored
    container_client.get_container_properties() # get properties of the container to force exception to be thrown if container does not exist
except Exception as e:
    container_client = blob_service_client.create_container(container_name) # create a container in the storage account if it does not exist



def doVerification(form_data):
    user_mapping={}
    # Get features and create model for unknown voice
    voicePreprocessing(form_data["inputFileName"])
    sample_rate, data = wav.read("Desilenced_Mono_" + form_data["inputFileName"])
    features = extractFeatures(data, sample_rate)
    # Get all gmm
    users_models = list()
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob=blob.name)
        download_stream = blob_client.download_blob()
        download = pickle.loads(download_stream.readall())
        userObj = User(download.userId,download.features,download.userModel)
        users_models.append(userObj)
    scores = np.zeros(len(users_models))
    for idx in range(len(users_models)) :
    # Score the voice sample under each gmm
        logprob = users_models[idx].userModel.score(features)
        scores[idx]=logprob
    # Calculate winner
    winner = np.argmax(scores)
    winner_useId = users_models[winner].userId
    return winner_useId, scores[winner]+100
