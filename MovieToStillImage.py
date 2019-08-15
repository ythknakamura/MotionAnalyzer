import sys
import os
import subprocess
import Common

def Run(fnameext):
    target, _ = os.path.splitext(fnameext)

    os.makedirs(os.path.join(target, "raw"), exist_ok=True)
    os.makedirs(os.path.join(target, "crop"), exist_ok=True)
    os.makedirs(os.path.join(target, "out"), exist_ok=True)

    try:
        if Common.TRANSPOSE_RAW == "":
            subprocess.run(["ffmpeg", "-i", fnameext,
                "-f", "image2", "-vcodec", "mjpeg", target+"/raw/%04d.jpg"], check=True)
        else:
            subprocess.run(["ffmpeg", "-i", fnameext, "-vf", Common.TRANSPOSE_RAW,
                "-f", "image2", "-vcodec", "mjpeg", target+"/raw/%04d.jpg"], check=True)

    except subprocess.CalledProcessError:
        print("*** エラー：ffmpegの実行エラー")
        exit()
