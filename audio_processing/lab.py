"""
6.101 Lab 0: Sam Vinu-Srivatsan
Audio Processing
"""

import wave
import struct
# No Additional Imports Allowed!
# sam machine (some weird virtualenv thing so run): python3 -m pytest test.py
# add python as path variable or alias right to pytest
# install black to format one way

def backwards(sound):
    # create a new empty dictionary
    back = {}
    # append  same rate
    back["rate"] = sound["rate"]
    # reverse sample list
    back["samples"] = sound["samples"][::-1]
    return back

def mix(sound1, sound2, p):
    # ensure same rate
    if sound1["rate"] != sound2["rate"]:
        return None
    # initialize new  dictionary for final mixed sound
    mixed = {"rate":sound1["rate"],"samples":[]}
    # populate the longer one with zeros to get 2 lists same (longer) length
    new_sound1 = sound1["samples"].copy() + [0]*(len(sound2["samples"]) - len(sound1["samples"])) # add zeros to end, same size
    new_sound2 = sound2["samples"].copy() + [0]*(len(sound1["samples"]) - len(sound2["samples"])) # add zeros to end
    # sum all the (sound1samp*p + sound2samp*(p-1))
    for i in range(len(new_sound1)):
        mixed["samples"].append(new_sound1[i]*p + new_sound2[i]*(1-p))
    return mixed

def convolve(sound, kernel):
    modif_dict = {"rate":sound["rate"],"samples":[]}
    out_dict = {"rate":sound["rate"],"samples":[]}
    # like poly_mul() in recitation. iterate through kernel index and value:
    for k_ind, k_val in enumerate(kernel):
        # create a new list where you multiply each sample by kernel value
        modif_dict["samples"] = [i*k_val for i in sound["samples"].copy()]
        # concatenate that list to the end of [0]*index
        modif_dict["samples"] = [0]*k_ind + modif_dict["samples"]
        # add the corresponding elements and update output list
# CALL MIX TO ADD THE LISTS, BUT WHAT VALUE TO PASS FOR P?
        out_dict = mix(out_dict,modif_dict,0.5)
        out_dict["samples"] = [i*2 for i in out_dict["samples"]]
    return out_dict


def echo(sound, num_echoes, delay, scale):
    # sample delay tells us how many indices to shift by
    sample_delay = round(delay * sound['rate'])
    echo_dict = {"rate": sound["rate"],"samples":[]}
    sound_copy = {"rate": sound["rate"], "samples":sound["samples"].copy()}
    # add together delay_list and sound["samples"]
    for num in range(num_echoes):
        echo_dict["samples"] = [0]*sample_delay*(num+1) + [s*(scale**(num+1)) for s in sound["samples"].copy()]
        # add together the sound_copy sample list indices and the echo_dict sample list indices inside soundcopy
        sound_copy = mix(sound_copy,echo_dict,0.5)
        sound_copy["samples"] = [s*2 for s in sound_copy["samples"]]
    return sound_copy

def pan(sound):
    left = sound["left"].copy()
    right = sound["right"].copy()
    n = len(left)
    for index in range(n):
        right[index] *= (index/(n-1))
        left[index] *= (1-(index/(n-1)))
    new_sound = {"left":left, "rate":sound["rate"], "right": right}
    return new_sound

def remove_vocals(sound):
    left = sound["left"].copy()
    right = sound["right"].copy()
    n = len(left)
    mono = {"rate":sound["rate"],"samples":[]}
    for sample in range(n):
        mono["samples"].append(left[sample]-right[sample])
    return mono




def bass_boost_kernel(n_val, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ n_val

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(n_val):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for left, right in zip(sound["left"], sound["right"]):
            left = int(max(-1, min(1, left)) * (2**15 - 1))
            right = int(max(-1, min(1, right)) * (2**15 - 1))
            out.append(left)
            out.append(right)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)

    # ic = load_wav("sounds/ice_and_chilli.wav")
    # kernel = bass_boost_kernel(1000,1.5)
    # write_wav(convolve(ic,kernel), 'sounds/ice_chilli_bassboost.wav')

    # ech = load_wav("sounds/chord.wav")
    # write_wav(echo(ech,5,0.3,0.6), 'sounds/chord_echoey.wav')

    # car = load_wav("sounds/car.wav",True)
    # write_wav(pan(car), "sounds/car_pan.wav")
    vocals = load_wav("sounds/lookout_mountain.wav",True)
    write_wav(remove_vocals(vocals), "sounds/lookout_mono.wav")
