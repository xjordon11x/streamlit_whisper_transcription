import sounddevice as sd
import numpy as np

def audio_recorder(pause_threshold=0.5, sample_rate=44100):
    duration = 60  # seconds

    def audio_callback(indata, frames, time, status):
        nonlocal recording
        if status:
            print(status, file=sys.stderr)
        frames_all.append(indata.copy())
        if len(frames_all) * buffer_size > sample_rate * duration:
            recording = False

    buffer_size = 2048
    frames_all = []
    recording = True

    with sd.InputStream(
        samplerate=sample_rate, blocksize=buffer_size, channels=1, callback=audio_callback
    ):
        print("Recording started!")
        while recording:
            sd.sleep(100)

    frames_all = np.concatenate(frames_all)
    audio_bytes = frames_all.tobytes()

    return audio_bytes
