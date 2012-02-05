from __future__ import division

import wave
import numpy as np
import threading
import time
import pyaudio

FORMAT = pyaudio.paInt8
CHANNELS = 1
RATE = 44100

from listen import most_likely_bpm, filter_and_envelope

class Listener(threading.Thread):
    def run(self):
        p = pyaudio.PyAudio()
        block_size_s = 5
        stream = p.open(input_device_index = 3, format = FORMAT, channels = CHANNELS,
                        rate = RATE, input = True, 
                        frames_per_buffer = block_size_s * RATE)
        # stream = wave.open('crazy.wav', 'r')
        # num_channels = stream.getnchannels()
        # framerate = stream.getframerate()
        # sample_width = stream.getsampwidth()
        num_channels = CHANNELS
        framerate = RATE
        total_samples = int(framerate * block_size_s) * num_channels
        sample_width = p.get_sample_size(FORMAT)
        if sample_width == 1: 
                fmt = "%iB" % total_samples # read unsigned chars
        elif sample_width == 2:
            fmt = "%ih" % total_samples # read signed 2 byte shorts
        else:
            raise ValueError("Only supports 8 and 16 bit audio formats.")
        cutoff = 160
        nyq = framerate/2
        q = int(nyq//cutoff)
        filtered_framerate = framerate / q
        bpm_to_test = range(50, 170)
        while True:
            data = stream.read(int(block_size_s * framerate))
            if len(data) < block_size_s * framerate * num_channels * sample_width:
                print "not enough samples"
                break
            data = wave.struct.unpack(fmt, data)
            channels = [ [] for x in range(num_channels) ]

            for index, value in enumerate(data):
                bucket = index % num_channels
                channels[bucket].append(value)
            enveloped_data = filter_and_envelope(channels[0], q)

            bpm, phase = most_likely_bpm(enveloped_data, 
                                         bpm_to_test, 
                                         filtered_framerate,
                                         block_size_s)
            print "Most likely BPM:", bpm, "phase:", phase

if __name__ == "__main__":
    listener = Listener()
    listener.start()
    listener.join()
            
