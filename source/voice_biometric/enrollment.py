from speech_pre_processing.preProcessing import voicePreprocessing
from feature_extraction.mfcc import extractFeatures
from training_model.gmm import getVoicePrint
import scipy.io.wavfile as wav
import pickle
from models.user import User
import numpy as np


def doEnrollment(form_data):
    features = list()
    # first file
    voicePreprocessing(form_data["inputFile1"])
    sample_rate, data = wav.read("Desilenced_Mono_" + form_data["inputFile1"])
    vector = extractFeatures(data, sample_rate)
    features = vector
    # second file
    voicePreprocessing(form_data["inputFile2"])
    sample_rate, data = wav.read("Desilenced_Mono_" + form_data["inputFile2"])
    vector = extractFeatures(data, sample_rate)
    features = np.vstack((features, vector))
    # third file
    voicePreprocessing(form_data["inputFile3"])
    sample_rate, data = wav.read("Desilenced_Mono_" + form_data["inputFile3"])
    vector = extractFeatures(data, sample_rate)
    features = np.vstack((features, vector))
    # Get Model
    model = getVoicePrint(features)
    userData = User(form_data['userId'], features, model)
    # save user data in database
    pickleFile = userData.userId + ".pkl"
    fileobj = open(pickleFile, 'wb')
    pickle.dump(userData, fileobj)
    fileobj.close()
    return pickleFile
