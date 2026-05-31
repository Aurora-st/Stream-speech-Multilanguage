import noisereduce as nr
import librosa
import soundfile as sf


def reduce_noise(input_path: str, output_path: str):
    y, sr = librosa.load(input_path, sr=None)
    reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.9)
    sf.write(output_path, reduced_noise, sr)
    return output_path
