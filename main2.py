#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import resource
import time
import sys
import configparser
from threading import Thread
from open_files import OpenFile
from compare import CompareFiles
from similarity import SimilarityRatio
from path_handler import path_handler
from video_classifier import video_classifier
from audio_classifier import audio_classifier
from img_class_img import img_class_img
from txt_class_txt import txt_xlass_txt
from ocr import OCR
from db_handler import *

from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QApplication,  QTabWidget,
    QVBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget, QInputDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QUrl

#from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# import numpy as np


# tags
tags_vid = {"0001.mp4":"S","0002.mp4":"N","0003.mp4":"S","0004.avi":"N","0005.mp4":"S","0006.mpg":"N","0007.mp4":"S","0008.mp4":"N","0009.mp4":"S","0010.mp4":"N","0011.mp4":"S","0012.mp4":"S","0013.mp4":"S","0014.mp4":"N","0015.mpg":"S","0016.avi":"S","0017.avi":"S"}
tags_audio = {"0001.mp3":"Mixed","0002.mp3":"Mixed","0003.wav":"Speech","0004.mp3":"Mixed","0005.mp3":"Mixed","0006.wav":"Mixed","0007.mp3":"Mixed","0008.mp3":"Mixed","0009.mp3":"Mixed","0010.mp3":"Speech","0011.mp3":"Mixed","0012.wav":"Speech","0013.mp3":"Mixed"}

templates_path = "/home/husmen/Workspace/PARDUS/templates_logo"
search_terms = ["öğrenci","üniversite","ankara","makedonya", "burs", "sınav"]

def display(item, dataset_path):
    if item == "vid_classification":
        print("# security vids")
        tmp = path_handler(dataset_path, db_name = db_vc, key= 'S', proc="list_files")
        print("# normal vids")
        tmp = path_handler(dataset_path, db_name = db_vc, key= 'N', proc="list_files")

    elif item == "audio_classification":
        print("# Speech Audio")
        tmp = path_handler(dataset_path, db_name = db_ac, key= 'Speech', proc="list_files")
        print("# Music Audio")
        tmp = path_handler(dataset_path, db_name = db_ac, key= 'Music', proc="list_files")
        print("# Mixed Audio")
        tmp = path_handler(dataset_path, db_name = db_ac, key= 'Mixed', proc="list_files")

    elif item == "img_classification":
        pass

class Window(QMainWindow):
    ''' docstring '''

    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')
        self.files_path = path_handler(self.config['DEFAULT']['dataset_path'])
        self.init_ui()
        self.connect_buttons()

    def init_ui(self):
        ''' docstring '''

        #self.com = Communicate()
        # self.com.close_app.connect(self.close)

        self.title = 'KOU DoSA GUI | {}'.format(self.config['DEFAULT']['username'])
 
        self.table_widget = MyTableWidget(self, self.config)
        self.setCentralWidget(self.table_widget)
        self.statusBar()
        self.statusBar().showMessage('Ready')
        #self.setGeometry(300, 300, 1280, 720)
        self.resize(1280, 720)
        self.center()
        self.setWindowTitle(self.title)
        self.show()

    def connect_buttons(self):
        self.table_widget.control3_wid.pushButtons[0].clicked.connect(self.classify_vid)
        self.table_widget.control3_wid.pushButtons[1].clicked.connect(self.classify_audio)
        self.table_widget.control3_wid.pushButtons[2].clicked.connect(self.list_vid)
        self.table_widget.control3_wid.pushButtons[3].clicked.connect(self.list_audio)

    def classify_vid(self):
        self.statusBar().showMessage('Video Classification Running')
        video_classifier(self.files_path.vid, tags = tags_vid)
        self.statusBar().showMessage('Video Classification Done')

    def classify_audio(self):
        self.statusBar().showMessage('Audio Classification Running')
        audio_classifier(self.files_path.audio, tags = tags_audio)
        self.statusBar().showMessage('Audio Classification Done')

    def list_vid(self):    
        self.statusBar().showMessage('Listing Video files by Classification')
        display("vid_classification", self.config['DEFAULT']['dataset_path'])
        self.statusBar().showMessage('Listing Done')

    def list_audio(self):  
        self.statusBar().showMessage('Listing Audio Files by Classification Done')  
        display("audio_classification", self.config['DEFAULT']['dataset_path'])
        self.statusBar().showMessage('Listing Done')
        

    def center(self):
        ''' docstring '''

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connect_server(self):
        ''' docstring '''

        new_tcp_host, ok = QInputDialog.getText(self, 'Connect to Server', 
            'Enter server IP address:')
        
        if ok:
            # create a socket object
            self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            print(new_tcp_host)
            self.sckt.connect((new_tcp_host, TCP_PORT))
            self.conn_status = True

            # send message to server
            msg_to_send = 'Houssem'
            self.sckt.send(msg_to_send.encode('utf-8'))

            # Receive no more than BUFFER_SIZE bytes
            msg = self.sckt.recv(BUFFER_SIZE)

            # print received reply
            print(msg.decode('utf-8'))
            self.statusBar().showMessage(msg.decode('utf-8'))

    def open_file(self):
        ''' docstring '''
        if self.conn_status:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

            if fname[0]:
                fsize = os.path.getsize(fname[0])
                self.sckt.send(str(fsize).encode('utf-8'))

                with open(fname[0], 'rb') as f:
                    data_buffer = f.read(BUFFER_SIZE)
                    while data_buffer:
                        self.sckt.send(data_buffer)
                        data_buffer = f.read(BUFFER_SIZE)

                print('File opened and sent to server')
                self.statusBar().showMessage('File opened and sent to server')
                self.receive_files()
        else:
            self.statusBar().showMessage('First connect to server')
        
    def close_app(self):
        ''' docstring '''
        if self.conn_status:
            self.sckt.close()
        QApplication.instance().quit()
 
