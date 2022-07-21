import sys
import numpy as np
from scipy.io import wavfile
import soundfile as sf


def rms_flat(a):  # from matplotlib.mlab
    """
    Return the root mean square of all the elements of *a*, flattened out.
    """
    return np.sqrt(np.mean(np.absolute(a)**2))


def measure_wav_db_level(wavFile):
    """
    Open a wave or raw audio file and perform the following tasks:
    - compute the overall level in db (RMS of data)
    """
    try:
        fs, x = wavfile.read(wavFile)
        LOG_SCALE = 20*np.log10(32767)
    except:
        x, fs = sf.read(wavFile,
                        channels=1, samplerate=44100,
                        format='RAW', subtype='PCM_16')
        LOG_SCALE = 0
    t = (np.array(x)).astype(np.float64)
    # x holds the int16 data, but it's hard to work on int16
    # t holds the float64 conversion
    print(wavFile)
    print(str(fs) + ' Hz')
    print(str(len(t) / fs) + ' s')
    orig_SPL = 20*np.log10(rms_flat(t)) - LOG_SCALE
    print('Sound level:   ' + str(orig_SPL) + ' dBFS')
    return orig_SPL



if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = 'output.wav'

