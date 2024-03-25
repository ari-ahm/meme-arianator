import requests
import os
import shutil
import cv2
import numpy as np
import pydub
from audiostretchy.stretch import stretch_audio
from pydub.silence import detect_leading_silence, split_on_silence
from argparse import ArgumentParser
from tqdm import tqdm
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import ImageFont, ImageDraw, Image
import ffmpeg

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

def putText(src : str, dest : str, text : str, fontpath : str, fontsize : int, timer : bool = False) :
    cv2Inp = cv2.VideoCapture(src)
    inpBuffer = []
    if (timer) :
        print("Reading video input...")
    success = True
    for i in (tqdm(range(int(cv2Inp.get(cv2.CAP_PROP_FRAME_COUNT)))) if timer else range(int(cv2Inp.get(cv2.CAP_PROP_FRAME_COUNT)))) :
        success, img = cv2Inp.read()
        if (not success) :
            break
        inpBuffer.append(img)
    
    videoDimension = (int(cv2Inp.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cv2Inp.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    out = cv2.VideoWriter(dest, int(cv2Inp.get(cv2.CAP_PROP_FOURCC)), cv2Inp.get(cv2.CAP_PROP_FPS), videoDimension)
    cv2Inp.release()
    
    if (timer) :
        print("Processing video output...")
    # text = arabic_reshaper.reshape(text)
    text = text[::-1]
    bidi_text = get_display(text)
    font = ImageFont.truetype(fontpath, fontsize)
    for i in (tqdm(inpBuffer) if timer else inpBuffer) :
        img_pil = Image.fromarray(i)
        draw = ImageDraw.Draw(img_pil)
        _, _, w, h = draw.textbbox((0, 0), bidi_text, font = font)
        draw.text(((videoDimension[0] - w) // 2, videoDimension[1] // 15), bidi_text, font = font)
        i = np.array(img_pil)
        out.write(i)
    
    out.release()

def getVideoDuration(src : str) :
    inp = cv2.VideoCapture(src)
    ret = int(inp.get(cv2.CAP_PROP_FRAME_COUNT)) / inp.get(cv2.CAP_PROP_FPS)
    inp.release()
    return ret

def repeat(src : str, dest : str, sleep : float, duration : float, destFormat : str = "wav") :
    audio : pydub.AudioSegment = pydub.AudioSegment.from_file(src)
    step = len(audio) / 1000 + sleep
    rep = int(duration / step)
    ret = pydub.AudioSegment.silent(duration=sleep * 1000)
    for i in range(rep) :
        ret = ret + audio + pydub.AudioSegment.silent(duration=sleep * 1000)
    ret.export(dest, destFormat)

def main() :
    parser = ArgumentParser(prog="Arianator",
                            description="This tool helps you make kaka-sangi-dancing to LAYE BARDAR memes",
                            epilog="Made by Arian")
    parser.add_argument("text", help="narration to be used in the video")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true", dest="verbose")
    parser.add_argument("-o", "--audio-output", help="destination audio file", dest="adest", action="store", default="mammad.wav")
    parser.add_argument("-O", "--video-output", help="destination video file", dest="vdest", action="store", default="mammad.mp4")
    parser.add_argument("--speed-mul", help="speed multiplier which controlls how slow the audio is going to be",
                        dest="sp_mul", action="store", default=2, type=float)
    parser.add_argument("-G", "--gain", help="gain used to distort the audio. in db",
                        dest="gain", action="store", default=50, type=float)
    parser.add_argument("--aggressive-silence-rm", help="remove silences aggressively", action="store_true", dest="silence_rm")
    parser.add_argument("-s", "--sleep", help="number of seconds to wait between each repetition",
                        dest="sleep", action="store", default=3, type=float)
    parser.add_argument("-V", "--video", help="Input video to be used as background", dest="vid", action="store",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/vid_low_q.mp4"))
    parser.add_argument("-f", "--font", help="Font path to be used", dest="font", action="store",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/arial.ttf"))
    parser.add_argument("-S", "--font-size", help="font size",
                        dest="fontsize", action="store", default=128, type=int)
    

    args = parser.parse_args()
    
    getVoice(args.text, args.adest)
    removeSilences(args.adest, args.adest)
    stretch_audio(args.adest, args.adest, args.sp_mul)
    if (args.silence_rm) :
        aggrSilenceRm(args.adest, args.daest)
    loudDistort(args.adest, args.adest, args.gain)
    repeat(args.adest, args.adest, args.sleep, getVideoDuration(args.vid))
    
    shutil.copy(args.vid, args.vdest)
    putText(args.vdest, args.vdest, args.text, args.font, args.fontsize, args.verbose)
    
    

if __name__ == "__main__" :
    main()