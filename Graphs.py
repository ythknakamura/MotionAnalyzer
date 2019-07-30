import Common
import numpy as np
import sys
import os
import math
import matplotlib.pyplot as plt

def windowLeastSquare(tlist, xlist):
    vlist = np.empty_like(tlist)
    alist = np.empty_like(tlist)
    for n in range(0,len(tlist)):
        t0, t1, t2, t3, t4 = 0, 0, 0, 0, 0
        x0, x1, x2 = 0, 0, 0
        for i in range(0,len(tlist)):
            c = 6/Common.FPS
            w = np.exp(-0.5*((tlist[i] - tlist[n])/c)**2)
            t0 += w * tlist[i] ** 0
            t1 += w * tlist[i] ** 1
            t2 += w * tlist[i] ** 2
            t3 += w * tlist[i] ** 3
            t4 += w * tlist[i] ** 4
            x0 += w * xlist[i] * tlist[i] ** 0
            x1 += w * xlist[i] * tlist[i] ** 1
            x2 += w * xlist[i] * tlist[i] ** 2

        D = (t4*t0 - t2*t2) * (t2*t0 - t1*t1) - (t3*t0 - t2*t1)**2
        A = ( (x2*t0 - x0*t2)*(t2*t0 - t1*t1) - (x1*t0-x0*t1)*(t3*t0-t2*t1) ) / D
        B = ( (x1*t0 - x0*t1)*(t4*t0 - t2*t2) - (x2*t0-x0*t2)*(t3*t0-t2*t1) ) / D
        alist[n] = 2*A
        vlist[n] = B + 2*A*tlist[n]
    return vlist, alist
   
def PlotAll(targets):
    fig, axes = plt.subplots(2,1,figsize=(12,9),sharex=True, gridspec_kw={'hspace':0.2})

    for target in targets:
        with open(Common.GraphFile(target), "r") as graphfile:
            data = np.loadtxt(graphfile, delimiter="\t")
        
            tlist = data[:,0]
            xlist = data[:,1]
            vlist = data[:,2]
            
            axes[0].plot(tlist, xlist)
            axes[0].grid(True)
            axes[0].set_ylabel('x [m]')

            axes[1].plot(tlist, vlist, label=target)
            axes[1].grid(True)
            axes[1].set_ylabel('v [m/s]')

            axes[1].set_xlabel('time [s]')
            axes[1].legend()

       
    plt.savefig("graphs.png")
    plt.show()

def Run(target):
    with open(Common.MeasureFile(target), "r") as csvfile:
        data = np.loadtxt(csvfile, delimiter=",")
        
        tlist = data[:,0]
        xlist = data[:,1]
        rlist = np.empty_like(tlist)

        xlist = [x - xlist[0] for x in xlist]
        rlist[0] = 0
        for i in range(1,len(rlist)):
            dr = data[i,3] - data[i-1,3]
            if dr > 0.25:
                dr -= 0.5
            if dr < -0.25:
                dr += 0.5
            rlist[i] =  rlist[i-1] + dr
        if rlist[-1] < 0:
            rlist = -1 * rlist

        area = data[:,3]
        vlist, alist = windowLeastSquare(tlist, xlist)
        vlist = (np.vectorize(lambda v: v if -0.5 < v < 5 else np.nan))(vlist)
        alist = (np.vectorize(lambda a: a if -10 < a < 2 else np.nan))(alist)

        fig, axes = plt.subplots(3,1,figsize=(6,12),sharex=True, gridspec_kw={'hspace':0.2})

        axes[0].plot(tlist, xlist, color='black')
        axes[0].set_xlim((tlist[0], tlist[-1]))
        axes[0].grid(True)
        axes[0].set_ylabel('x [m]')

        axes[1].plot(tlist, vlist, color='black')
        axes[1].grid(True)
        axes[1].set_ylabel('v [m/s]')

        #axes[2].plot(tlist, alist, color='black')
        #axes[2].grid(True)
        #axes[2].set_ylabel('a [m/s2]')
        axes[2].plot(tlist, rlist, color='black')
        axes[2].grid(True)
        axes[2].set_ylabel('angle [x 360 deg]')
        

        axes[2].set_xlim((tlist[0], tlist[-1]))
        axes[2].set_xlabel('time [s]')

        axes[0].set_title(target)
   
        with open(Common.GraphFile(target), mode='w') as f:
            for i, t in enumerate(tlist):
                str = "%f\t%f\t%f\t%f\t%f\n" %(t, xlist[i], vlist[i], alist[i], rlist[i])
                print(str, end="")
                f.write(str)
            
        plt.savefig(Common.GraphPng(target))
        plt.show()

if __name__ == '__main__':
    args = sys.argv
    if len(args)==2:
        target, ext = os.path.splitext(args[1])
        Run(target)
    else:
        print("*** エラー：「python3 %s 動画ファイル名」などと呼び出すこと！" % args[0])