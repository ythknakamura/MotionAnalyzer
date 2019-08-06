import os

### 入力動画のfps
FPS = 240


### 入力動画に回転をかけるかどうか
TRANSPOSE_RAW = None
TRANSPOSE_RAW = "hflip"
#TRANSPOSE_RAW = "transpose=2"


### Cropの際の画像の縮小率
SAMPLE_ON_CROP = 2


### モンタージュの作成間隔 
#MAKE_DETECTED_MONTAGE_STEP = None
MAKE_DETECTED_MONTAGE_STEP = 24*2


### 自動検出後の確認動画を作るかどうか
MAKE_DETECTED_MOVIE = True


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
