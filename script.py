import sounddevice
from scipy.io.wavfile import write
import numpy as np
from threading import Timer
from time import sleep, time

segmentDuration = 8
fs = 44100

first = np.zeros((0,1))
second = np.zeros((0,1))
third = np.zeros((0,1))

# what second and third player should be playing in current segment
# respectively the previous and previous previous segments played by the first player
secondHalfSegment1 = np.zeros((segmentDuration*fs//2,1))
thirdHalfSegment1 = np.copy(secondHalfSegment1)
secondHalfSegment2 = np.copy(secondHalfSegment1)
thirdHalfSegment2 = np.copy(secondHalfSegment1)

# construct the cello segment
celloSegment = np.zeros((segmentDuration*fs,1))
# D, A, B, F#, G, D, G, A
# https://pages.mtu.edu/~suits/notefreqs.html
noteFreqList = [293.66, 220, 246.94, 185.00, 196, 146.83, 196, 220]
for i in range(len(noteFreqList)):
    noteFreq = noteFreqList[i]
    t = np.arange(segmentDuration*fs/len(noteFreqList))/fs
    celloNote = 0.1 * np.sin(2*np.pi*noteFreq*t)
    celloNote = celloNote.reshape((-1, 1))
    celloSegment[segmentDuration*fs*i//len(noteFreqList):segmentDuration*fs*(i+1)//len(noteFreqList), :] = celloNote
celloHalfSegment1 = celloSegment[:segmentDuration*fs//2, :]
celloHalfSegment2 = celloSegment[segmentDuration*fs//2:, :]

wholeRecording = np.copy(celloHalfSegment1)
def save(first, second, third, cello, accompaniment):
    global wholeRecording
    wholeRecording = np.append(wholeRecording, first+second+third+cello, axis=0)
    third[:] = np.copy(second)
    second[:] = np.copy(first)
    accompaniment[:] = second + third + cello

accompanimentHalfSegment1 = np.copy(celloHalfSegment1)
accompanimentHalfSegment2 = np.copy(celloHalfSegment2)
firstHalfSegment2 = np.zeros((segmentDuration*fs//2,1))
timing = 0.3
try:
    while True:
        # first half-segment
        firstHalfSegment1 = sounddevice.playrec(accompanimentHalfSegment1, samplerate=fs, channels=1)
        t = Timer(segmentDuration/4, save, args=(firstHalfSegment2, secondHalfSegment2, thirdHalfSegment2, celloHalfSegment2, accompanimentHalfSegment2))
        t.start()
        sleep(segmentDuration/2-timing)

        firstHalfSegment2 = sounddevice.playrec(accompanimentHalfSegment2, samplerate=fs, channels=1)
        t = Timer(segmentDuration/4, save, args=(firstHalfSegment1, secondHalfSegment1, thirdHalfSegment1, celloHalfSegment1, accompanimentHalfSegment1))
        t.start()
        sleep(segmentDuration/2-timing)
        
except KeyboardInterrupt:
    pass
write("output.wav", fs, wholeRecording)
