import sounddevice
from scipy.io.wavfile import write

record_seconds = 3
fs = 44100

recording = sounddevice.rec(int(record_seconds*fs), samplerate=fs, channels=2)
sounddevice.wait()
print(recording.shape)
write("output.wav", fs, recording)