class MyTableWidget(QWidget):        
 
    def __init__(self, parent, config):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        #self.tabs.resize(300,200) 
 
        # Add tabs
        self.tabs.addTab(self.tab1,"File Type 1 (Text Documents)")
        self.tabs.addTab(self.tab2,"File Type 2 (Images and PDFs)")
        self.tabs.addTab(self.tab3,"File Type 3 (Video and Audio)")
 
        # Create first tab
        # self.tab3.layout = Tab3ControlWidget(self)
        # self.pushButtons = []
        # self.pushButtons.append(QPushButton("Classify Video"))
        # self.pushButtons.append(QPushButton("Classify Audio"))
        # self.pushButtons.append(QPushButton("List Video with metadata"))
        # self.pushButtons.append(QPushButton("List Audio with metadata"))

        # for button in self.pushButtons:
        #     self.tab3.layout.addWidget(button)

        self.control1_wid = Tab1ControlWidget(self, config)
        self.control2_wid = Tab2ControlWidget(self, config)
        self.control3_wid = Tab3ControlWidget(self, config)
        self.canvas1_wid = CanvasWidget(self)
        self.canvas2_wid = CanvasWidget(self)
        self.canvas3_wid = CanvasWidget(self)

        grid1 = QGridLayout()
        grid1.setSpacing(10)
        grid1.addWidget(self.control1_wid, 1, 0)
        grid1.addWidget(self.canvas1_wid, 1, 1, 1, 7)
        #grid1.addWidget(self.map_wid, 1, 1, 1, 7)
        self.tab1.setLayout(grid1)

        grid2 = QGridLayout()
        grid2.setSpacing(10)
        grid2.addWidget(self.control2_wid, 1, 0)
        grid2.addWidget(self.canvas2_wid, 1, 1, 1, 7)
        #grid1.addWidget(self.map_wid, 1, 1, 1, 7)
        self.tab2.setLayout(grid2)

        grid3 = QGridLayout()
        grid3.setSpacing(10)
        grid3.addWidget(self.control3_wid, 1, 0)
        grid3.addWidget(self.canvas3_wid, 1, 1, 1, 7)
        #grid1.addWidget(self.map_wid, 1, 1, 1, 7)
        self.tab3.setLayout(grid3)

        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
 
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


class MainWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.control_wid = ControlWidget(self)
        #self.map_wid = QWebEngineView(self)
        self.canvas_wid = CanvasWidget(self)

        grid1 = QGridLayout()
        grid1.setSpacing(10)
        grid1.addWidget(self.control_wid, 1, 0)
        grid1.addWidget(self.canvas_wid, 1, 1, 1, 7)
        #grid1.addWidget(self.map_wid, 1, 1, 1, 7)
        self.setLayout(grid1)

