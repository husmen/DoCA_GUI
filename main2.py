#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import resource
import time
import sys
import logging
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
    QMainWindow, QPushButton, QFileDialog, QApplication,  QTabWidget, QPlainTextEdit, 
    QVBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget, QInputDialog, QDialog)
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

        self.title = 'KOU DoSA GUI | {}'.format(self.config['DEFAULT']['username'])
 
        self.table_widget = MyTableWidget(self, self.config)
        self.setCentralWidget(self.table_widget)
        self.statusBar()
        self.statusBar().showMessage('Ready')
        #self.setGeometry(300, 300, 1280, 720)
        self.resize(720, 480)
        self.center()
        self.setWindowTitle(self.title)
        self.show()

    def connect_buttons(self):

        self.table_widget.control1_wid.pushButtons[0].clicked.connect(self.doc_similarity)
        self.table_widget.control1_wid.pushButtons[1].clicked.connect(self.doc_compare)
        self.table_widget.control1_wid.pushButtons[2].clicked.connect(self.doc_classify)
        self.table_widget.control1_wid.pushButtons[3].clicked.connect(self.list_audio)

        self.table_widget.control3_wid.pushButtons[0].clicked.connect(self.classify_vid)
        self.table_widget.control3_wid.pushButtons[1].clicked.connect(self.classify_audio)
        self.table_widget.control3_wid.pushButtons[2].clicked.connect(self.list_vid)
        self.table_widget.control3_wid.pushButtons[3].clicked.connect(self.list_audio)

    def doc_compare(self):
        tmp = self.table_widget.control1_wid.combo_box.currentText()
        self.statusBar().showMessage('Comparing 2 files')
        f1 = self.open_file(type=tmp)
        f2 = self.open_file(type=tmp)
        
        if not f1 or not f2:
            self.statusBar().showMessage('Action Cancelled')
        else:
            CompareFiles([f1,f2],tmp)

    def doc_similarity(self):
        tmp = self.table_widget.control1_wid.combo_box.currentText()
        self.statusBar().showMessage('Calculating Similarity of 2 files')
        f1 = self.open_file(type=tmp)
        f2 = self.open_file(type=tmp)
        if not f1 or not f2:
            self.statusBar().showMessage('Action Cancelled')
        else:
            SimilarityRatio([f1,f2],tmp,method="fuzzywuzzy")
    
    def doc_classify(self):
        tmp = self.table_widget.control1_wid.combo_box.currentText()
        self.statusBar().showMessage('Classifying files')
        if tmp == "docx":
            SimilarityRatio(self.files_path.docx,"docx")
        elif tmp == "pptx":
            SimilarityRatio(self.files_path.pptx,"pptx")
        elif tmp == "xlsx":
            SimilarityRatio(self.files_path.xlsx,"xlsx")

    def classify_vid(self):
        startTime = time.time()
        self.statusBar().showMessage('Video Classification Running')
        self.table_widget.canvas3_wid.test
        video_classifier(self.files_path.vid, tags = tags_vid)
        self.statusBar().showMessage('Video Classification Done')

    def classify_audio(self):
        startTime = time.time()
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

    def open_file(self, type):
        ''' docstring '''
        if type == "docx":
            tmp = "Text Documents (*.docx *.doc *.odt)"
        elif type == "pptx":
            tmp = "Presentations (*.pptx *.ppt *.odp)"
        elif type == "xlsx":
            tmp = "Datasheets (*.xlsx *.xls *.ods)"
        fname = QFileDialog.getOpenFileName(self, 'Open file', self.config['DEFAULT']['dataset_path'], tmp)
        if fname[0]:
            self.statusBar().showMessage('File {} opened'.format(fname[0]))
        return fname[0]


        
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

        self.control1_wid = Tab1ControlWidget(self, config)
        self.control2_wid = Tab2ControlWidget(self, config)
        self.control3_wid = Tab3ControlWidget(self, config)

        self.tab1.layout = QVBoxLayout(self)
        self.tab2.layout = QVBoxLayout(self)
        self.tab3.layout = QVBoxLayout(self)

        self.tab1.layout.addWidget(self.control1_wid)
        self.tab2.layout.addWidget(self.control2_wid)
        self.tab3.layout.addWidget(self.control3_wid)

        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)
        self.tab3.setLayout(self.tab3.layout)

        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
 
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

class Tab1ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent, config):
        super(Tab1ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.combo_box = QComboBox(self)
        self.combo_box.setToolTip(
            "Choose Document Type")
        self.combo_box.addItem("docx")
        self.combo_box.addItem("pptx")
        self.combo_box.addItem("xlsx")


        self.pushButtons = []
        self.pushButtons.append(QPushButton("Calculate Similarity Ratio"))
        self.pushButtons.append(QPushButton("Display Differences"))

        self.pushButtons.append(QPushButton("Classify Documents"))
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
        self.vbox.addWidget(self.combo_box)
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

