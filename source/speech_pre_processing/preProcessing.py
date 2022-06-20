# import pydub.AudioSegment to work with audio files
from pydub import AudioSegment
# import pytorch for Voice Activity Detection
import torch

torch.set_num_threads(1)
# import sampling rate value
from speech_pre_processing.config import SAMPLING_RATE
# import os for removing file
import os


def voicePreprocessing(voiceClip):
    '''
    Pre-processing phase: change Channel to MONO, perform Voice Activity Detection,
                            and Noise Reduction
    :param voiceClip: Name of the speech clip in String format
    '''

    ##################################
    # Step 1: Change channel to mono #
    ##################################

    # Import wav file
    voice_clip = AudioSegment.from_file(file=voiceClip, format="wav")
    # Change channel to mono
    voice_clip = voice_clip.set_channels(1)
    # Save file
    voice_clip.export("Mono_" + voiceClip, format="wav")

    ##################################################
    # Step 2: Perform Voice Activity Detection (VAD) #
    ##################################################

    # Load VAD model and tools to work with audio
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad',
                                  force_reload=False)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
    # Read file
    wav_file = read_audio("Mono_" + voiceClip, sampling_rate=SAMPLING_RATE)
    # Get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav_file, model, sampling_rate=SAMPLING_RATE)
    # Merge all speech chunks to one audio
    save_audio("Desilenced_Mono_" + voiceClip,
               collect_chunks(speech_timestamps, wav_file), sampling_rate=SAMPLING_RATE)
    ###################################
    # Step 3: Perform noise reduction #
    ###################################

    return