class Tab1ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent, config):
        super(Tab1ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.pushButtons = []
        self.pushButtons.append(QPushButton("Calculate Similarity Ratio"))
        self.pushButtons.append(QPushButton("Display Differences"))

        self.pushButtons.append(QPushButton("Hierarchecally Classify Documents"))
        self.pushButtons.append(QPushButton("Watch for Changes"))

        self.pushButtons.append(QPushButton("Watch and Classify"))
        #.pushButtons[0].clicked.connect(self.classify_vid)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        for button in self.pushButtons[:2]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[2:4]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[4:]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(3)

        self.setLayout(self.vbox)

class Tab2ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent, config):
        super(Tab2ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.pushButtons = []
        self.pushButtons.append(QPushButton("Query by String of Characters"))
        self.pushButtons.append(QPushButton("Query by Template"))

        self.pushButtons.append(QPushButton("List Previous Search Results"))
        self.pushButtons.append(QPushButton("Classify Images"))
        self.pushButtons.append(QPushButton("Hierarchecally Classify Images"))
        
        self.pushButtons.append(QPushButton("Watch and Classify"))

        #.pushButtons[0].clicked.connect(self.classify_vid)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        for button in self.pushButtons[:2]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[2:5]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[5:]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(3)

        self.setLayout(self.vbox)


class Tab3ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent, config):
        super(Tab3ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.pushButtons = []
        self.pushButtons.append(QPushButton("Classify Video"))
        self.pushButtons.append(QPushButton("Classify Audio"))
        self.pushButtons.append(QPushButton("List Video with metadata"))
        self.pushButtons.append(QPushButton("List Audio with metadata"))

        #.pushButtons[0].clicked.connect(self.classify_vid)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        for button in self.pushButtons[:2]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[2:]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(3)

        self.setLayout(self.vbox)
        

class ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.connect_btn = QPushButton("Connect to Server")
        self.open_btn = QPushButton("Open File")
        self.plot_btn = QPushButton("Plot Trajectory")
        self.query_btn = QPushButton("Query")
        self.close_btn = QPushButton("Close")

        self.combo_box = QComboBox(self)
        self.combo_box.setToolTip(
            "Choose between full dataset/reduced dataset")
        self.combo_box.addItem("Full Dataset")
        self.combo_box.addItem("Reduced Dataset")

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.connect_btn)
        self.vbox.addWidget(self.open_btn)
        self.vbox.addWidget(self.combo_box)
        self.vbox.addWidget(self.plot_btn)
        self.vbox.addWidget(self.query_btn)
        self.vbox.addWidget(self.close_btn)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)


class CanvasWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent):
        super(CanvasWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.canvas)

        self.setLayout(self.vbox)



if __name__=="__main__":

    APP = QApplication(sys.argv)
    ex = Window()
    sys.exit(APP.exec_())

    # #specify files locations
    # op = sys.argv[1] if len(sys.argv) > 1 else None
    # files_path = path_handler(dataset_path)
    # templates = path_handler(templates_path)
    # #tmp = path_handler(dataset_path, proc="list_files")

    # if not op:
    #     print("# Choose an option #")

    # elif op == "clear_db":
    #     # clear database
    #     db_server = db_handler()
    #     db_server.delete_all()

    # elif op == "audio_classifier":  
    #     startTime = time.time()
    #     # classify audio
    #     audio_classifier(files_path.audio, tags = tags_audio)

    # elif op == "video_classifier":  
    #     startTime = time.time()
    #     # classify video
    #     video_classifier(files_path.vid, tags = tags_vid)
        
    # elif op == "video_display":
    #     # display video classifications
    #     display("vid_classification")

    # elif op == "audio_display":
    #     # display video classifications
    #     display("audio_classification")

    # elif op == "docx_compare": 
    #     startTime = time.time()
    #     CompareFiles(files_path.docx,"docx")

    # elif op == "xlsx_compare": 
    #     startTime = time.time()
    #     CompareFiles(files_path.xlsx,"xlsx")

    # elif op == "pptx_compare": 
    #     startTime = time.time()
    #     CompareFiles(files_path.pptx,"pptx")

    # elif op == "docx_similarity": 
    #     startTime = time.time()
    #     SimilarityRatio(files_path.docx,"docx",method="None")

    # elif op == "xlsx_similarity": 
    #     startTime = time.time()
    #     SimilarityRatio(files_path.xlsx,"xlsx",method="fuzzywuzzy")

    # elif op == "pptx_similarity": 
    #     startTime = time.time()
    #     SimilarityRatio(files_path.pptx,"pptx",method="fuzzywuzzy")

    # elif op == "txt_class_txt": 
    #     startTime = time.time()
    #     for term in search_terms:
    #         txt_xlass_txt(files_path.docx, search = term)
    #         txt_xlass_txt(files_path.pptx, search = term)
    #         txt_xlass_txt(files_path.xlsx, search = term)
    #     #print("this functionality is not implemented yet")


    # elif op == "txt_display": 
    #     startTime = time.time()
    #     print("this functionality is not implemented yet")
    #     #TODO

    # elif op == "img_class_txt": 
    #     startTime = time.time()
    #     for term in search_terms:
    #         img2txt = OCR(files_path.img, lang="tur", search=term)
    #         pdf2txt = OCR(files_path.pdf, lang="tur", search=term, file_type = "pdf")
    
    # elif op == "img_class_img": 
    #     startTime = time.time()
    #     img_class_img(files_path.img, templates = templates.img)
    #     img_class_img(files_path.pdf, templates = templates.img, file_type = "pdf")


    # endTime = time.time()
    # delta = int((endTime - startTime)*1000)
    # display_performance(delta)

