import numpy as np
import matplotlib.pyplot as plt
import Common


graphElements = [
    (1, "x",  "x  [m]"), 
    (2, "vx", "vx [m/s]"), 
    (3, "ax", "ax [m/s2]"), 
    (4, "y",  "y  [m]"),
    (5, "vy", "yv [m/s]"),
    (6, "ay", "ya [m/s2]"),
    (7, "w",  "w  [360 deg]"), 
    (8, "vw", "vw [360 deg/s]"),
    (9, "aw", "aw [360 deg/s2]")]

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

def MakePltFile(targets):
    lineStyles = " ".join([str(1) for _ in targets])
    targetList = " ".join(targets)
    pltString = """
reset

##############################################
### gnuplot に読み込ませるためのスクリプト ###
##############################################


### 表示したいもの以外の行頭に#をつける
###################################################
#tate_label = "x [m]"		        ;tate_rownum = 2
tate_label = "v [m/s]"		        ;tate_rownum = 3
#tate_label = "a [m/s2] "       	;tate_rownum = 4
#tate_label = "y [m]"	            ;tate_rownum = 5
#tate_label = "yv [m/s]"	        ;tate_rownum = 6
#tate_label = "ya [m/s2]"	        ;tate_rownum = 7
#tate_label = "anlge [360 deg]"	    ;tate_rownum = 8
#tate_label = "omega [360 deg/s]"	;tate_rownum = 9
###################################################


###　プロットの設定
targets   = "{targetList}"
line_styles = "{lineStyles}"

### 線種の定義
set style line 1 lw 2 lc rgb "black"
set style line 2 lw 2 lc rgb "red"
set style line 3 lw 2 lc rgb "blue"
set style line 4 lw 2 lc rgb "green"
set style line 5 lw 2 lc rgb "orange"


set grid		# グリッドを表示
set zeroaxis		# 縦横軸の表示

###################################################
### 以下、編集不要

set term qt
num = words(targets)
files =""
do for [id=1:num]{{
    files = files . sprintf("%s/%s_graph.txt ", word(targets, id),  word(targets, id))
}}
set xlabel "time [s]"
set ylabel tate_label
plot for[id=1:num] word(files, id) us 1:tate_rownum w l ls word(line_styles, id) ti word(targets, id)

set term push
set term pngcairo
set output "gnuplot_graph.png"
replot
set output
set term pop
""".format(targetList=targetList, lineStyles=lineStyles)
    print(pltString)
    with open("gnuplotgraph.plt", mode='w') as f:
        f.write(pltString)

def PlotAll(targets):
    for id, name, ylabel in graphElements:
        if not name in Common.GRAPH_OUT:
            continue

        fig, ax = plt.subplots(figsize=(8, 6))
        for target in targets:
            with open(Common.GraphFile(target), "r") as graphfile:
                data = np.loadtxt(graphfile, delimiter="\t")
                yoko_list = data[:, 0]
                tate_list= data[:, id]
                ax.plot(yoko_list, tate_list, label=target)

        ax.grid(True)
        ax.set_xlabel('time [s]')
        ax.set_ylabel(ylabel)
        ax.legend()
        fig.tight_layout()
        fig.savefig("graphs_%s.png"%name)
        fig.show()
    
def Run(target, show):
    with open(Common.MeasureFile(target), "r") as csvfile:
        data = np.loadtxt(csvfile, delimiter=",")

        tlist = data[:, 0]
        xlist = data[:, 1]
        ylist = data[:, 2]
        wlist = np.empty_like(tlist)

        # x座標の原点の設定
        xlist = [x - xlist[0] for x in xlist]

        # y座標の原点の設定
        ylist = [y - ylist[0] for y in ylist]

        # 角度の計算
        wlist[0] = 0
        for i in range(1, len(wlist)):
            dr = data[i, 3] - data[i-1, 3]
            if dr > 0.25:
                dr -= 0.5
            if dr < -0.25:
                dr += 0.5
            wlist[i] = wlist[i-1] + dr

        # 最小２乗法で微分量を計算
        vxlist, axlist = windowLeastSquare(tlist, xlist)
        vylist, aylist = windowLeastSquare(tlist, ylist)
        vwlist, awlist = windowLeastSquare(tlist, wlist)

        # 上限値の設定
        if Common.V_LIM is not None:
            vmin, vmax = Common.V_LIM
            vxlist = (np.vectorize(lambda v: v if vmin < v < vmax else np.nan))(vxlist)
            vylist = (np.vectorize(lambda v: v if vmin < v < vmax else np.nan))(vylist)
            vwlist = (np.vectorize(lambda v: v if vmin < v < vmax else np.nan))(vwlist)
        if Common.A_LIM is not None:
            amin, amax = Common.A_LIM
            axlist = (np.vectorize(lambda a: a if amin < a < amax else np.nan))(axlist)
            aylist = (np.vectorize(lambda a: a if amin < a < amax else np.nan))(aylist)
            awlist = (np.vectorize(lambda a: a if amin < a < amax else np.nan))(awlist)
        

        # グラフ作成
        plotList = [tlist, xlist, vxlist, axlist, ylist, vylist, aylist, wlist, vwlist, awlist]
        for id, name, ylabel in graphElements:
            if not name in Common.GRAPH_OUT:
                continue

            fig, ax = plt.subplots(figsize=(8, 6))
        
            ax.plot(plotList[0], plotList[id], color='black')
            ax.set_xlim((plotList[0][0], plotList[0][-1]))
            ax.grid(True)
            ax.set_xlabel('time [s]')
            ax.set_ylabel(ylabel)
            fig.tight_layout()
            fig.savefig(Common.GraphPng(target, name))
            if show:
                fig.show()
 
   
        with open(Common.GraphFile(target), mode='w') as f:
            output = "# time\t x \t vx \t ax \t y \t vy \t ay \t w \t vw \t aw\n"
            f.write(output)
            for i, t in enumerate(tlist):
                output = "%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f\n" %(t, xlist[i], vxlist[i], axlist[i], ylist[i], vylist[i], aylist[i], wlist[i], vwlist[i], awlist[i])
                f.write(output)