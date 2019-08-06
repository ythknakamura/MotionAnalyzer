import Common
import cv2
import sys
import numpy as np
import glob
import os
import subprocess
import math

def getRectangle(image, thresh):
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    element8 = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], np.uint8)
    im_temp = cv2.morphologyEx(im_gray, cv2.MORPH_OPEN, element8)
    im_mask = cv2.morphologyEx(im_temp, cv2.MORPH_CLOSE, element8)
    _, im_thre = cv2.threshold(im_mask, thresh, 255, cv2.THRESH_BINARY)
   
    if(cv2.__version__[0] == "3"):
        _, contours, _ = cv2.findContours(
        im_thre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, _ = cv2.findContours(
        im_thre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        return max(contours,key=cv2.contourArea)
    else:
        return None

def Run(target):
    if not os.path.exists(Common.CalibrationFile(target)):
            print("*** エラー *** : Cropが完了していない")
            quit()

    makeMontage = Common.MAKE_DETECTED_MONTAGE_STEP != None


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
    
    with open(Common.MeasureFile(target), mode='w') as f:
        for i, file in enumerate(files):
            image = cv2.imread(file, 1)
            cnt = getRectangle(image, thresh)
            if cnt is not None:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                centerX = ((box[0][0] + box[1][0] + box[2][0] + box[3][0])/4 - zeroPointX)*dia
                centerY = ((box[0][1] + box[1][1] + box[2][1] + box[3][1])/4 - image.shape[0]/2) * dia
                area = int(cv2.contourArea(cnt))

                dx1 = box[0][0] - box[1][0] 
                dy1 = box[0][1] - box[1][1] 

                dx2 = box[0][0] - box[3][0] 
                dy2 = box[0][1] - box[3][1] 

                if dx1**2 + dy1**2 > dx2**2 + dy2**2:
                    theta = math.atan2(dx1, dy1)
                else:
                    theta = math.atan2(dx2, dy2)

                #theta = math.atan2(box[0][0] - box[1][0] , box[0][1] - box[1][1])

                output = "%.6f, %.6f, %.6f, %.6f, %d, %d\n" % (i/Common.FPS, centerX, centerY, theta / 2 / math.pi, area, i+startF)
                print(output, end="")
                f.write(output)

                rec = np.array([box[i][xy]+shift[xy] for i in [0,1,2,3] for xy in [0,1]], dtype=np.int32).reshape([4,2])               
            else:
                rec = []

            rawImage = cv2.imread(rawfiles[i], 1)
            rawStr = "time=%4.2f   pos=(%+.3f, %+.3f)   Area=%04d   frame=%04d" % (i/Common.FPS, centerX, centerY, area, i+startF)
            rawImage = cv2.putText(rawImage, rawStr, (10,50), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255), thickness=3)
            if len(rec)==4:
                rawImage = cv2.polylines(rawImage, [rec], True,(0,0,255), thickness=2)
                rawImage = cv2.line(rawImage, (rec[0][0], rec[0][1]), (rec[2][0], rec[2][1]), (0,0,255), thickness=2)
                rawImage = cv2.line(rawImage, (rec[1][0], rec[1][1]), (rec[3][0], rec[3][1]), (0,0,255), thickness=2)
            cv2.imwrite("%s/out/%s" % (target, os.path.basename(file)), rawImage)
            if makeMontage and i%Common.MAKE_DETECTED_MONTAGE_STEP==0:
                mask = np.zeros_like(montage)
                mask = cv2.fillConvexPoly(mask, np.array([rec]), color=(255,255,255))
                montage = np.where(mask==255, rawImage, montage)
            
            
    if makeMontage:
        cv2.imwrite(Common.DetectedMontage(target), montage)

    if Common.MAKE_DETECTED_MOVIE:
        subprocess.run(["ffmpeg" , "-framerate", "30", 
                        "-start_number", str(startF), 
                        "-i", target+"/out/%04d.jpg",
                        "-vcodec", "libx264", 
                        "-pix_fmt", "yuv420p", 
                        Common.DetectedMovie(target)], check=True)

if __name__ == '__main__':
    args = sys.argv
    if len(args)==2:
        target, ext = os.path.splitext(args[1])
        Run(target)
    else:
        print("*** エラー：「python3 %s 動画ファイル名」などと呼び出すこと！" % args[0])