import requests
import os
import pydub
from audiostretchy.stretch import stretch_audio
from pydub.silence import detect_leading_silence, split_on_silence
from argparse import ArgumentParser

api = "https://tts.datacula.com/api/"

def checkAlive() :
    """checks if the api is alive
    
    Returns :
        0 if everything's ok
        1 if the api response is not ok
        2 if the api is reporting that it's dead
    """
    try :
        res = requests.get(api)
        if (not res.ok) :
            return 1
        
        if (not res.json()["alive"]) :
            return 2
        
        return 0
    
    except :
        return 1

def getVoice(text : str, dest : str, modelName : str = "amir") :
    """Get speech from text! and save it to path as a wav file

    Args:
        text (str): text to be spoken
        dest (str): destination file(should not exist beforehand)
        modelName (str, optional): api specific. Defaults to "amir".

    Raises:
        FileExistsError: if dest already exists
        ConnectionError: if the api's response code is not ok
        ConnectionRefusedError: if api returns a json instead of the requested wav
    """
    # if (os.path.isfile(dest)) :
    #     raise FileExistsError("getVoice output file already exists")
    
    ret = requests.get(api + "tts", params={"text": text.encode("utf-8"), "model_name": modelName.encode("utf-8")})
    if (not ret.ok) :
        raise ConnectionError(f"{api}tts response code not okay : <{ret.status_code}>")
    
    retIsJson = False
    try :
        ret.json()
        retIsJson = True
    except :
        pass
    
    if (retIsJson) :
        raise ConnectionRefusedError(f"{api}tts response not an audio file : {ret.text}")
    
    with open(dest, "wb") as f :
        f.write(ret.content)
        f.close()

def loudDistort(src : str, dest : str, dbMul : float = 50, destFormat : str = "wav") :
    """Distorts src audio file by adding dbMul db to its volume

    Args:
        src (str): src file
        dest (str): dest file(saved in destFormat file format)
        dbMul (int, optional): how many dbs to add. Defaults to 50.
        destFormat (str, optional): output file format. Defaults to "wav".

    Raises:
        FileExistsError: occurs when the output file is not the same as the input file and it already exists.
    """
    # if (os.path.isfile(dest) and dest != src) :
    #     raise FileExistsError("loudDistort output file already exists")
    
    audio : pydub.AudioSegment = pydub.AudioSegment.from_file(src)
    audio += dbMul
    audio.export(dest, destFormat)

def removeSilences(src : str, dest : str, destFormat : str = "wav") :
    """Remove leading and trailing silences

    Args:
        src (str): source file
        dest (str): dest file
        destFormat (str, optional): audio format to save dest. Defaults to "wav".
    """
    audio : pydub.AudioSegment = pydub.AudioSegment.from_file(src)
    audio = audio[detect_leading_silence(audio):-detect_leading_silence(audio.reverse())]
    audio.export(dest, destFormat)

def aggrSilenceRm(src : str, dest : str, destFormat : str = "wav") :
    audio : pydub.AudioSegment = pydub.AudioSegment.from_file(src)
    audio = sum(split_on_silence(audio, 300, keep_silence=100))
    audio.export(dest, destFormat)

def main() :
    parser = ArgumentParser(prog="Arianator",
                            description="This tool helps you make kaka-sangi-dancing to LAYE BARDAR memes",
                            epilog="Made by Arian")
    parser.add_argument("text", help="narration to be used in the video")
    parser.add_argument("-o", "--output", help="destination file", dest="dest", action="store", default="mammad.wav")
    parser.add_argument("--speed-mul", help="speed multiplier which controlls how slow the audio is going to be",
                        dest="sp_mul", action="store", default=2, type=float)
    parser.add_argument("-G", "--gain", help="gain used to distort the audio. in db",
                        dest="gain", action="store", default=50, type=float)
    parser.add_argument("--aggressive-silence-rm", help="remove silences aggressively", action="store_true", dest="silence_rm")

    args = parser.parse_args()
    
    getVoice(args.text, args.dest)
    removeSilences(args.dest, args.dest)
    stretch_audio(args.dest, args.dest, args.sp_mul)
    if (args.silence_rm) :
        aggrSilenceRm(args.dest, args.dest)
    loudDistort(args.dest, args.dest, args.gain)


if __name__ == "__main__" :
    main()