import sounddevice
from scipy.io.wavfile import write
import numpy as np

segmentDuration = 8
fs = 44100

first = np.zeros((0,1))
second = np.zeros((0,1))
third = np.zeros((0,1))

# what second and third player should be playing in current segment
# respectively the previous and previous previous segments played by the first player
secondSegment = np.zeros((segmentDuration*fs,1))
thirdSegment = np.zeros((segmentDuration*fs,1))

# construct the cello segment
celloSegment = np.zeros((segmentDuration*fs,1))
# D, A, B, F#, G, D, G, A
# https://pages.mtu.edu/~suits/notefreqs.html
noteFreqList = [293.66, 220, 246.94, 185.00, 196, 146.83, 196, 220]
for i in range(len(noteFreqList)):
    noteFreq = noteFreqList[i]
    t = np.arange(segmentDuration*fs/len(noteFreqList))/fs
    celloNote = 0.2 * np.sin(2*np.pi*noteFreq*t)
    celloNote = celloNote.reshape((-1, 1))
    celloSegment[segmentDuration*fs*i//len(noteFreqList):segmentDuration*fs*(i+1)//len(noteFreqList), :] = celloNote

wholeRecording = np.zeros((0,1))
try:
    while True:
        accompaniment = secondSegment + thirdSegment + celloSegment
        recording = sounddevice.playrec(accompaniment, samplerate=fs, channels=1)
        sounddevice.wait()
        recording *= 3
        thirdSegment = secondSegment
        secondSegment = recording
        wholeRecording = np.append(wholeRecording, accompaniment+recording, axis=0)
except KeyboardInterrupt:
    pass
write("output.wav", fs, wholeRecording)
