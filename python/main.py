from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
import os
import requests
import json
import subprocess
from ImageViewer import QImageViewer
from PySide2 import QtCore, QtWidgets, QtGui, QtSql
from PySide2 import QtXml
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication,QMainWindow, QPushButton, QLineEdit, QLabel,QFileDialog,QAction,QMenuBar,QMessageBox,QWidget,QRadioButton,QComboBox,QTextEdit
from PySide2.QtCore import QFile, QObject, QProcess
from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord, QSqlTableModel
from PySide2.QtGui import*
from ImageViewer import QImageViewer


class MainWindow(QMainWindow):
 
    def __init__(self, ui_file, parent=None):
        super(MainWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
    
        loader = QUiLoader()
        self.mainwindow = loader.load(ui_file)
        ui_file.close()
        
        self.lineEdit = self.mainwindow.findChild(QLineEdit, 'lineEdit') 
        self.onlineBtn = self.mainwindow.findChild(QPushButton, 'onlineBtn')    
        self.lokalBtn = self.mainwindow.findChild(QPushButton, 'lokalBtn')
        self.hakkindaAction= self.mainwindow.findChild(QAction, 'hakkindaAction')
        self.lokalBtn.clicked.connect(self.darknetWindowAc)
        self.onlineBtn.clicked.connect(self.nanonetsWindowAc)
        self.hakkindaAction.triggered.connect(self.hakkinda)
        self.mainwindow.setWindowTitle("Toyota Proje | Taha")
        self.mainwindow.show()

    def darknetWindowAc(self):
        self.darknetwindow = darknetWindow(appctxt.get_resource('darknet.ui'))

    def nanonetsWindowAc(self):
        self.nanonetswindow = nanonetsWindow(appctxt.get_resource('nanonets.ui'))
    

    def hakkinda(self):
        QMessageBox.about(self, "Hakkında", "Bu program Toyota SAU Proje ofisi alımları için \nTaha M. Sağlam tarafından hazırlanmıştır. \n2020")    


class nanonetsWindow(QMainWindow):
    def __init__(self, ui_file, parent=None):
        super(nanonetsWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
    
        loader = QUiLoader()
        self.nanonetswindow = loader.load(ui_file)
        ui_file.close()
        
        self.nanonetsDosyaYoluLine = self.nanonetswindow.findChild(QLineEdit, 'nanonetsDosyaYoluLine') 
        #self.nanonetsGraphicsView = self.nanonetswindow.findChild(QGraphicsView, 'nanonetsGraphicsView') 
        self.nanonetsDosyaYoluBtn = self.nanonetswindow.findChild(QPushButton, 'nanonetsDosyaYoluBtn')    
        self.nanonetsTanitBtn = self.nanonetswindow.findChild(QPushButton, 'nanonetsTanitBtn')
        self.dbBtn = self.nanonetswindow.findChild(QPushButton, 'dbBtn')
        self.nanonetsConfigAction= self.nanonetswindow.findChild(QAction, 'nanonetsConfigAction')
        self.nanonetsLabel=self.nanonetswindow.findChild(QLabel, 'nanonetsLabel')
        # self.label.installEventFilter(self)
        self.nanonetsDosyaYoluBtn.clicked.connect(self.nanonetsDosyaSec)
        self.nanonetsTanitBtn.clicked.connect(self.nanonetsYukle)
        self.dbBtn.clicked.connect(self.dbGonder)
        self.nanonetsConfigAction.triggered.connect(self.nanonetsConfigWidgetAc)
        self.nanonetswindow.setWindowTitle("Nanonets | Toyota Proje | Taha")
        self.dbBtn.hide()
        self.nanonetswindow.show()

    def dbGonder(self):
        db = QSqlDatabase.addDatabase('QPSQL')
        db.setHostName("localhost")
        db.setDatabaseName("postgres")
        db.setUserName("postgres")
        db.setPassword("12345")
        if not db.open():
            QtGui.QMessageBox.Warning(None,"Hata", QtCore.QString("Veritabanı hatası %1").arg(db.lastError().text()))
        ok = db.open()
        tableView = QtWidgets.QTableView()

        # sql
        query = QtSql.QSqlQuery()
        translation = {39: None}
        result = query.exec_("INSERT INTO \"nanonetsTablo\" (\"url\", \"dosyaYolu\", \"skor\", \"xminVeri\", \"xmaxVeri\", \"yminVeri\", \"ymaxVeri\") VALUES (\'"+str(urlList).translate(translation)+"\', "+"\'"+nanonetsTanitDosyaYolu+"\', "+"\'"+str(scoreList)+"\', "+"\'"+str(xminList)+"\', "+"\'"+str(xmaxList)+"\', "+"\'"+str(yminList)+"\', "+"\'"+str(ymaxList)+"\')")
        if result:
            areply =  QMessageBox.about(self, "Sonuç", "Veriler veritabanına yüklendi.")
        elif not result:
            print(str(query.lastError()))
            hata = QMessageBox.critical(None,"Hata", str(query.lastError()))


    def nanonetsDosyaSec(self):
        global nanonetsTanitDosyaYolu
        nanonetsTanitDosyaYoluStr, _filtre = QFileDialog.getOpenFileName(None,"Resim seçiniz", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
        if nanonetsTanitDosyaYoluStr:
            nanonetsTanitDosyaYolu=nanonetsTanitDosyaYoluStr
            self.nanonetsDosyaYoluLine.setText(nanonetsTanitDosyaYolu)
            #self.kareCiz(nanonetsTanitDosyaYolu)

    def nanonetsYukle(self):
        self.nanonetsLabel.clear()
        try:
            nanonetsModelID
            nanonetsAPIKey
        except NameError:
            reply = QMessageBox.critical(None, 'Hata','Nanonets parametreleri tanımlanmamış. Konfigürasyonu açmak ister misiniz?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.nanonetsConfigWidgetAc()
        else:
            url = 'https://app.nanonets.com/api/v2/ObjectDetection/Model/'+nanonetsModelID+'/LabelFile/'
            data = {'file': open(nanonetsTanitDosyaYolu, 'rb')}
            response = requests.post(url, auth=requests.auth.HTTPBasicAuth(nanonetsAPIKey, ''), files=data)
            binary = response.content
            output = json.loads(binary)
            print(output)
            if output['message']!='Success':
                hataMesaj=QMessageBox.critical(None, 'Hata',"Nanonets'e giriş yapılmadı. Parametreler yanlış olabilir.\nKonfigürasyonu açmak ister misiniz?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
                if hataMesaj == QMessageBox.StandardButton.Yes:
                    self.nanonetsConfigWidgetAc()

            global xminList,yminList,xmaxList,ymaxList,scoreList,urlList
            xminList=[]
            yminList=[]
            xmaxList=[]
            ymaxList=[]
            scoreList=[]
            urlList=[]
            for results in output['result']:
                for predictions in results['prediction']:
                    xminList.append(predictions['xmin'])
                    yminList.append(predictions['ymin'])
                    xmaxList.append(predictions['xmax'])
                    ymaxList.append(predictions['ymax'])
                    scoreList.append(predictions['score'])
                urlList.append("https://nanonets.imgix.net/"+results['filepath'])
                print(str(urlList))
            if not xminList:
                self.dbBtn.hide()
                self.nanonetsLabel.setText("Görüntüde çizik bulunamadı :(")
            else:
                self.dbBtn.show()
                self.nanonetsLabel.setText("Görüntüde "+str(len(xminList))+ " çizik algılandı.")
                for i in range(len(xminList)):
                    self.nanonetsLabel.setText(self.nanonetsLabel.text()+"\n Çizik "+str(i+1)+ " (%"+str(scoreList[i])[2:4]+") Koordinatları (x,y): min:("+str(xminList[i])+","+str(yminList[i])+") , max:("+str(xmaxList[i])+","+str(ymaxList[i])+")" )
                self.kareCiz(nanonetsTanitDosyaYolu)

    def kareCiz(self,nanonetsTanitDosyaYolu):

        self.pixmap_image = QtGui.QPixmap(nanonetsTanitDosyaYolu)
        self.painterInstance = QtGui.QPainter(self.pixmap_image)
        for i in range(len(xminList)):
            self.penRectangle = QtGui.QPen(QtCore.Qt.green)
            self.penRectangle.setWidth(3)
            self.painterInstance.setPen(self.penRectangle)
            self.painterInstance.drawRect(xminList[i],yminList[i],xmaxList[i]-xminList[i],ymaxList[i]-yminList[i])
        self.imageViewer = QImageViewer()
        self.imageViewer.open(self.pixmap_image)
        self.imageViewer.show()
        del self.painterInstance

    def nanonetsConfigWidgetAc(self):
        self.nanonetsConfigWidget=nanonetsConfigWidget(appctxt.get_resource('nanonetsconfig.ui'))


class nanonetsConfigWidget(QWidget):
    def __init__(self, ui_file, parent=None):
        super(nanonetsConfigWidget, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)        
        loader = QUiLoader()
        self.nanonetsConfigWidget = loader.load(ui_file)
        ui_file.close()
        
        self.nanonetsModelLine = self.nanonetsConfigWidget.findChild(QLineEdit, 'nanonetsModelLine')
        self.nanonetsApiLine = self.nanonetsConfigWidget.findChild(QLineEdit, 'nanonetsApiLine')
        self.nanonetsKaydetBtn=self.nanonetsConfigWidget.findChild(QPushButton,'nanonetsKaydetBtn')

        self.nanonetsKaydetBtn.clicked.connect(self.nanonetsKaydet)
        try:
            nanonetsModelID
        except:
            pass
        else:
            self.nanonetsModelLine.setText(nanonetsModelID)
        try:
            nanonetsAPIKey
        except:
            pass
        else:
            self.nanonetsApiLine.setText(nanonetsAPIKey)
            # self.onlineBtn = self.window.findChild(QPushButton, 'onlineBtn')    
            # self.lokalBtn = self.window.findChild(QPushButton, 'lokalBtn')
            # self.actiondarknet_Yolunu_Belirle= self.darknetwindow.findChild(QAction, 'actiondarknet_Yolunu_Belirle')
            # self.label=self.window.findChild(QLabel, 'label')
            # self.lokalBtn.clicked.connect(self.darknetFotoGonder)
            # self.onlineBtn.clicked.connect(self.nanonetsYukle)
            # self.actiondarknet_Yolunu_Belirle.triggered.connect(self.darknetYoluBelirle)
        self.nanonetsConfigWidget.setWindowTitle("Nanonets konfigurasyonu | Toyota Proje | Taha")
        self.nanonetsConfigWidget.show()
    
    def nanonetsKaydet(self):
        global nanonetsAPIKey
        global nanonetsModelID
        if self.nanonetsApiLine.text():
            nanonetsAPIKey=self.nanonetsApiLine.text()
        if self.nanonetsModelLine.text():
            nanonetsModelID=self.nanonetsModelLine.text()
        self.nanonetsConfigWidget.close()

class darknetWindow(QMainWindow):
    def __init__(self, ui_file, parent=None):
            super(darknetWindow, self).__init__(parent)
            ui_file = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)
        
            loader = QUiLoader()
            self.darknetwindow = loader.load(ui_file)
            ui_file.close()
            
            self.dosyaYoluLine= self.darknetwindow.findChild(QLineEdit, 'dosyaYoluLine') 
            self.videoLinkLine= self.darknetwindow.findChild(QLineEdit, 'videoLinkLine') 
            self.tanitBtn = self.darknetwindow.findChild(QPushButton, 'tanitBtn')
            self.dosyaYoluBtn = self.darknetwindow.findChild(QPushButton, 'dosyaYoluBtn')
            self.darknetConfigAction= self.darknetwindow.findChild(QAction, 'darknetConfigAction')
            self.fotoRadio = self.darknetwindow.findChild(QRadioButton, 'fotoRadio')
            self.videoRadio = self.darknetwindow.findChild(QRadioButton, 'videoRadio')
            self.videoComboBox = self.darknetwindow.findChild(QComboBox, 'videoComboBox')
            self.textEdit = self.darknetwindow.findChild(QTextEdit,'textEdit')
            self.videoComboBox.addItem("Yerel Dosya")
            self.videoComboBox.addItem("Link")
            self.videoComboBox.setDisabled(True)
            self.videoLinkLine.setDisabled(True)
            

            self.darknetLabel=self.darknetwindow.findChild(QLabel, 'darknetLabel')
            self.dosyaYoluBtn.clicked.connect(self.darknetDosyaSec)
            self.tanitBtn.clicked.connect(self.darknetBaslat)
            self.fotoRadio.clicked.connect(self.toggleRadio)
            self.videoRadio.clicked.connect(self.toggleRadio)
            self.videoComboBox.currentIndexChanged.connect(self.toggleCombo)
            self.darknetConfigAction.triggered.connect(self.darknetConfigWidgetAc)
            self.darknetwindow.setWindowTitle("YOLOv4 darknet | Toyota Proje | Taha")
            self.darknetwindow.show()
    def toggleCombo(self):
        if self.videoComboBox.currentIndex()==0:
            self.videoLinkLine.setDisabled(True)
            self.dosyaYoluLine.setDisabled(False)
            self.dosyaYoluBtn.setDisabled(False)
        elif self.videoComboBox.currentIndex()==1:
            self.videoLinkLine.setDisabled(False)
            self.dosyaYoluLine.setDisabled(True)
            self.dosyaYoluBtn.setDisabled(True)
    def toggleRadio(self):
        if self.fotoRadio.isChecked():
            self.videoComboBox.setDisabled(True)
            self.videoLinkLine.setDisabled(True)
            self.dosyaYoluLine.setDisabled(False)
            self.dosyaYoluBtn.setDisabled(False)
        else:
            self.videoComboBox.setDisabled(False)
        if self.videoRadio.isChecked() and self.videoComboBox.currentIndex()==1:
            self.dosyaYoluLine.setDisabled(True)
            self.dosyaYoluBtn.setDisabled(True)
            self.videoLinkLine.setDisabled(False)
            

    
    def darknetConfigWidgetAc(self):
        self.darknetConfigWidget=darknetConfigWidget(appctxt.get_resource('darknetconfig.ui'))
        
    def darknetBaslat(self):
        if self.fotoRadio.isChecked():
            self.darknetFotoGonder()
        if self.videoRadio.isChecked():
            if self.videoComboBox.currentIndex()==0:
                self.darknetVideoGonderYerel()
            elif self.videoComboBox.currentIndex()==1:
                self.darknetVideoGonderLink()
            else:
                pass

                
    def darknetDosyaSec(self):
        global darknetTanitDosyaYolu
        global darknetTanitVideoYolu
        if self.videoRadio.isChecked() and self.videoComboBox.currentIndex()==0:
            darknetTanitVideoYoluStr, _filtre = QFileDialog.getOpenFileName(None,"Video dosyası seçiniz", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
            if darknetTanitVideoYoluStr:
                darknetTanitVideoYolu=darknetTanitVideoYoluStr
                self.dosyaYoluLine.setText(darknetTanitVideoYolu)
        if self.fotoRadio.isChecked():
            darknetTanitDosyaYoluStr, _filtre = QFileDialog.getOpenFileName(None,"Resim dosyası seçiniz", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
            if darknetTanitDosyaYoluStr:
                darknetTanitDosyaYolu=darknetTanitDosyaYoluStr
                self.dosyaYoluLine.setText(darknetTanitDosyaYolu)

    def darknetFotoGonder(self):
        try:
            darknetYolu
        except NameError:
            print("Darknet yolu belirlenmemis")
            reply = QMessageBox.critical(None, 'Hata','darknet klasör yolu ayarlanmamış. Konfigürasyonu açmak ister misiniz?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.darknetConfigWidgetAc()
        else:
            print("Darknet klasoru bulundu")
            self.process = QtCore.QProcess()
            #self.process.setProcessChannelMode(QProcess.ForwardedChannels)
            self.process.setWorkingDirectory(darknetYolu)
            self.process.readyReadStandardOutput.connect(self.stdoutReady)
            self.process.start("darknet", ["detector", "test",darknetData, darknetConfig,darknetWeights,darknetTanitDosyaYolu,"-dont_show","-ext_output"])
            self.process.waitForFinished(-1)
            self.kareCiz()

    def darknetVideoGonderLink(self):
        link=self.videoLinkLine.text()
        self.processyt = QtCore.QProcess()
        self.processyt.setWorkingDirectory(darknetYolu)
        self.processyt.readyReadStandardOutput.connect(self.stdoutReadyYt)
        self.processyt.start("youtube-dl", ["-o","ytdlvideo.mp4",link])
        self.processyt.waitForFinished(-1)
        

        try:
            darknetYolu
        except NameError:
            print("Darknet yolu belirlenmemis")
            reply = QMessageBox.critical(None, 'Hata','darknet klasör yolu ayarlanmamış. Konfigürasyonu açmak ister misiniz?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.darknetConfigWidgetAc()
                
        else:
            pass

    def stdoutReadyYt(self):
        stdouttextYt = self.processyt.readAllStandardOutput().data().decode()
        print(stdouttextYt.strip())
        self.textEdit.append(stdouttextYt[2:len(stdouttextYt)-1])

    def stdoutReady(self):
        stdouttext = self.process.readAllStandardOutput().data().decode()
        print(stdouttext.strip())
        self.textEdit.append(stdouttext[2:len(stdouttext)-1])

    def darknetVideoGonderYerel(self):
        try:
            darknetYolu
        except NameError:
            print("Darknet yolu belirlenmemis")
            reply = QMessageBox.critical(None, 'Hata','darknet klasör yolu ayarlanmamış. Konfigürasyonu açmak ister misiniz?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.darknetConfigWidgetAc()
                
        else:
            print("Darknet vid klasoru bulundu")
            process = QtCore.QProcess()
            process.setProcessChannelMode(QProcess.ForwardedChannels)
            process.setWorkingDirectory(darknetYolu)
            videosoru = QMessageBox.critical(None, 'Video','Video çıkışı MJPEG serverinden verilsin mi? \n Evet seçerseniz servera localhost:8090 adresinden erişebilirsiniz.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            if videosoru == QMessageBox.StandardButton.Yes:
                process.start("darknet", ["detector", "demo",darknetData, darknetConfig,darknetWeights,darknetTanitVideoYolu,"-mjpeg_port","8090","-ext_output","-dont_show"])
            elif videosoru == QMessageBox.StandardButton.No:
                self.darknetLabel.setText("Açılan videoyu kapatmak için ESC tuşuna basın.")
                process.start("darknet", ["detector", "demo",darknetData, darknetConfig,darknetWeights,darknetTanitVideoYolu,"-ext_output"])
                
            stdOut = process.readAllStandardOutput()
            print(stdOut)
            process.waitForFinished(-1)
            #self.darknetLabel.setText("")

    def kareCiz(self):
        self.pixmap_image = QtGui.QPixmap(darknetYolu+'/predictions.jpg')
        self.imageViewer = QImageViewer()
        self.imageViewer.open(self.pixmap_image)
        self.imageViewer.show()

class darknetConfigWidget(QWidget):
    def __init__(self, ui_file, parent=None):
        super(darknetConfigWidget, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)        
        loader = QUiLoader()
        self.darknetConfigWidget = loader.load(ui_file)
        ui_file.close()
        
        self.dirLine = self.darknetConfigWidget.findChild(QLineEdit, 'dirLine')
        self.configLine = self.darknetConfigWidget.findChild(QLineEdit, 'configLine') 
        self.weightsLine = self.darknetConfigWidget.findChild(QLineEdit, 'weightsLine')
        self.dataLine = self.darknetConfigWidget.findChild(QLineEdit, 'dataLine')

        self.dirBtn=self.darknetConfigWidget.findChild(QPushButton,'dirBtn')
        self.configBtn=self.darknetConfigWidget.findChild(QPushButton,'configBtn')
        self.weightsBtn=self.darknetConfigWidget.findChild(QPushButton,'weightsBtn')
        self.dataBtn=self.darknetConfigWidget.findChild(QPushButton,'dataBtn')        
        self.kaydetBtn=self.darknetConfigWidget.findChild(QPushButton,'kaydetBtn')

        self.dirBtn.clicked.connect(self.darknetYoluBelirle)
        self.configBtn.clicked.connect(self.darknetConfigBelirle)
        self.weightsBtn.clicked.connect(self.darknetWeightsBelirle)
        self.dataBtn.clicked.connect(self.darknetDataBelirle)
        self.kaydetBtn.clicked.connect(self.ayarKaydet)
        try:
            darknetYolu
        except:
            pass
        else:
            self.dirLine.setText(darknetYolu)
        try:
            darknetConfig
        except:
            pass
        else:
            self.configLine.setText(darknetConfig)
        try:
            darknetWeights
        except:
            pass
        else:
            self.weightsLine.setText(darknetWeights)
        try:
            darknetData
        except:
            pass
        else:
            self.dataLine.setText(darknetData)
            # self.onlineBtn = self.window.findChild(QPushButton, 'onlineBtn')    
            # self.lokalBtn = self.window.findChild(QPushButton, 'lokalBtn')
            # self.actiondarknet_Yolunu_Belirle= self.darknetwindow.findChild(QAction, 'actiondarknet_Yolunu_Belirle')
            # self.label=self.window.findChild(QLabel, 'label')
            # self.lokalBtn.clicked.connect(self.darknetFotoGonder)
            # self.onlineBtn.clicked.connect(self.nanonetsYukle)
            # self.actiondarknet_Yolunu_Belirle.triggered.connect(self.darknetYoluBelirle)
        self.darknetConfigWidget.setWindowTitle("YOLOv4 darknet konfigurasyonu | Toyota Proje | Taha")
        self.darknetConfigWidget.show()

    def darknetYoluBelirle(self):
        global darknetYolu
        darknetYoluStr = str(QFileDialog.getExistingDirectory(None, "Klasör seç"))
        if darknetYoluStr:
            darknetYolu=darknetYoluStr
            self.dirLine.setText(darknetYolu)
    def darknetConfigBelirle(self):
        global darknetConfig
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        darknetConfigStr, _filtre = QFileDialog.getOpenFileName(None,"Cfg dosyası seç", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
        if darknetConfigStr:
            darknetConfig=darknetConfigStr
            self.configLine.setText(darknetConfig)
    def darknetWeightsBelirle(self):
        global darknetWeights
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        darknetWeightsStr, _filtre = QFileDialog.getOpenFileName(None,"Weights dosyası seç", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
        if darknetWeightsStr:
            darknetWeights=darknetWeightsStr
            self.weightsLine.setText(darknetWeights)
    def darknetDataBelirle(self):
        global darknetData
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        darknetDataStr, _filtre = QFileDialog.getOpenFileName(None,"Data dosyası seç", "","All Files (*);;Python Files (*.py)",options=QFileDialog.Options())
        if darknetDataStr:
            darknetData=darknetDataStr
            self.dataLine.setText(darknetData)
    def ayarKaydet(self):
        self.darknetConfigWidget.close()

    
if __name__ == '__main__':
    
    appctxt = ApplicationContext()
    form = MainWindow(appctxt.get_resource('app.ui'))
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
