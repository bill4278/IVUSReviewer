from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QImage, QPixmap
import sys
import os
import numpy as np
import cv2
import pandas as pd
from pandas import DataFrame
import glob2

from Ui_main import *

class openNPY(QMainWindow, Ui_Mainwindow):
    def __init__(self):
        super(openNPY,self).__init__()
        self.setupUi(self)
        self.setupConnection()
        self.BifuState=0
        self.StentState=0
        self.CalcState=0
        self.AdjVesState=0
        self.stateList=self.ifExistXlsx()
        icon = QIcon()
        icon.addPixmap(QPixmap('bitbug_favicon.ico'))
        self.setWindowIcon(icon)
        self.fileName = []


    def enableUi(self):
        
        self.horizontalSlider.setEnabled(True)
        self.lcdNumber.setEnabled(True)
        
        self.CheckBifurcation.setEnabled(True)
        self.CheckCalcified.setEnabled(True)
        self.CheckStent.setEnabled(True)
        self.CheckAdjcentVessel.setEnabled(True)
        self.NextFrameBtn.setEnabled(True)
        self.LastFrameBtn.setEnabled(True)
        self.SaveBtn.setEnabled(True)

    #@jit(nopython=False)
    def ifExistXlsx(self):
        if os.path.exists('D:/IVUSReviewer.xlsx'):
            df=pd.read_excel('D:/IVUSReviewer.xlsx')
            tempList=[]
            for i in df.index.values:#获取行号的索引，并对其进行遍历：
                #根据i来获取每一行指定的数据 并利用to_dict转成字典
                row_data=df.loc[i,['FrameName','StentState','BifuState','AdjVesState','CalcState',]].to_dict()
                tempList.append(row_data)
            return tempList
        else:
            return []


    def slot_btn_chooseFile(self):
           
        folderChoose = QFileDialog.getExistingDirectory(self,"choose a floder",os.getcwd())
        
        if(folderChoose == ''):
            print('no folder choosed')
        else:
            #print(str(folderChoose).split('/')[-1])        
            
            self.fileName = glob2.glob('{}/**/*.npy'.format(folderChoose),recursive=True)
            if (self.fileName == []):
                self.ShowFileName.setText("no npy file found!")
            else:
                self.horizontalSlider.setMaximum(len(self.fileName)-1)
                if (self.stateList==[]):
                    self.showImage(0)
                    self.enableUi()
                else:
                    self.horizontalSlider.setValue(len(self.stateList))
                    self.enableUi()

    def slot_slider_changed(self):
        picFrame = self.horizontalSlider.value()
        self.lcdNumber.display(picFrame)
        self.showImage(picFrame)
        try:
            lastState = self.stateList[self.horizontalSlider.value()]
            print(lastState)
            self.CheckStatus.setText("Checked")
            self.CheckBifurcation.setChecked(int(lastState['BifuState']))
            self.CheckCalcified.setChecked(int(lastState['CalcState']))
            self.CheckStent.setChecked(int(lastState['StentState']))
            self.CheckAdjcentVessel.setChecked(int(lastState['AdjVesState']))
        except:
            print("do nothing")   
            self.CheckStatus.setText("Not Checked")  
            self.resetCheckBox()   
    
    def showImage(self, imageIndex):
        self.ShowFileName.setText(self.fileName[imageIndex].split('/')[-1])
        imageArray = np.load(self.fileName[imageIndex])
        print(imageArray.shape)
        imageArray = imageArray[int((imageArray.shape[0]-1)/2),:,:]
        img = cv2.resize(cv2.cvtColor(imageArray, cv2.COLOR_GRAY2RGB),(360,360))
        img = QImage(img,img.shape[0],img.shape[1],QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.item=QGraphicsPixmapItem(pix)                      #创建像素图元
        self.scene=QGraphicsScene()                             #创建场景
        self.scene.addItem(self.item)
        self.IVUSViewer.setScene(self.scene)                        #将场景添加至视图
      
        
    def resetCheckBox(self):
        self.CheckBifurcation.setChecked(False)
        self.CheckCalcified.setChecked(False)
        self.CheckStent.setChecked(False)
        self.CheckAdjcentVessel.setChecked(False)
           
    def slot_saveBtn(self):
        FrameName = self.fileName[self.horizontalSlider.value()].split('\\')[-1][:-4]
        print("Frame Name: ", FrameName)
        print("StentState: ",self.StentState)
        print("BifuState: ",self.BifuState)
        print("AdjVesState: ",self.AdjVesState)
        print("CalcState: ",self.CalcState)
        if(self.horizontalSlider.value()<=(len(self.stateList)-1)):
            self.stateList[self.horizontalSlider.value()] = {'FrameName': FrameName,
                    'StentState': str(self.StentState),
                    "BifuState": str(self.BifuState),
                    'AdjVesState': str(self.AdjVesState),
                    'CalcState': str(self.CalcState)}
        else:
            self.stateList.append({'FrameName': FrameName,
                    'StentState': str(self.StentState),
                    "BifuState": str(self.BifuState),
                    'AdjVesState': str(self.AdjVesState),
                    'CalcState': str(self.CalcState)})
        

        #save into xlxs
        self.writeToExcel(self.stateList)
        
        self.resetCheckBox()  
        self.slot_nextFrameBtn()
        
    def writeToExcel(self,contentDict):

        df = pd.DataFrame(contentDict)
        df.to_excel('D:/IVUSReviewer.xlsx', index=False)
  
    def slot_nextFrameBtn(self):
        self.horizontalSlider.setValue(self.horizontalSlider.value()+1)
        try:
            lastState = self.stateList[self.horizontalSlider.value()]
            print(lastState)
            self.CheckStatus.setText("Checked")  
            self.CheckBifurcation.setChecked(int(lastState['BifuState']))
            self.CheckCalcified.setChecked(int(lastState['CalcState']))
            self.CheckStent.setChecked(int(lastState['StentState']))
            self.CheckAdjcentVessel.setChecked(int(lastState['AdjVesState']))
        except:
            print("do nothing")
            self.CheckStatus.setText("Not Checked")  
            self.resetCheckBox()    
    
    def slot_lastFrameBtn(self):
        self.horizontalSlider.setValue(self.horizontalSlider.value()-1)
        try:
            lastState = self.stateList[self.horizontalSlider.value()]
            print(lastState)
            self.CheckStatus.setText("Checked")  
            self.CheckBifurcation.setChecked(int(lastState['BifuState']))
            self.CheckCalcified.setChecked(int(lastState['CalcState']))
            self.CheckStent.setChecked(int(lastState['StentState']))
            self.CheckAdjcentVessel.setChecked(int(lastState['AdjVesState']))
        except:
            print("do nothing")
            self.CheckStatus.setText("Not Checked")  
            self.resetCheckBox() 
        
        
        
        
            
    def CheckBifuState(self, BifuState):
        if BifuState == QtCore.Qt.Checked:
            self.BifuState=1
        else:
            self.BifuState=0

    def CheckStentState(self, StentState):
        if StentState == QtCore.Qt.Checked:
            self.StentState=1
        else:
            self.StentState=0
   
    def CheckCalcifiedState(self, CalcState):
        if CalcState == QtCore.Qt.Checked:
            self.CalcState=1
        else:
            self.CalcState=0 

    def CheckAdjcentVesselState(self, AdjVesState):
        if AdjVesState == QtCore.Qt.Checked:
            self.AdjVesState=1
        else:
            self.AdjVesState=0
       
    def setupConnection(self):

        self.OpenFileBtn.clicked.connect(self.slot_btn_chooseFile)
        self.horizontalSlider.valueChanged.connect(self.slot_slider_changed)
        self.NextFrameBtn.clicked.connect(self.slot_nextFrameBtn)
        self.LastFrameBtn.clicked.connect(self.slot_lastFrameBtn)
        self.SaveBtn.clicked.connect(self.slot_saveBtn)
        
        self.CheckBifurcation.stateChanged.connect(self.CheckBifuState)
        self.CheckCalcified.stateChanged.connect(self.CheckCalcifiedState)
        self.CheckStent.stateChanged.connect(self.CheckStentState)
        self.CheckAdjcentVessel.stateChanged.connect(self.CheckAdjcentVesselState)
        



if __name__=="__main__":
    app = QApplication(sys.argv)    
    win = openNPY()
    win.show()
    sys.exit(app.exec_())