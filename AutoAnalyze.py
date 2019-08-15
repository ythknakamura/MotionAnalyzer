import os
import subprocess
import math
import glob
import cv2
import numpy as np
import Common

def getContour(image, thresh):
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    element8 = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], np.uint8)
    im_temp = cv2.morphologyEx(im_gray, cv2.MORPH_OPEN, element8)
    im_mask = cv2.morphologyEx(im_temp, cv2.MORPH_CLOSE, element8)
    _, im_thre = cv2.threshold(im_mask, thresh, 255, cv2.THRESH_BINARY)

    if cv2.__version__[0] == "3":
        _, contours, _ = cv2.findContours(
            im_thre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, _ = cv2.findContours(
            im_thre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        return max(contours, key=cv2.contourArea)
    else:
        return None

def Run(target):
    if not os.path.exists(Common.CalibrationFile(target)):
        print("*** エラー *** : Cropが完了していない")
        quit()

    makeMontage = Common.MONTAGE_STEP > 0

    with open(Common.CalibrationFile(target), mode='r') as f:
        zeroPointX = int(f.readline().split('\t')[0])
        onePointX  = int(f.readline().split('\t')[0])
        zeroPointY = int(f.readline().split('\t')[0])
        onePointY  = int(f.readline().split('\t')[0])
        dia = 1/math.sqrt((onePointX - zeroPointX)**2 +(onePointY - zeroPointY)) 
        shift = [int(f.readline().split('\t')[0]), int(f.readline().split('\t')[0])]
        thresh = int(f.readline().split('\t')[0])
        startF, endF = (int(f.readline().split('\t')[0]), int(f.readline().split('\t')[0]))

    files = glob.glob("%s/crop/*.jpg" % target)
    files.sort()

    rawfiles = glob.glob("%s/raw/*.jpg" % target)
    rawfiles.sort()
    rawfiles = rawfiles[startF:endF+1]

    if makeMontage:
        montage = cv2.imread(rawfiles[0], 1)
        traject = cv2.imread(rawfiles[0], 1)

    trajectPoints = []
    with open(Common.MeasureFile(target), mode='w') as f:
        for i, file in enumerate(files):
            image = cv2.imread(file, 1)
            cnt = getContour(image, thresh)
            if cnt is None:
                continue

            area = int(cv2.contourArea(cnt))
            if Common.DETECT_TYPE_RECTANGLE:
                box = cv2.boxPoints(cv2.minAreaRect(cnt))
                centerX = ((box[0][0] + box[1][0] + box[2][0] + box[3][0])/4 - zeroPointX)*dia
                centerY = ((box[0][1] + box[1][1] + box[2][1] + box[3][1])/4 - image.shape[0]/2) * dia
                rec = np.array([box[i][xy]+shift[xy] for i in [0,1,2,3] for xy in [0, 1]], dtype=np.int32).reshape([4,2])               
                intcenter = tuple([ int((rec[0][xy] + rec[1][xy] + rec[2][xy] + rec[3][xy])/4) for xy in [0,1]])
                dx1 = box[0][0] - box[1][0]
                dy1 = box[0][1] - box[1][1]

                dx2 = box[0][0] - box[3][0]
                dy2 = box[0][1] - box[3][1]

                if dx1**2 + dy1**2 > dx2**2 + dy2**2:
                    theta = math.atan2(dx1, dy1)
                else:
                    theta = math.atan2(dx2, dy2)
            else:
                (centerX, centerY), radius = cv2.minEnclosingCircle(cnt)
                intcenter = (int(centerX)+shift[0], int(centerY)+shift[1])
                centerX = (centerX- zeroPointX)*dia
                centerY = (centerY- image.shape[0]/2) * dia
                theta = 0
                
            output = "%.6f, %.6f, %.6f, %.6f, %d, %d\n" % (i/Common.FPS, centerX, centerY, theta / 2 / math.pi, area, i+startF)
            print(output, end="")
            f.write(output)
            

            rawImage = cv2.imread(rawfiles[i], 1)
            rawStr = "time=%4.2f   pos=(%+.3f, %+.3f)   Area=%04d   frame=%04d" % (i/Common.FPS, centerX, centerY, area, i+startF)
            rawImage = cv2.putText(rawImage, rawStr, (10,50), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255), thickness=3)
            if Common.DETECT_TYPE_RECTANGLE:
                rawImage = cv2.polylines(rawImage, [rec], True, (0, 0, 255), thickness=2)
                rawImage = cv2.line(rawImage, (rec[0][0], rec[0][1]), (rec[2][0], rec[2][1]), (0,0,255), thickness=2)
                rawImage = cv2.line(rawImage, (rec[1][0], rec[1][1]), (rec[3][0], rec[3][1]), (0,0,255), thickness=2)
            else:
                rawImage = cv2.circle(rawImage, intcenter, int(radius), (0,0,255), thickness=2)
       
            cv2.imwrite("%s/out/%s" % (target, os.path.basename(file)), rawImage)
            
            if makeMontage and cnt is not None:
                trajectPoints.append(intcenter)
                if i % Common.MONTAGE_STEP == 0:
                    mask = np.zeros_like(montage)
                    if Common.DETECT_TYPE_RECTANGLE:
                        mask = cv2.fillConvexPoly(mask, np.array([rec]), color=(255, 255, 255))
                    else:
                        mask = cv2.circle(mask, intcenter, int(radius),(255,255,255), thickness=-1) 
                    montage = np.where(mask==255, rawImage, montage)
            
    if makeMontage:
        cv2.imwrite(Common.DetectedMontage(target), montage)
        traject = cv2.polylines(traject, [np.array(trajectPoints)], False, (0,0,255), thickness=4)
        cv2.imwrite(Common.Trajectory(target), traject)

    if Common.MAKE_DETECTED_MOVIE:
        subprocess.run(["ffmpeg" , "-framerate", "30", 
                        "-start_number", str(startF), 
                        "-i", target+"/out/%04d.jpg",
                        "-vcodec", "libx264", 
                        "-pix_fmt", "yuv420p", 
                        Common.DetectedMovie(target)], check=True)
