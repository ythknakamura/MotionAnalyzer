import os
import json

SETTING_JSON = "setting.json"

setting = {
    "fps" : 240,                    # 入力動画のfps
    "makeDetectedMovie" : True,     # 自動検出後の確認動画を作るかどうか
    "transposeRaw" : "hflip",       # 入力動画に回転をかけるかどうか
    "sampleOnCrop" : 2,             # Cropの際の画像の縮小率
    "motageStep" : 48,              # モンタージュの作成間隔
    "vLimit" : (-5,5),              # グラフの速度の範囲
    "aLimit" : (-10, 2),            # グラフの加速度の範囲
    "oLimit" : (-3,3),              # グラフの角速度の範囲
    }

## transposeRawは""か"hflip"か"transpose=2"


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
FPS = setting.get("fps") or 30
MAKE_DETECTED_MOVIE = setting.get("makeDetectedMovie") or False
TRANSPOSE_RAW = setting.get("transposeRaw") or ""
SAMPLE_ON_CROP = setting.get("sampleOnCrop") or 2
MONTAGE_STEP = setting.get("motageStep") or 0
V_LIM = setting.get("vLimit")
A_LIM = setting.get("aLimit")
O_LIM = setting.get("oLimit")


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

def GraphPng(target, id):
    return os.path.join(target, "%s_graph%s.png"%(target, id))
