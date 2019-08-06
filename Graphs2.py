import numpy as np
import matplotlib.pyplot as plt
import Common

def windowLeastSquare(tlist, xlist):
    vlist = np.empty_like(tlist)
    for n, tlistn in enumerate(tlist):
        t0, t1, t2, t3, t4 = 0, 0, 0, 0, 0
        x0, x1, x2 = 0, 0, 0
        for t, x in zip(tlist, xlist):
            c = 6/Common.FPS
            w = np.exp(-0.5*((t - tlistn)/c)**2)
            t0 += w * t ** 0
            t1 += w * t ** 1
            t2 += w * t ** 2
            t3 += w * t ** 3
            t4 += w * t ** 4
            x0 += w * x * t ** 0
            x1 += w * x * t ** 1
            x2 += w * x * t ** 2

        D = (t4*t0 - t2*t2) * (t2*t0 - t1*t1) - (t3*t0 - t2*t1)**2
        A = ((x2*t0 - x0*t2)*(t2*t0 - t1*t1) - (x1*t0-x0*t1)*(t3*t0-t2*t1)) / D
        B = ((x1*t0 - x0*t1)*(t4*t0 - t2*t2) - (x2*t0-x0*t2)*(t3*t0-t2*t1)) / D
        vlist[n] = B + 2*A*tlistn
    return vlist

def PlotAll(targets):
    _, axes = plt.subplots(2, 2, figsize=(15, 8), sharex=True, gridspec_kw={'hspace':0.2})

    for target in targets:
        with open(Common.GraphFile(target), "r") as graphfile:
            data = np.loadtxt(graphfile, delimiter="\t")

            tlist = data[:, 0]
            xlist = data[:, 1]
            vlist = data[:, 2]
            rlist = data[:, 3]
            slist = data[:, 4]

            axes[0, 0].plot(tlist, xlist)
            axes[0, 0].grid(True)
            axes[0, 0].set_ylabel('x [m]')

            axes[1, 0].plot(tlist, vlist, label=target)
            axes[1, 0].grid(True)
            axes[1, 0].set_ylabel('v [m/s]')

            axes[0, 1].plot(tlist, rlist)
            axes[0, 1].grid(True)
            axes[0, 1].set_ylabel('angle [360 deg]')

            axes[1, 1].plot(tlist, slist, label=target)
            axes[1, 1].grid(True)
            axes[1, 1].set_ylabel('angle [360 deg/s]')


            axes[1, 0].set_xlabel('time [s]')
            axes[1, 0].legend()
            axes[1, 1].set_xlabel('time [s]')
            axes[1, 1].legend()

    plt.savefig("graphs.png")
    plt.show()

def Run(target, show):
    with open(Common.MeasureFile(target), "r") as csvfile:
        data = np.loadtxt(csvfile, delimiter=",")

        tlist = data[:, 0]
        xlist = data[:, 1]
        rlist = np.empty_like(tlist)

        xlist = [x - xlist[0] for x in xlist]
        rlist[0] = 0
        for i in range(1, len(rlist)):
            dr = data[i, 3] - data[i-1, 3]
            if dr > 0.25:
                dr -= 0.5
            if dr < -0.25:
                dr += 0.5
            rlist[i] = rlist[i-1] + dr


        vlist = windowLeastSquare(tlist, xlist)
        vlist = (np.vectorize(lambda v: v if -0.5 < v < 5 else np.nan))(vlist)

        slist = windowLeastSquare(tlist, rlist)
        slist = (np.vectorize(lambda s: s if -3 < s < 3 else np.nan))(slist)

        fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, gridspec_kw={'hspace':0.2})

        axes[0, 0].plot(tlist, xlist, color='black')
        axes[0, 0].set_xlim((tlist[0], tlist[-1]))
        axes[0, 0].grid(True)
        axes[0, 0].set_ylabel('x [m]')

        axes[1, 0].plot(tlist, vlist, color='black')
        axes[1, 0].grid(True)
        axes[1, 0].set_ylabel('v [m/s]')

        axes[0, 1].plot(tlist, rlist, color='black')
        axes[0, 1].grid(True)
        axes[0, 1].set_ylabel('angle [360 deg]')

        axes[1, 1].plot(tlist, slist, color='black')
        axes[1, 1].grid(True)
        axes[1, 1].set_ylabel('angle [360 deg/s]')

        axes[1, 0].set_xlabel('time [s]')
        axes[1, 1].set_xlabel('time [s]')

        fig.suptitle(target)

        with open(Common.GraphFile(target), mode='w') as f:
            for i, t in enumerate(tlist):
                output = "%f\t%f\t%f\t%f\t%f\n" %(t, xlist[i], vlist[i], rlist[i], slist[i])
                print(output, end="")
                f.write(output)

        plt.savefig(Common.GraphPng(target))
        if show:
            plt.show()
