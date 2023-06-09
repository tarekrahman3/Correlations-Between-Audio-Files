# Date - March 31, 2023
# Dev - Tarek Rahman

import datetime, time, os, re
from pprint import pprint

import numpy as np
import pandas as pd

from scipy.io import wavfile
from scipy.signal import correlate

recorded_files_directory = "wav_files"
good_samples_directory = "good_samples"
mute_samples_directory = "mute_samples"


def compute_signals(audio_files_directory):
    samples = [os.path.join(audio_files_directory, file) for file in os.listdir(audio_files_directory)]
    signals = []
    for filename in samples:
        _, signal = wavfile.read(filename)
        signals.append(signal)
    return [signal / np.max(np.abs(signal)) for signal in signals]

def convert_unix_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') 

def get_corr(input_signal, comparison_signals):
    correlation_coefficients = [np.max(correlate(input_signal, signal, mode="full")) for signal in comparison_signals]
    max_index = np.argmax(correlation_coefficients)
    return correlation_coefficients[max_index]

def analyse_wav(wav_file, good_samples_signals, mute_samples_signals):
    input_file = wav_file['file_name']
    timestamp = re.search(r" (.+)\.wav", input_file).group(1)
    wav_file['called_time'] = convert_unix_timestamp(float(timestamp))
    wav_file['phn_nmbr'] = re.search(r"\d+", input_file).group()
    wav_file['status'] = None
    _, input_signal = wavfile.read(input_file)
    input_signal = input_signal / np.max(np.abs(input_signal))
    wav_file['good_corr'] = get_corr(input_signal, good_samples_signals)
    wav_file['mute_corr'] = 0.00
    if wav_file['good_corr'] > 5000:
        wav_file['status'] = "Active"
    else:
        wav_file['mute_corr'] = get_corr(input_signal, mute_samples_signals)
        if wav_file['mute_corr'] > 500:
            wav_file['status'] = "Mute"
        else:
            wav_file['status'] = "Inactive"
    return wav_file


if __name__ == "__main__":
    good_samples_signals = compute_signals(good_samples_directory)
    mute_samples_signals = compute_signals(mute_samples_directory)
    wav_files = [{"file_name": os.path.join(recorded_files_directory, file)} for file in os.listdir(recorded_files_directory)]
    [pprint(analyse_wav(wav_file, good_samples_signals, mute_samples_signals), sort_dicts=False) for wav_file in wav_files]
    pd.DataFrame(wav_files).to_csv(f'analysis {time.time()}csv')
