#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import resource
import time
import sys
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

# tags
tags_vid = {"0001.mp4":"S","0002.mp4":"N","0003.mp4":"S","0004.avi":"N","0005.mp4":"S","0006.mpg":"N","0007.mp4":"S","0008.mp4":"N","0009.mp4":"S","0010.mp4":"N","0011.mp4":"S","0012.mp4":"S","0013.mp4":"S","0014.mp4":"N","0015.mpg":"S","0016.avi":"S","0017.avi":"S"}
tags_audio = {"0001.mp3":"Mixed","0002.mp3":"Mixed","0003.wav":"Speech","0004.mp3":"Mixed","0005.mp3":"Mixed","0006.wav":"Mixed","0007.mp3":"Mixed","0008.mp3":"Mixed","0009.mp3":"Mixed","0010.mp3":"Speech","0011.mp3":"Mixed","0012.wav":"Speech","0013.mp3":"Mixed"}

#specify path locations
dataset_path = "/home/husmen/workspace/PARDUS/dosyalar"
#dataset_path = "/home/husmen/workspace/PARDUS/dosyalar_ornek_2"
templates_path = "/home/husmen/workspace/PARDUS/templates_logo"
search_terms = ["öğrenci","üniversite","ankara","makedonya", "burs", "sınav"]


# search for image: 
#TODO

# display image classification:
#TODO
def display_performance(delta):
    print("RAM max usage: {} MB".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024))
    print("Total run time: {} ms".format(delta))

def display(item):
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

if __name__=="__main__":
    #specify files locations
    op = sys.argv[1] if len(sys.argv) > 1 else None
    files_path = path_handler(dataset_path)
    templates = path_handler(templates_path)
    #tmp = path_handler(dataset_path, proc="list_files")

    if not op:
        print("# Choose an option #")

    elif op == "clear_db":
        # clear database
        db_server = db_handler()
        db_server.delete_all()

    elif op == "audio_classifier":  
        startTime = time.time()
        # classify audio
        audio_classifier(files_path.audio, tags = tags_audio)

    elif op == "video_classifier":  
        startTime = time.time()
        # classify video
        video_classifier(files_path.vid, tags = tags_vid)
        
    elif op == "video_display":
        # display video classifications
        display("vid_classification")

    elif op == "audio_display":
        # display video classifications
        display("audio_classification")

    elif op == "docx_compare": 
        startTime = time.time()
        CompareFiles(files_path.docx,"docx")

    elif op == "xlsx_compare": 
        startTime = time.time()
        CompareFiles(files_path.xlsx,"xlsx")

    elif op == "pptx_compare": 
        startTime = time.time()
        CompareFiles(files_path.pptx,"pptx")

    elif op == "docx_similarity": 
        startTime = time.time()
        SimilarityRatio(files_path.docx,"docx",method="None")

    elif op == "xlsx_similarity": 
        startTime = time.time()
        SimilarityRatio(files_path.xlsx,"xlsx",method="fuzzywuzzy")

    elif op == "pptx_similarity": 
        startTime = time.time()
        SimilarityRatio(files_path.pptx,"pptx",method="fuzzywuzzy")

    elif op == "txt_class_txt": 
        startTime = time.time()
        for term in search_terms:
            c(files_path.docx, search = term)
            c(files_path.pptx, search = term)
            c(files_path.xlsx, search = term)
        #print("this functionality is not implemented yet")


    elif op == "txt_display": 
        startTime = time.time()
        print("this functionality is not implemented yet")
        #TODO

    elif op == "img_class_txt": 
        startTime = time.time()
        for term in search_terms:
            img2txt = OCR(files_path.img, lang="tur", search=term)
            pdf2txt = OCR(files_path.pdf, lang="tur", search=term, file_type = "pdf")
    
    elif op == "img_class_img": 
        startTime = time.time()
        #img_class_img(files_path.img, templates = templates.img)
        img_class_img(files_path.pdf, templates = templates.img, file_type = "pdf")


    endTime = time.time()
    delta = int((endTime - startTime)*1000)
    display_performance(delta)

