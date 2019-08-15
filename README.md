# MotionAnalyzer


## MotionAnalyzerとは
+ スマートフォンなどで撮った動画を画像解析し、映っている物体の時間ごとの位置・速度など出力するプログラム
+ シェル上で```python3 MotionAnalyzer.py``` などと実行
+ ```setting.json``` にて少しだけ設定を変更可能


## 実行に必要な環境
+ python3
+ ffmpeg
+ openCV
+ gnuplot (なくてもOK)


## 処理内容
1. 動画を連番の静止画に分割
1. 解析範囲を指定する
    + 検出物体は白色のもの
    + 精度向上のため、物体の存在範囲を教えたほうが良い
    + 画像を右＆左クリックで1mの長さを教える必要がある
    + 動画の時間的なトリミングもできる
1. 画像認識で自動計測
1. グラフデータの作成
1. グラフデータの集約


## 最終的に出来上がるもの
+ 動画から切り出した連番ファイル
+ 画像認識の確認用の連番ファイル
+ 画像認識の確認用の動画
+ ストロボ写真風
+ 縦の位置、横の位置、横の速度、横の加速度、角度、角速度の時間ごとの値(csvファイル)
+ そのcsvをグラフ化したもの
+ さらにそのグラフを集約したもの
+ さらにその集約グラフを出力するためのpltファイル(gnuplot用)

