import os
import os.path as path
import shutil
import glob
import functools

import Common
import MovieToStillImage
import Crop
import AutoAnalyze
import Graphs2

import cv2

NUM_OF_INFO = 6

def safedelete(file):
    if path.exists(file):
        os.remove(file)

def deleteFileIn(dir):
    for file in glob.glob(dir +"/*"):
        os.remove(file)


def toStill(targetNum, info):
    deleteFileIn(os.path.join(targets[targetNum], "raw"))
    MovieToStillImage.Run(targetFiles[targetNum])

def cropping(targetNum,info):
    target = targets[targetNum]
    if not info[0]:
        print("まずは{0}を!".format(step_str[0]))
    else:
        deleteFileIn(os.path.join(target, "crop"))
        safedelete(Common.CalibrationFile(target))
        Crop.Run(target)

def autoAnalyze(targetNum, info):
    target = targets[targetNum]
    if not info[0]:
        print("まずは{0}を!".format(step_str[0]))
    elif not info[1]:
        print("まずは{0}を!".format(step_str[1]))
    else:
        deleteFileIn(os.path.join(target, "out"))
        safedelete(Common.MeasureFile(target))
        safedelete(Common.DetectedMontage(target))
        safedelete(Common.DetectedMovie(target))
        AutoAnalyze.Run(target)

def makeGraph(targetNum, info, show=True):
    target = targets[targetNum]
    if not info[0]:
        print("まずは{0}を!".format(step_str[0]))
    elif not info[1]:
        print("まずは{0}を!".format(step_str[1]))
    elif not info[2]:
        print("まずは{0}を!".format(step_str[2]))
    else:
        safedelete(Common.GraphFile(target))
        safedelete(Common.GraphPng(target))
        Graphs2.Run(target, show)

def doAll(targetNum, info):
    for i in [0,1,2,3]:
        step_cmd[i](targetNum, info)
        info = target_info(targetNum)

def clear(targetNum, info):
    result = input("対象の解析成果を破棄します。[y/N]")
    if result == "y":
        shutil.rmtree(targets[targetNum])



step_str = ["動画から静止画を作成", "静止画のクロッピング", "画像認識で自動計測", "グラフデータの作成", "順に全部やる", "作成物を破棄"]
step_cmd = [toStill, cropping, autoAnalyze, makeGraph, doAll, clear]


def target_info(targetNum):
    target = targets[targetNum]
    info = [False]*(NUM_OF_INFO)
    info[0] = len(glob.glob(target + "/raw/*.jpg")) != 0
    info[1] = len(glob.glob(target + "/crop/*.jpg")) != 0 and path.exists(Common.CalibrationFile(target))
    info[2] = len(glob.glob(target + "/out/*.jpg")) != 0 and path.exists(Common.MeasureFile(target))
    info[3] = path.exists(Common.GraphFile(target))
    info[4] = all(info[:-2])
    return info

def startAnalyze(targetNum):
    while(True):
        print("\n\n\n*************************************\n")
        print("解析対象のファイル:{0}\n".format(targets[targetNum]))
        info = target_info(targetNum)
        for i in range(NUM_OF_INFO):
            print("{0}:{1}\t{2}".format(i, step_str[i], "[完了]" if info[i] else ""))
        n = input("何をする? : ")

        if n.isdigit() and  0 <= int(n) < NUM_OF_INFO:
            step_cmd[int(n)](targetNum, info)
            if int(n)==4:
               return
        else:
            print("終了します")
            return

def toStillforAll(targets):
     for i, target in enumerate(targets):
         info =  target_info(i)
         if not info[0]:
            toStill(i, info)

def plotAllData(targets):
    ts = [target for i, target in enumerate(targets) if target_info(i)[3] ]
    Graphs2.PlotAll(ts)

def twoThreeToAll(targets):
    for i, target in enumerate(targets):
        info =  target_info(i)
        if info[1]:
            autoAnalyze(i, info)
            makeGraph(i,info, False)


while(True):
    targetFiles = glob.glob('*.MOV')
    targets = [t for t, _ in map(path.splitext, targetFiles)]
    for i, target in enumerate(targets):
        print("{0:3d} : {1} {2}".format(i+1, target, " [完了]" if all(target_info(i)[:-1]) else ""))
    print(" a :　すべての動画を静止画に分解")
    print(" b :　すべてに画像解析＆グラフ化を再適応")
    print(" c :　すべてのグラフの集約")

    filenum = input("なにをする？ : ")
    if filenum.isdigit():
        startAnalyze(int(filenum)-1)
    elif filenum == 'a':
        toStillforAll(targets)
    elif filenum == 'b':
        twoThreeToAll(targets)
    elif filenum == 'c':
        plotAllData(targets)
    else:
        exit()

 