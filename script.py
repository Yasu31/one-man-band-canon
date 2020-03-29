import sounddevice
from scipy.io.wavfile import write
import numpy as np
import datetime

segmentDuration = 10
fs = 44100
repetitions = 34

# construct the cello segment
celloSegment = np.zeros((segmentDuration*fs,1))
# D, A, B, F#, G, D, G, A
# https://pages.mtu.edu/~suits/notefreqs.html
noteFreqList = [293.66, 220, 246.94, 185.00, 196, 146.83, 196, 220]
for i in range(len(noteFreqList)):
    noteFreq = noteFreqList[i]
    t = np.arange(segmentDuration*fs/len(noteFreqList))/fs
    celloNote = 0.3 * np.sin(2*np.pi*noteFreq*t)
    celloNote = celloNote.reshape((-1, 1))
    celloSegment[segmentDuration*fs*i//len(noteFreqList):segmentDuration*fs*(i+1)//len(noteFreqList), :] = celloNote
    celloSegment[int(segmentDuration*fs*(i+0.75)//len(noteFreqList)):segmentDuration*fs*(i+1)//len(noteFreqList), :] = 0
    # todo: smoother fade in / out

# "premature optimization is the root of all evil"
first = np.zeros((segmentDuration*fs*repetitions, 1))
second = np.zeros((segmentDuration*fs*repetitions, 1))
third = np.zeros((segmentDuration*fs*repetitions, 1))
cello = np.tile(celloSegment, (repetitions, 1))

initialSdTime = None
def time2index(sdTime):
    '''convert time obtained from sounddevice into index of the data 
    '''
    return int((sdTime - initialSdTime) * fs)

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    # save input to first violin part
    global initialSdTime
    if initialSdTime is None:
        initialSdTime = time.inputBufferAdcTime
    i = time2index(time.inputBufferAdcTime)
    first[i:i+frames, :] = indata
    i += segmentDuration * fs
    second[i:i+frames, :] = indata
    i += segmentDuration * fs
    third[i:i+frames, :] = indata

    # create accompaniment music
    i = time2index(time.outputBufferDacTime)
    outdata[:] = cello[i:i+frames] + second[i:i+frames] + third[i:i+frames]

try:
    with sounddevice.Stream(channels=1, samplerate=fs, callback=callback) as stream:
        input()
except KeyboardInterrupt or ValueError:
    pass

now = datetime.datetime.now()
filename = "canon-{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H-%M"))
print("saving to {}".format(filename))
write(filename, fs, first+second+third+cello)
