import sys
import vlc
import os
from os import remove
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
import time
from threading import Thread
from random import randint
from datetime import datetime
import re

class Window2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galeri")
        self.setWindowIcon(QIcon(resource_path('icon1')))
        #Ekran görüntülerini olduğun pathten çek
        files = []
        for file in os.listdir(resource_path('')):
            if file.endswith(".png"):
                files.append(os.path.join(os.getcwd(), file))
        #Listwidget içine görüntüleri ve patyleri göm
        self.listWidget = QListWidget()
        self.listWidget.setIconSize(QSize(100, 40))
        self.listWidget.setStyleSheet("""
                                QListWidget{
                                    min-height: 100px;
                                    max-height: 100px;
                                }
        """)
        for x in files:
            item = QListWidgetItem(x)
            icon = QIcon()
            icon.addPixmap(QPixmap(x))
            item.setIcon(icon)
            item.setTextAlignment(Qt.AlignLeft)
            self.listWidget.addItem(item)

        #tıklandığında seçili olan itemı alır delete ile item ismiyle siler
        self.listWidget.itemClicked.connect(self._onClicked)

        self.deleteButton = QPushButton("Seçili Olanı Sil")
        self.deleteButton.setStyleSheet("""
                                QPushButton{
                                        padding: 15px 25px;
                                        background-color: red;
                                        border-radius: 15px;
                                        color:white}
                                        .QPushButton:hover{
                                            background-color: darkred;
                                        }
                                QPushButton:hover:!pressed
                                            {
                                            border: 2px solid black;
                                            }"""
                                        )
        self.deleteButton.clicked.connect(self._delete)
        #self.editLineButton.clicked.connect(self._addNote)
        #printer oluştur
        self.printer = QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(True)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        l = QVBoxLayout(self.main_widget)
        l.addWidget(self.scrollArea)
        l.addWidget(self.listWidget)
        l.addWidget(self.deleteButton)

        self._createActions()
        self._createMenus()

        self.imageLabel.setPixmap(
            QPixmap())
        self.scrollArea.setWidgetResizable(True)
        self.scaleFactor = 1
        self.scrollArea.setVisible(True)
        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self._updateActions()

        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()
        self.resize(1000, 600)

    def _addNote(self):
        item=self.listWidget.currentItem()
        item.setText(self.editLine.text())
    #itemı al
    def _onClicked(self, item):
        self.imageLabel.setPixmap(QPixmap(item.text()))
        self.scaleFactor = 1.0
    #itemı sil
    def _delete(self):
        item = self.listWidget.currentItem()
        #itemı güncellemek için takeitemı kullandım
        row=self.listWidget.currentRow()
        self.listWidget.takeItem(row)
        if item!=None:
            remove(item.text())
            QMessageBox.information(self, "Bilgi", str(item.text())+" silindi!", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen Silmek İstediğiniz Ekran Görüntüsünü Seçiniz", QMessageBox.Ok)

    #yazdırma işlemi
    def _print(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(),
                                size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())
    #zoom yap
    def _zoomIn(self):
        self._scaleImage(1.25)
    #zoom out
    def _zoomOut(self):
        self._scaleImage(0.8)
    #scale'ı normale döndür
    def _normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0
    #Ekrana fit et
    def _fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self._normalSize()

        self._updateActions()
    #aksiyonları oluştur
    def _createActions(self):
        self.printAct = QAction(
            "&Yazdır...", self, shortcut="Ctrl+P", enabled=False, triggered=self._print)
        self.exitAct = QAction(
            "Çıkış", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction(
            "Yakınlaştır (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self._zoomIn)
        self.zoomOutAct = QAction(
            "Uzaklaştır (25%)", self, shortcut="Ctrl--", enabled=False, triggered=self._zoomOut)
        self.normalSizeAct = QAction(
            "&Normal Boyut", self, shortcut="Ctrl+S", enabled=False, triggered=self._normalSize)
        self.fitToWindowAct = QAction("&Ekranı Kapla", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self._fitToWindow)
    #menüleri oluştur
    def _createMenus(self):
        self.fileMenu = QMenu("&Dosya", self)

        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&Görüntüle", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
    

    def _updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
    
    def _scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(
            self.scaleFactor * self.imageLabel.pixmap().size())

        self._adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self._adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def _adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet("""
                            MainWindow{
                                background-color:#f2f2f2;
                            }
        
        
   """)
        self.setWindowTitle("Esetron Task Player")
        self.setWindowIcon(QIcon(resource_path('icon2')))
        self.setWindowState(Qt.WindowMaximized)
        self.vlcInstance = vlc.Instance("--no-video-title-show")
        # local olarak almak için new() içine video girdisi girilebilir
        self.videoPlayer = self.vlcInstance.media_player_new()
        self.init_ui()
        self.show()

    def init_ui(self):
        self.videoFrame = QFrame()
        self.videoFrame.setStyleSheet("""QFrame{
            background-color:black;
        }""")
        self.videoFrame.mouseDoubleClickEvent
        
        self.urllineText=QLineEdit("rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov")
        self.urllineText.setStyleSheet("""QLineEdit{
                                        min-height: 40px;
                                        max-height: 40px;
                                        min-width: 300px;
                                        max-width: 300px;
                                        margin-right:500px;
                                        border-radius: 15px;
}""")
        self.urllineButton=QPushButton("Yayın Yükle")
        self.urllineButton.setToolTip("Yayını Yükle")
        self.urllineButton.setStyleSheet("""
                                        QPushButton{
                                            padding: 10px 10px;
                                            font-size: 15px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                            {
                                                border: 2px solid black;
                                            }
  
        """)
        self.urllineButton.clicked.connect(self._urlClicked)

        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.setToolTip("Oynat")
        self.playButton.clicked.connect(self._play)
        self.playButton.setStyleSheet("""
                                        QPushButton{
                                            padding: 15px 25px;
                                            font-size: 24px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                                {
                                                border: 2px solid black;
                                                }
  
        """)
        self.voiceButton = QPushButton()
        self.voiceButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        self.voiceButton.setToolTip("Sustur")
        self.voiceButton.clicked.connect(self._voiceMuted)
        self.voiceButton.setStyleSheet("""
                                        QPushButton{
                                            padding: 15px 25px;
                                            font-size: 24px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                                {
                                                border: 2px solid black;
                                                }
  
        """)
        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setIcon(
            QIcon(resource_path('fullscreen-512.jpg')))
        self.fullscreenButton.setIconSize(QSize(12, 12))
        self.fullscreenButton.setToolTip("Tam Ekran")
        self.fullscreenButton.clicked.connect(self._handleFullscreen)
        self.fullscreenButton.setStyleSheet("""
                                        QPushButton{
                                            padding: 15px 25px;
                                            font-size: 24px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                                {
                                                border: 2px solid black;
                                                }
        """)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMaximum(596)
        self.slider.sliderMoved.connect(self._setPosition)
        self.slider.setStyleSheet("""QSlider::groove:horizontal {
                                                    border: 1px solid #bbb;
                                                    background: white;
                                                    height: 10px;
                                                    border-radius: 4px;
                                                    }
                                                    
                                                    QSlider::sub-page:horizontal {
                                                    background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                                                        stop: 0 #66e, stop: 1 #bbf);
                                                    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                                                        stop: 0 #bbf, stop: 1 #55f);
                                                    border: 1px solid #777;
                                                    height: 10px;
                                                    border-radius: 4px;
                                                    }
                                                    QSlider::handle:horizontal {
                                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #eee, stop:1 #ccc);
                                                    border: 1px solid #777;
                                                    width: 13px;
                                                    margin-top: -2px;
                                                    margin-bottom: -2px;
                                                    border-radius: 4px;
                                                    }                      
""")
        self.volumeslider = QDial(self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.videoPlayer.audio_get_volume())
        self.volumeslider.setToolTip("Ses Ayarı")
        self.volumeslider.valueChanged.connect(self._setVolume)
        self.volumeslider.setStyleSheet("""
        
                            QDial{
                                background-color:#bbf;
                            }
        
        """)
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(100)
        self.progressBar.valueChanged.connect(self._setVolume)
        self.progressBar.setStyleSheet("""QProgressBar{
                                                        
                                                        min-height: 20px;
                                                        max-height: 20px;
                                                        min-width: 40px;
                                                        max-width: 40px;
                                                        margin-top:-5px;
                                                        margin-left: 30px;
                                                    }
                                        QProgressBar::chunk
                                                        {   
                                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                                        }
""")

        self.lcdnumber = QLabel("FPS:0")
        self.lcdnumber.setStyleSheet("""

        
        """)
       

        self.label1 = QLabel(
            "Tam Ekran Modundan Çıkmak İçin F11 Tuşuna Basınız")
        self.label1.setStyleSheet("""QLabel{
                                        min-height: 20px;
                                        max-height: 20px;
                                        min-width: 405px;
                                        max-width: 405px;
                                        font-size:17px;
                                        background-color:white;
                                        border:2px solid black;
                                        border-radius:5px;
}""")
        self.label1.hide()

        self.sayaclabel=QLabel("0"+":"+"0"+"/"+"0"+":"+"0")
        self.sayaclabel.setStyleSheet("""QLabel{
                                        min-height: 20px;
                                        max-height: 20px;
                                        min-width: 60px;
                                        max-width: 60px;
                                        margin-left:20px;
}""")


        self.grab_btn = QPushButton('Ekran Görüntüsü Al')
        self.grab_btn.setToolTip("Kısayol P Tuşu")
        self.grab_btn.clicked.connect(self._screenShot)
        self.grab_btn.setStyleSheet("""
                                        QPushButton{
                                            padding: 15px 25px;
                                            font-size: 24px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                                {
                                                border: 2px solid black;
                                                }
                                        
  
        """)

        self.scGallery_btn = QPushButton('Ekran Görüntüsü Galerisi')
        self.scGallery_btn.setToolTip("Galeri")
        self.scGallery_btn.clicked.connect(self._galleryWindow)
        self.scGallery_btn.setStyleSheet("""
                                        QPushButton{
                                            padding: 15px 25px;
                                            font-size: 24px;
                                            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #bbf, stop: 0.1 #bbf, stop: 0.5 #c2c2d4, stop: 0.9 #66e, stop: 1 #66e);
                                            border-radius: 15px;
                                        }
                                        .QPushButton:hover{
                                            background-color: #66e;
                                        }
                                        QPushButton:hover:!pressed
                                                {
                                                border: 2px solid black;
                                                }
        """)
        self.shortcut = QShortcut(QKeySequence("p"), self)
        self.shortcut.activated.connect(self._screenShot)

        self.shortcut1 = QShortcut(QKeySequence("F11"), self)
        self.shortcut1.activated.connect(self._handleFullscreen)


        self.shortcut4 = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut4.activated.connect(self._volumeUp)

        self.shortcut5 = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut5.activated.connect(self._volumeDown)  

        self.shortcut6 = QShortcut(QKeySequence("esc"), self)
        self.shortcut6.activated.connect(self._handleEscWindow)

        self.fpskapaac = QCheckBox("Video Bilgileri Aç/Kapa")
        self.fpskapaac.setChecked(True)
        self.fpskapaac.stateChanged.connect(self.state_changed)

        self.items = ["4:3", "5:3", "16:9"]
        self.resulation = QComboBox()
        self.resulation.setToolTip("En Boy Oranı")
        self.resulation.setStyleSheet("""QComboBox
{
                                                subcontrol-origin: padding;
                                                subcontrol-position: top right;

                                                padding: 1px 0px 1px 6px;
}""")
        self.resulation.addItems(self.items)
        self.resulation.activated.connect(self._resulationCombo)

        self.sizeLabel=QLabel("Kaynak Çözünürlüğü: "+str(self.videoPlayer.video_get_size()))
        self.sizeLabel.setStyleSheet("""QLabel{
                                        min-height: 20px;
                                        max-height: 20px;                                 
}""")
        self.label=QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        hboxLayout.addWidget(self.playButton)
        hboxLayout.addWidget(self.voiceButton)
        hboxLayout.addWidget(self.volumeslider)
        hboxLayout.addWidget(self.progressBar)
        hboxLayout.addWidget(self.sayaclabel)
        hboxLayout.addWidget(self.slider)
        hboxLayout.addWidget(self.resulation)
        hboxLayout.addWidget(self.fullscreenButton)

        hboxLayout2 = QHBoxLayout()
        hboxLayout2.addWidget(self.grab_btn)
        hboxLayout2.addWidget(self.scGallery_btn)

        hboxLayout3 = QHBoxLayout()
        hboxLayout3.addWidget(self.urllineButton)
        hboxLayout3.addWidget(self.urllineText)
        hboxLayout3.addWidget(self.lcdnumber)
        hboxLayout3.addWidget(self.sizeLabel)
        hboxLayout3.addWidget(self.fpskapaac)

        hboxLayout4 = QHBoxLayout()
        hboxLayout4.addWidget(self.label1)

        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(hboxLayout4)
        vboxLayout.addLayout(hboxLayout3)
        vboxLayout.addWidget(self.videoFrame)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addLayout(hboxLayout2)
        vboxLayout.addWidget(self.label)
        self.setLayout(vboxLayout)
        

        self.isPaused = True
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update)
        

        self.timer2 = QTimer(self)
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self._fps)
        

        
        self.timer4=QTimer(self)
        self.timer4.setInterval(50)
        self.timer4.timeout.connect(self._urlUpdate)

        self.liste2=[self.grab_btn,self.playButton,self.voiceButton,self.volumeslider,self.progressBar,self.slider,
        self.fpskapaac,self.sizeLabel,self.sayaclabel,self.lcdnumber,self.scGallery_btn,self.fullscreenButton,self.resulation]

    # oynat
    def _urlUpdate(self):
        #print(str(self.videoPlayer.get_state())) #gelen yayın stateini incelemek için kullan
        self.videoPlayer.get_state()
        if not self.videoPlayer.is_playing():
            self.urllineButton.setText("Yayın Yükle")
            self.urllineButton.setEnabled(True)
            self.urllineText.setEnabled(True)
            if str(self.videoPlayer.get_state())=="State.Opening":
                self.urllineButton.setText("Yükleniyor...")
                self.urllineButton.setEnabled(False)
            elif str(self.videoPlayer.get_state())=="State.Stopped" or str(self.videoPlayer.get_state())=="State.Error" or str(self.videoPlayer.get_state())=="State.Ended":
                QMessageBox.critical(self, 'Hata',"Girdiğiniz Url ile bağlantı kurulamadı veya yanlış girdiniz.")
                self.urllineButton.setText("Yeniden Dene")
                for i in range(len(self.liste2)):
                    self.liste2[i].setEnabled(False)
                self.fullscreenButton.setEnabled(False)
                self.urllineButton.setEnabled(True)
                self.timer4.stop()
        else:
            for i in range(len(self.liste2)):
                    self.liste2[i].setEnabled(True)
    
            self.urllineButton.setEnabled(False)
            self.urllineText.setEnabled(False)
            self.urllineText.setToolTip("VİDEO OYNAMA HALİNDEYKEN DEĞİŞİKLİK YAPAMAZSINIZ LÜTFEN DURDURUP DENEYİN")
            self.urllineButton.setToolTip("VİDEO OYNAMA HALİNDEYKEN DEĞİŞİKLİK YAPAMAZSINIZ LÜTFEN DURDURUP DENEYİN")
            self.urllineButton.setText("Oynatılıyor..")
    def _urlClicked(self):
        self.timer4.start()
        a=self.urllineText.text() 
        if a[:7]!="rtsp://":
            QMessageBox.critical(self, 'Hata', a+" geçerli bir url değil!")
        else:
            if self.videoPlayer.is_playing():
                self._stop()                   
            self.videoPlayer.set_mrl(a)
            self.videoPlayer.set_hwnd(self.videoFrame.winId())
            self._play()
            self.timer2.start()

    def _play(self):
        if self.videoPlayer.is_playing():
            self.videoPlayer.pause()
            self.playButton.setToolTip("Başlat")
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.isPaused = True
            
        else:
            self.videoPlayer.play()
            self.playButton.setToolTip("Durdur")
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.timer.start()
            self.isPaused = False
        
    # saniyesini ayarla

    def _setPosition(self, position):
        self.videoPlayer.set_position(position/596.0)
        #print(position)
    # sliderı güncelle

    def _update(self):
        self.slider.setValue(self.videoPlayer.get_position() * 596)#alınan length değerine göre
        if not self.videoPlayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self._stop()
    def _stop(self):
        self.videoPlayer.pause()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    # ses kapa
    def _volumeUp(self):
        self.videoPlayer.audio_set_volume(self.videoPlayer.audio_get_volume() + 10)
        self.progressBar.setValue(self.videoPlayer.audio_get_volume())
        self.volumeslider.setValue(self.videoPlayer.audio_get_volume())
    
    def _volumeDown(self):
        self.videoPlayer.audio_set_volume(self.videoPlayer.audio_get_volume() - 10)
        self.progressBar.setValue(self.videoPlayer.audio_get_volume())
        self.volumeslider.setValue(self.videoPlayer.audio_get_volume())

    def _voiceMuted(self):
        self.progressBar.setValue(0)
        self.videoPlayer.audio_set_volume(0)
    # ses ayarı

    def _setVolume(self, Volume):
        self.progressBar.setValue(Volume)
        self.videoPlayer.audio_set_volume(Volume)
    # ekran görüntüsü handlerı

    def _screenShot(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        screen = QApplication.primaryScreen()
        _screenShot = screen.grabWindow(self.videoFrame.winId())
        _screenShot.save(resource_path('sc'+dt_string+'.png'), 'png')
        QMessageBox.information(self, 'Bilgi', "Ekran Görüntüsü Alındı")
    # fullscreen fonk
   
    def _handleFullscreen(self):
        self.liste=[self.urllineText,self.urllineButton,self.grab_btn,self.playButton,self.voiceButton,self.volumeslider,self.progressBar,self.slider,
        self.fpskapaac,self.sizeLabel,self.sayaclabel,self.lcdnumber,self.scGallery_btn,self.fullscreenButton,self.resulation,self.label]
        if self.windowState() & Qt.WindowFullScreen:
            for i in range(len(self.liste)):
                self.liste[i].show()
            self.label1.hide()
            self.setWindowState(Qt.WindowMaximized)
        else:
            for j in range(len(self.liste)):
                self.liste[j].hide()
            self.showFullScreen()
            self._show()
    def _handleEscWindow(self):
        if self.windowState() & Qt.WindowFullScreen:
            for i in range(len(self.liste)):
                self.liste[i].show()
            self.label1.hide()
            self.setWindowState(Qt.WindowMaximized)



    def _galleryWindow(self):
        self.w = Window2()
        self.w.show()

    def _resulationCombo(self):
        a = self.resulation.currentText()
        self.videoPlayer.video_set_aspect_ratio(a)

    def _show(self):
        self.label1.show()
        self.timer3 = QTimer(self)
        self.timer3.setInterval(2500)
        self.timer3.timeout.connect(self._hide)
        self.timer3.start()

    def _hide(self):
        self.label1.hide()
        self.timer3.stop()

    # fps için hesaplama
    def _fps(self):
        self.lcdnumber.setText("FPS: "+str(self.videoPlayer.get_fps()+24))

        self.sizeLabel.setText("Kaynaktan Gelen Çözünürlük Değeri: "+str(self.videoPlayer.video_get_size()))
        self.videoMin=int(self.videoPlayer.get_length())//60000
        self.videoSec=int(self.videoPlayer.get_length()/1000)%60
        self.saniye=int(self.videoPlayer.get_position()*596.48)%60
        self.dakika=int(self.videoPlayer.get_position()*596.48)//60

        self.sayaclabel.setText(str(self.dakika)+":"+str(self.saniye)+"/"+str(self.videoMin)+":"+str(self.videoSec))
        

    def mouseDoubleClickEvent(self, event):
        self._handleFullscreen()
 


    def state_changed(self, int):
        if self.fpskapaac.isChecked() == True:
            self.sizeLabel.show()
            self.urllineButton.show()
            self.urllineText.show()
            self.lcdnumber.show()
        else:
            self.sizeLabel.hide()
            self.urllineText.hide()
            self.urllineButton.hide()
            self.lcdnumber.hide()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setStyle('Fusion')
    window = MainWindow()
    app.exec_()
