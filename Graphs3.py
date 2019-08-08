import numpy as np
import matplotlib.pyplot as plt
import Common

def windowLeastSquare(tlist, xlist):
    d1 = np.empty_like(tlist)
    d2 = np.empty_like(tlist)
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
        d1[n] = B + 2*A*tlistn
        d2[n] = 2*A
    return d1, d2

def PlotAll(targets):
    _, axes = plt.subplots(2, 2, figsize=(15, 8), sharex=True, gridspec_kw={'hspace':0.2})

    for target in targets:
        with open(Common.GraphFile(target), "r") as graphfile:
            data = np.loadtxt(graphfile, delimiter="\t")

            tlist = data[:, 0]
            xlist = data[:, 1]
            vlist = data[:, 2]
            alist = data[:, 3]
            ylist = data[:, 4]            
            rlist = data[:, 5]
            olist = data[:, 6]

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
        ylist = data[:, 2]
        angle_list = np.empty_like(tlist)

        # x座標の原点の設定
        xlist = [x - xlist[0] for x in xlist]

        # y座標の原点の設定
        ylist = [y - ylist[0] for y in ylist]

        # 角度の計算
        angle_list[0] = 0
        for i in range(1, len(angle_list)):
            dr = data[i, 3] - data[i-1, 3]
            if dr > 0.25:
                dr -= 0.5
            if dr < -0.25:
                dr += 0.5
            angle_list[i] = angle_list[i-1] + dr

        # 最小２乗法で微分量を計算
        vlist, alist  = windowLeastSquare(tlist, xlist)
        omega_list, _ = windowLeastSquare(tlist, angle_list)

        # 上限値の設定
        if Common.V_LIM is not None:
            vmin, vmax = Common.V_LIM
            vlist = (np.vectorize(lambda v: v if vmin < v < vmax else np.nan))(vlist)
        if Common.A_LIM is not None:
            amin, amax = Common.A_LIM
            alist = (np.vectorize(lambda a: a if amin < a < amax else np.nan))(alist)
        if Common.O_LIM is not None:
            omin, omax = Common.O_LIM
            omega_list = (np.vectorize(lambda o: o if omin < o < omax else np.nan))(omega_list)

        # グラフ作成
        graphElements = [
            (xlist, "x [m]", vlist, "v [m/s]", "1"),
            (alist, "a [m/s2]", ylist, "y [m]", "2"),
            (angle_list, "angle [360 deg]", omega_list, "omega [360 deg/s]", "3")]             
        for ele in graphElements:
            fig, axes = plt.subplots(2, 1, figsize=(6, 12), sharex=True, gridspec_kw={'hspace':0.2})
            axes[0].plot(tlist, ele[0], color='black')
            axes[0].set_xlim((tlist[0], tlist[-1]))
            axes[0].grid(True)
            axes[0].set_ylabel(ele[1])
            axes[1].plot(tlist, ele[2], color='black')
            axes[1].grid(True)
            axes[1].set_ylabel(ele[3])
            axes[1].set_xlabel("time [s]")
            fig.suptitle(target + "-" + ele[4])
            plt.savefig(Common.GraphPng(target, ele[4]))
            if show:
                plt.show()

        with open(Common.GraphFile(target), mode='w') as f:
            output = "# time\t x \t v \t a \t y \t angle \t omega\n"
            print(output, end="")
            f.write(output)
            for i, t in enumerate(tlist):
                output = "%f\t%f\t%f\t%f\t%f\t%f\t%f\n" %(t, xlist[i], vlist[i], alist[i], ylist[i], angle_list[i], omega_list[i])
                print(output, end="")
                f.write(output)