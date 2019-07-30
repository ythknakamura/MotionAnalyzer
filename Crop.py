
import tkinter as tk
import glob
import os
import sys
from PIL import Image, ImageTk
import Common

def CropAll(target, files, cropRange):
     for file in files:
            basename =  os.path.basename(file)
            rawName   = os.path.join(target, os.path.join("raw",basename))
            cropName  = os.path.join(target, os.path.join("crop", basename))
            cropImage = Image.open(rawName).crop(cropRange)
            cropImage.save(cropName)
            print(cropName)

class Application(tk.Frame):
    def __init__(self, target, master=None):
        super().__init__()
        
        self.sample=Common.SAMPLE_ON_CROP
        self.target = target
        self.files = glob.glob("%s/raw/*.jpg" % target)
        self.files.sort()
        self.image = Image.open(self.files[0])
        self.image = self.image.resize((self.image.width//self.sample, self.image.height//self.sample))
        self.image_tk = ImageTk.PhotoImage(self.image)      
       
        self.pack()
        self.create_wigets()
        
        self.zero = (0,0)
        self.one = (self.image_tk.width()*self.sample, 0)
        self.startF = 0
        self.endF = len(self.files)

        self.setImage()
        self.showCropRange()


    def create_wigets(self):
        imageWidth = self.image_tk.width();
        imageHeight = self.image_tk.height();

        buttonFrame = tk.Frame(self.master, bd=2)
        buttonFrame.pack(fill=tk.X)

        ctrlFrame = tk.Frame(self.master, bd=2)
        ctrlFrame.pack(fill=tk.X)
        
        self.canvas = tk.Canvas(self.master, width=imageWidth , height=imageHeight)
        self.ioc = self.canvas.create_image(0, 0, image=self.image_tk, anchor='nw') 
        self.canvas.bind("<Button-1>", self.setZeroPoint)
        self.canvas.bind("<Button-3>", self.setOnePoint)
        self.canvas.pack()
        
        tk.Button(buttonFrame, text="開始フレームのセット", width=20, command=self.setStartF).pack(side='left' , padx=25)
        tk.Button(buttonFrame, text="終了フレームのセット", width=20, command=self.setEndF).pack(side='left' , padx=25)
        
        
        self.okButton = tk.Button(buttonFrame, text="OK", width=25, command=self.cropStart)
        self.okButton.pack(side='right', padx=25)
        

        tk.Label(ctrlFrame, text="上:").grid(row=0, column=0, sticky=tk.S)
        self.uScale = tk.Scale(ctrlFrame, from_=0, to=imageHeight*self.sample, 
                               orient='h', command=self.showCropRange)
        self.uScale.set(0)
        self.uScale.grid(row=0, column=1, sticky=(tk.W,tk.E), padx=10)


        tk.Label(ctrlFrame, text="下:").grid(row=1, column=0, sticky=tk.S)
        self.dScale = tk.Scale(ctrlFrame, from_=0, to=imageHeight*self.sample, 
                               orient='h', command=self.showCropRange)
        self.dScale.set(imageHeight*self.sample)
        self.dScale.grid(row=1, column=1, sticky=(tk.W,tk.E), padx=10)


        tk.Label(ctrlFrame, text="左:").grid(row=2, column=0, sticky=tk.S)
        self.lScale = tk.Scale(ctrlFrame, from_=0, to=imageWidth*self.sample, 
                               orient='h', command=self.showCropRange)
        self.lScale.set(0)
        self.lScale.grid(row=2, column=1, sticky=(tk.W,tk.E), padx=10)


        tk.Label(ctrlFrame, text="右:").grid(row=3, column=0, sticky=tk.S)
        self.rScale = tk.Scale(ctrlFrame, from_=0, to=imageWidth*self.sample, 
                               orient='h', command=self.showCropRange)
        self.rScale.set(imageWidth*self.sample)
        self.rScale.grid(row=3, column=1, sticky=(tk.W,tk.E), padx=10)
        


        tk.Label(ctrlFrame, text="検出閾:").grid(row=4, column=0, sticky=tk.S)
        self.cScale = tk.Scale(ctrlFrame, from_=0, to=255, 
                               orient='h', command=self.showCropRange)
        self.cScale.set(125)
        self.cScale.grid(row=4, column=1, sticky=(tk.W,tk.E), padx=10)


        tk.Label(ctrlFrame, text="フレーム:").grid(row=5, column=0, sticky=tk.S)
        self.tScale = tk.Scale(ctrlFrame, from_=0, to=len(self.files),
                               orient='h', command=self.setImage)
        self.tScale.set(0)
        self.tScale.grid(row=5, column=1, sticky=(tk.W,tk.E), padx=10)

        ctrlFrame.columnconfigure(0, weight=0)
        ctrlFrame.columnconfigure(1, weight=1)

        self.master.bind("<Left>",  lambda event:self.tScale.set(self.tScale.get()-1))
        self.master.bind("<Right>", lambda event:self.tScale.set(self.tScale.get()+1))

    def setStartF(self, args=None):
        self.startF = self.tScale.get()
        self.setTitle()
    
    def setEndF(self, args=None):
        self.endF = self.tScale.get()
        self.setTitle()

    def setTitle(self):
        self.master.title("Crop Image  [%s]  start:%d   end:%d "
                         %( self.files[self.tScale.get()], self.startF, self.endF))

    def setImage(self, args=None):
        if 0 <= self.tScale.get() < len(self.files):
            self.image = Image.open(self.files[self.tScale.get()])
            self.image = self.image.resize((self.image.width//self.sample, self.image.height//self.sample))
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.canvas.itemconfig(self.ioc, image=self.image_tk)
            self.setTitle()

    def showCropRange(self, args=None):
        imageWidth = self.image_tk.width();
        imageHeight = self.image_tk.height();
        self.canvas.delete('draw')
        self.canvas.create_rectangle(0, 0, imageWidth, self.uScale.get()//self.sample, 
                                     fill='green', width=0, tag='draw')
        self.canvas.create_rectangle(0, imageHeight, imageWidth, self.dScale.get()//self.sample, 
                                     fill='green', width=0, tag='draw')
        self.canvas.create_rectangle(0, 0, self.lScale.get()//self.sample, imageHeight, 
                                     fill='green', width=0, tag='draw')
        self.canvas.create_rectangle(self.rScale.get()//self.sample, 0, imageWidth, imageHeight, 
                                     fill='green', width=0, tag='draw')
        
        r = 3
        x0 = self.zero[0]//self.sample
        y0 = self.zero[1]//self.sample
        x1 = self.one[0]//self.sample
        y1 = self.one[1]//self.sample

        self.canvas.create_oval(x0-r, y0-r, x0+r, y0+r, fill='red', tag='draw')
        self.canvas.create_oval(x1-r, y1-r, x1+r, y1+r, fill='red',tag='draw')
        self.canvas.create_line(x0, y0, x1, y1, fill='red',tag='draw')

    def cropStart(self):
        with open(Common.CalibrationFile(self.target), mode='w') as f:
            output  = "%d\n%d\n" % (self.zero[0] - self.lScale.get(), self.one[0] - self.lScale.get())
            output += "%d\n%d\n" % (self.zero[1] - self.uScale.get(), self.one[1] - self.uScale.get())
            output += "%d\n%d\n" % (self.lScale.get(), self.uScale.get())
            output += "%d\n" % (self.cScale.get())
            output += "%d\n%d\n" % (self.startF, self.endF)
            f.writelines(output)
       
        cropRange= (self.lScale.get(), self.uScale.get(), self.rScale.get(), self.dScale.get())
        self.master.quit()
        self.master.destroy()
        CropAll(self.target, self.files[self.startF:self.endF+1], cropRange)
       
    def setZeroPoint(self, event):
        self.zero = (event.x * self.sample, event.y * self.sample)
        self.showCropRange()
        pass

    def setOnePoint(self, event):
        self.one = (event.x * self.sample, event.y * self.sample)
        self.showCropRange()
        pass


def Run(target):
    root = tk.Tk()
    myapp = Application(target=target, master=root)
    myapp.mainloop()

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print("*** エラー：「python3 %s 動画ファイル名」などと呼び出すこと！" % args[0])

    else:
        target, ext = os.path.splitext(args[1])
        root = tk.Tk()
        myapp = Application(target=target, master=root)
        myapp.mainloop()
