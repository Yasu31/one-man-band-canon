import sounddevice
from scipy.io.wavfile import write
import numpy as np
import datetime

segmentDuration = 10 # duration in seconds for 2 bars.
fs = 44100 # sampling freq.
repetitions = 34 # repeat a bit more than is necessary

#### hardcode the cello part ####
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
    # by not having the note play all the time, I feel it becomes easier to feel the tempo
    # So, cut the sound at 3/4 of the quarter note
    celloSegment[int(segmentDuration*fs*(i+0.75)//len(noteFreqList)):segmentDuration*fs*(i+1)//len(noteFreqList), :] = 0
    # todo: this is a bit too abrupt. smoother fade in / out

#### Allocate array to store performance ####
# "premature optimization is the root of all evil"
# this uses a lot of memory, but that can be dealt with later when I feel like it. For the time being, this works.
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
    '''manage sound I/O
    callback for the Stream object that receives mic input and determines speaker output.
    https://python-sounddevice.readthedocs.io/en/0.3.15/usage.html#callback-streams
    '''
    global initialSdTime
    if initialSdTime is None:
        initialSdTime = time.inputBufferAdcTime
    if status:
        print(status)

    # save input of first violin to respective positions in each part
    i = time2index(time.inputBufferAdcTime)
    first[i:i+frames, :] = indata
    i += segmentDuration * fs
    second[i:i+frames, :] = indata
    i += segmentDuration * fs
    third[i:i+frames, :] = indata

    # create accompaniment music to output from speaker
    i = time2index(time.outputBufferDacTime)
    outdata[:] = cello[i:i+frames] + second[i:i+frames] + third[i:i+frames]

try:
    with sounddevice.Stream(channels=1, samplerate=fs, callback=callback) as stream:
        input()
except (KeyboardInterrupt, ValueError):
    # ctrl-c or recording overflows allocated array
    pass

now = datetime.datetime.now()
filename = "canon-{}.wav".format(datetime.datetime.now().strftime("%Y%m%d-%H-%M"))
print("saving to {}".format(filename))
write(filename, fs, first+second+third+cello)
