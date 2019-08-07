import os
import json

SETTING_JSON = "setting.json"

setting = {
    "fps" : 240,                    # 入力動画のfps
    "makeDetectedMovie" : True,     # 自動検出後の確認動画を作るかどうか
    #"transposeRaw" : "hflip",       # 入力動画に回転をかけるかどうか
    "transposeRaw" : "transpose=2",
    "sampleOnCrop" : 2,             # Cropの際の画像の縮小率
    "motageStep" : 48,              # モンタージュの作成間隔 
    }

def SaveSetting():
    f = open(SETTING_JSON, "w")
    json.dump(setting, f, indent=4)

def LoadSetting():
    global setting
    if os.path.exists(SETTING_JSON):
        f = open(SETTING_JSON, "r")
        setting = json.load(f)
    else:
        SaveSetting()
    print("### MotionAnalyzer")
    print(json.dumps(setting,indent=4))
    print("##################\n\n")


LoadSetting()
FPS = setting["fps"]
MAKE_DETECTED_MOVIE = setting["makeDetectedMovie"]
TRANSPOSE_RAW = setting["transposeRaw"]
SAMPLE_ON_CROP = setting["sampleOnCrop"]
MONTAGE_STEP = setting["motageStep"]


def CalibrationFile(target):
    return os.path.join(target, "%s_calibration.txt"%target)

def MeasureFile(target):
    return os.path.join(target, "%s_measure.txt"%target)

def DetectedMovie(target):
    return os.path.join(target, "%s_detected.mp4"%target)

def DetectedMontage(target):
    return os.path.join(target, "%s_detected.jpg"%target)

def GraphFile(target):
    return os.path.join(target, "%s_graph.txt"%target)

def GraphPng(target):
    return os.path.join(target, "%s_graph.png"%target)
