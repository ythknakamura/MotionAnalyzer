import os
import os.path as path
import shutil
import glob

import Common
import MovieToStillImage
import Crop
import AutoAnalyze
import Graphs3

stepCmds = []

def safedelete(file):
    if path.exists(file):
        os.remove(file)

def deleteFileIn(dir):
    for file in glob.glob(dir +"/*"):
        os.remove(file)

def checkInfo(targetNum, checklist):
    info = targetInfo(targetNum)
    for c in checklist:
        if not info[c]:
            print("まずは「{0}」を!".format(stepCmds[0][1]))
            return False
    return True

def toStill(targetNum):
    deleteFileIn(os.path.join(targets[targetNum], "raw"))
    MovieToStillImage.Run(targetFiles[targetNum])
stepCmds.append((toStill, "動画から静止画を作成"))

def cropping(targetNum):
    target = targets[targetNum]
    if checkInfo(targetNum, [0]):
        deleteFileIn(os.path.join(target, "crop"))
        safedelete(Common.CalibrationFile(target))
        Crop.Run(target)
stepCmds.append((cropping, "解析範囲の指定"))

def autoAnalyze(targetNum):
    target = targets[targetNum]
    if checkInfo(targetNum, [0, 1]):
        deleteFileIn(os.path.join(target, "out"))
        safedelete(Common.MeasureFile(target))
        safedelete(Common.DetectedMontage(target))
        safedelete(Common.DetectedMovie(target))
        AutoAnalyze.Run(target)
stepCmds.append((autoAnalyze, "画像認識で自動計測"))

def makeGraph(targetNum, show=True):
    target = targets[targetNum]
    if checkInfo(targetNum, [0, 1, 2]):
        safedelete(Common.GraphFile(target))
        safedelete(Common.GraphPng(target, 0))
        safedelete(Common.GraphPng(target, 1))
        safedelete(Common.GraphPng(target, 2))
        Graphs3.Run(target, show)
stepCmds.append((makeGraph, "グラフデータの作成"))

def doAll(targetNum):
    for i in [0, 1, 2, 3]:
        stepCmds[i][0](targetNum)
stepCmds.append((doAll, "順に全部やる"))

def clear(targetNum):
    result = input("対象の解析成果を破棄します。[y/N]")
    if result == "y":
        shutil.rmtree(targets[targetNum])
stepCmds.append((clear, "作成物を破棄"))

def toStillforAll(targets):
    for i, _ in enumerate(targets):  
        if not targetInfo(i)[0]:
            toStill(i)

def plotAllData(targets):
    ts = [target for i, target in enumerate(targets) if targetInfo(i)[3] ]
    #Graphs3.PlotAll(ts)
    Graphs3.MakePltFile(ts)

def twoThreeToAll(targets):
    for i, _ in enumerate(targets):
        if targetInfo(i)[1]:
            autoAnalyze(i)
            makeGraph(i, False)

def targetInfo(targetNum):
    target = targets[targetNum]
    info = [False] * len(stepCmds)
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
        info = targetInfo(targetNum)
        for i, cmd in enumerate(stepCmds):
            print("{0}:{1}\t{2}".format(i, cmd[1], "[完了]" if info[i] else ""))
        n = input("何をする? : ")

        if n.isdigit() and  0 <= int(n) < len(stepCmds):
            stepCmds[int(n)][0](targetNum)
            if int(n)==4:
                return
        else:
            print("終了します")
            return

while(True):
    exts = [".mov", ".mp4", ".avi", ".m4a", ".wmv", ".mts"]
    targetFiles = [file for file in glob.glob('*') if path.splitext(file)[1].lower() in exts]
    targetFiles.sort()
    targets = [t for t, _ in map(path.splitext, targetFiles)]
    for i, target in enumerate(targets):
        print("{0:3d} : {1} {2}".format(i+1, target, " [完了]" if all(targetInfo(i)[:-1]) else ""))
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
