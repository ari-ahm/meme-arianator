import requests
import os

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
    if (os.path.isfile(dest)) :
        raise FileExistsError("get_voice output file already exists")
    
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

def main() :
    getVoice("به به سلام حال شما چطوره", "mammad.wav")


if __name__ == "__main__" :
    main()