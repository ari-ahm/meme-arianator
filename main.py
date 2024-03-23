import requests

domain = "https://tts.datacula.com/api/"

def check_alive() :
    """checks if the api is alive
    
    Returns :
        0 if everything's ok
        1 if the api response is not ok
        2 if the api is reporting that it's dead
    """
    try :
        res = requests.get(domain)
        if (not res.ok) :
            return 1
        
        if (not res.json()["alive"]) :
            return 2
        
        return 0
    
    except :
        return 1
        

def main() :
    print(check_alive())


if __name__ == "__main__" :
    main()