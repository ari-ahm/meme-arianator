# Arianator

This is a tool for making a specific type of memes that have been going viral recently(march of 2024) in Iranian meme communities using AI. it uses piper to get it's audio.

# Setting up
Clone the project and download fa_IR-gyro-medium.onnx and fa_IR-gyro-medium.onnx.json into assets folder from [here](https://huggingface.co/gyroing/Persian-Piper-Model-gyro/tree/main).

# Howto
```
usage: Arianator [-h] [-v] [-o ADEST] [-O VDEST] [--speed-mul SP_MUL] [-G GAIN] [--aggressive-silence-rm]
                 [-s SLEEP] [-V VID] [-f FONT] [-S FONTSIZE] [-m BGMUSIC]
                 text

This tool helps you make kaka-sangi-dancing to LAYE BARDAR memes

positional arguments:
  text                  narration to be used in the video

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -o ADEST, --audio-output ADEST
                        destination audio file
  -O VDEST, --video-output VDEST
                        destination video file
  --speed-mul SP_MUL    speed multiplier which controlls how slow the audio is going to be
  -G GAIN, --gain GAIN  gain used to distort the audio. in db
  --aggressive-silence-rm
                        remove silences aggressively
  -s SLEEP, --sleep SLEEP
                        number of seconds to wait between each repetition
  -V VID, --video VID   Input video to be used as background
  -f FONT, --font FONT  Font path to be used
  -S FONTSIZE, --font-size FONTSIZE
                        font size
  -m BGMUSIC, --music BGMUSIC
                        background music

Made by Arian
```