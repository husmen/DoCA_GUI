#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import resource
import time
import sys
import logging
import configparser
import webbrowser
from threading import Thread
from open_files import OpenFile
from compare import CompareFiles
from similarity import SimilarityRatio
from path_handler import path_handler
from video_classifier import video_classifier
from audio_classifier import audio_classifier
from img_class_img import img_class_img
from txt_class_txt import txt_class_txt
from ocr import OCR
from db_handler import *
from auto_classifier import AUTO_CLASSIFIER

import folder_watchdog

from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QApplication,  QTabWidget, QPlainTextEdit, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QComboBox, QDesktopWidget, QInputDialog, QDialog)
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

templates_path = "/home/husmen/workspace/PARDUS/templates_logo"
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
        self.table_widget.control1_wid.pushButtons[3].clicked.connect(self.watchdog)
        self.table_widget.control1_wid.pushButtons[4].clicked.connect(self.doc_classify2)

        self.table_widget.control2_wid.pushButtons[0].clicked.connect(self.img_class_txt)
        self.table_widget.control2_wid.pushButtons[1].clicked.connect(self.img_class_img)
        self.table_widget.control2_wid.pushButtons[2].clicked.connect(self.new_img)

        self.table_widget.control3_wid.pushButtons[0].clicked.connect(self.classify_vid)
        self.table_widget.control3_wid.pushButtons[1].clicked.connect(self.classify_audio)
        self.table_widget.control3_wid.pushButtons[2].clicked.connect(self.list_vid)
        self.table_widget.control3_wid.pushButtons[3].clicked.connect(self.list_audio)

        self.table_widget.control4_wid.pushButtons[0].clicked.connect(self.open_db)
        self.table_widget.control4_wid.pushButtons[1].clicked.connect(self.clear_db)

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

    def doc_classify2(self):
        tmp = self.table_widget.control1_wid.combo_box.currentText()
        self.statusBar().showMessage('Classifying new file')
        f1 = self.open_file(type=tmp)
        if not f1:
            self.statusBar().showMessage('Action Cancelled')
        else:
            if tmp == "docx":
                SimilarityRatio([f1],"docx", method="inference")
            elif tmp == "pptx":
                SimilarityRatio([f1],"pptx", method="inference")
            elif tmp == "xlsx":
                SimilarityRatio([f1],"xlsx", method="inference")

    def watchdog(self): 
        folder_watchdog.run(self.config['DEFAULT']['dataset_path'])

    def img_class_img(self):
        self.statusBar().showMessage('Running Template Query on Images')
        tmplt = self.open_file(type="img")
        if not tmplt:
            self.statusBar().showMessage('Action Cancelled')
        else:
            img_class_img(self.files_path.img, templates = [tmplt])
            img_class_img(self.files_path.pdf, templates = [tmplt], file_type = "pdf")
            self.statusBar().showMessage('Query Done')

    def img_class_txt(self):
        term = self.table_widget.control2_wid.textbox.text()
        if term == "":
            self.statusBar().showMessage('You need one query term')
        else:
            self.statusBar().showMessage('Running Text Query on Images')
            img2txt = OCR(self.files_path.img, lang="tur", search=term)
            pdf2txt = OCR(self.files_path.pdf, lang="tur", search=term, file_type = "pdf")
            self.statusBar().showMessage('Query Done')

    def new_img(self):
        f1 = self.open_file(type="pdf")
        if not f1:
            self.statusBar().showMessage('Action Cancelled')
        else:
            classifier = AUTO_CLASSIFIER()
            classifier.classify(os.path.abspath(f1))
            self.statusBar().showMessage('New Image query')

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

    def open_db(self):
        url = self.config['DB']['db_server']+"_utils/index.html"
        self.statusBar().showMessage('Opening Database') 
        webbrowser.open_new(url)

    def clear_db(self):
        self.statusBar().showMessage('Clearing Database')
        db_server = db_handler()
        db_server.delete_all()
        self.statusBar().showMessage('Database Clearing Done')
        

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
        elif type == "img":
            tmp = "Images (*.png *.jpg *.jpeg *.gif)"
        elif type == "pdf":
            tmp = "Images ,PDFs (*.png *.jpg *.jpeg *.gif *.pdf)"
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
        self.tab4 = QWidget()
        #self.tabs.resize(300,200) 
 
        # Add tabs
        self.tabs.addTab(self.tab1,"Type 1 (Text Documents)")
        self.tabs.addTab(self.tab2,"Type 2 (Images and PDFs)")
        self.tabs.addTab(self.tab3,"Type 3 (Video and Audio)")
        self.tabs.addTab(self.tab4,"Database")

        self.control1_wid = Tab1ControlWidget(self, config)
        self.control2_wid = Tab2ControlWidget(self, config)
        self.control3_wid = Tab3ControlWidget(self, config)
        self.control4_wid = Tab4ControlWidget(self, config)
        

        self.tab1.layout = QVBoxLayout(self)
        self.tab2.layout = QVBoxLayout(self)
        self.tab3.layout = QVBoxLayout(self)
        self.tab4.layout = QVBoxLayout(self)

        self.tab1.layout.addWidget(self.control1_wid)
        self.tab2.layout.addWidget(self.control2_wid)
        self.tab3.layout.addWidget(self.control3_wid)
        self.tab4.layout.addWidget(self.control4_wid)

        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)
        self.tab3.setLayout(self.tab3.layout)
        self.tab4.setLayout(self.tab4.layout)

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

        self.pushButtons.append(QPushButton("Classify Documents in dataset"))
        self.pushButtons.append(QPushButton("Watch for Changes"))

        self.pushButtons.append(QPushButton("Classify new Document"))
        #.pushButtons[0].clicked.connect(self.classify_vid)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        self.vbox.addWidget(self.combo_box)
        self.vbox.addStretch(1)
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

        self.textbox = QLineEdit(self)
        self.textbox.setText("Query Term")


        self.pushButtons = []
        self.pushButtons.append(QPushButton("Query by String of Characters"))
        self.pushButtons.append(QPushButton("Query by Template"))
        
        self.pushButtons.append(QPushButton("Classify new Image"))

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        self.vbox.addWidget(self.textbox)
        for button in self.pushButtons[:2]:
            self.vbox.addWidget(button)
        self.vbox.addStretch(1)
        for button in self.pushButtons[2:]:
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

class Tab4ControlWidget(QWidget):
    ''' doc string '''

    def __init__(self, parent, config):
        super(Tab4ControlWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        ''' docstring '''

        self.pushButtons = []
        self.pushButtons.append(QPushButton("Open Database in Browser"))
        self.pushButtons.append(QPushButton("Clear Database"))

        #.pushButtons[0].clicked.connect(self.classify_vid)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(10)
        self.vbox.addStretch(3)
        for button in self.pushButtons:
            self.vbox.addWidget(button)
        self.vbox.addStretch(3)

        self.setLayout(self.vbox)

if __name__=="__main__":
    """ main routine """

    if not os.path.exists("html"):
            os.makedirs("html")

    if not os.path.exists("tmp"):
            os.makedirs("tmp")

    if not os.path.exists("models"):
            os.makedirs("models")

    APP = QApplication(sys.argv)
    ex = Window()
    sys.exit(APP.exec_())
