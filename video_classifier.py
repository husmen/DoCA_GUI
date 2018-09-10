import os
import time
import cv2
#import couchdb
import numpy as np
from threading import Thread
from skimage.measure import compare_ssim as ssim
from db_handler import *
import subprocess
import shlex
import json
import datetime
import resource

class video_classifier():
    def __init__(self, files, tags = None):
        self.media = files
        self.results = []
        self.times = []
        self.results = []
        self.tags = tags
        self.meta = []
        self.db_server = db_handler()

        self.classify()
        self.save_results()
        self.print_results()
        #self.view_db()
        #global db_server   

    def classify(self):
        counter = 0
        for videoPath in self.media:
            startTime = int(round(time.time()))
            dim = (192, 144)
            resize_flag = False
            vid = videoPath.split("/")[-1]
            print("### {}/{} Processing {} ###".format(counter, len(self.media), vid))
            video = cv2.VideoCapture(videoPath)
            #fps = video.get(cv2.CAP_PROP_FPS)
            #res = (video.get(cv2.CAP_PROP_FRAME_WIDTH),video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            width, height, duration, fps = findVideoMetada(videoPath)
            res = (width, height)
            self.meta.append({"res" : res, "fps" : fps, "duration" : duration})
            if res[1] > 144:
                r = res[0]/res[1]
                dim = (int(144 * r), 144)
                resize_flag = True
            counter += 1
            
            suc, img = video.read()
            count_1 = 0
            count_2 = 1
            img_processed = []
            while suc:
                if count_1%int(fps) == 0:
                    img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    if resize_flag:       
                        img_g = cv2.resize(img_g, dim)
                    img_processed.append(img_g)
                    count_2 += 1
                count_1 += 1
                suc, img = video.read()
            #print("\tFPS: {} # Resolution: {} #: New Resolution: {} # Numer of frames: {}".format(round(fps,2), res, dim, len(img_processed)))

            x = 3 # Number of following seconds to compare to
            ratio = []
            points = [i for i in range(0,len(img_processed), int(len(img_processed)/4))[:4]]
            points.append(len(img_processed))

            def procces (start,end,count):
                for i in range(start, end):
                    img1 = img_processed[i]
                    for j in range(count):
                        i_2 = i + j
                        if i_2 < len(img_processed):
                            img2 = img_processed[i+j]
                            tmp = self.compare_images(img1, img2)
                            ratio.append(tmp)

            threads = []
            threads.append(Thread(target=procces, args=(points[0], points[1], x)))
            threads.append(Thread(target=procces, args=(points[1], points[2], x)))
            threads.append(Thread(target=procces, args=(points[2], points[3], x)))
            threads.append(Thread(target=procces, args=(points[3], points[4], x)))

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            avg = sum(ratio) / float(len(ratio))
            avg = round(avg,2)

            if avg >= 0.76:
                    self.results.append(("S",avg))

            else:
                    self.results.append(("N",avg))
            endTime = int(round(time.time()))
            self.times.append(endTime-startTime)
 
    def save_results(self):
        for i, videoPath in enumerate(self.media):
            vid = videoPath.split("/")[-1]
            data = {'name' : vid, 'path' : videoPath, 'kullanici': 'kubra', 'class': self.results[i][0], 'meta' : self.meta[i]}
            self.db_server.save(db_vc, data, doc_id=videoPath)

    def print_results(self):
        print("\n\n### Results ###\n")
        correct_counter = 0

        for i, videoPath in enumerate(self.media):
            vid = videoPath.split("/")[-1]
            if self.tags:
                if self.results[i][0] == self.tags[vid]:
                    correct_counter += 1
                print("# {} # Result: {} ({}) # Actual: {} # Time: {}".format(vid, self.results[i][0], self.results[i][1], self.tags[vid], self.times[i]))
                print("correct answer rate: {}/{}".format(correct_counter, len(self.media)))
            else:
                print("# {} # Result: {} ({}) # Time: {}".format(vid, self.results[i][0], self.results[i][1], self.times[i]))

    def mse(self, imageA, imageB):
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    def compare_images(self, imageA, imageB, algo="ssim"):
        if algo == "ssim":
            m = ssim(imageA, imageB)  # Better results -- Structural Similarity
        else:
            m = self.mse(imageA, imageB)  # Faster results -- Mean squared error
       
        return m

# function to find the resolution of the input video file
def findVideoMetada(pathToInputVideo):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    # prints all the metadata available:
    #import pprint
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(ffprobeOutput['streams'][0])

    # for example, find height and width
    width = int(ffprobeOutput['streams'][0]['width'])
    height = int(ffprobeOutput['streams'][0]['height'])
    duration_ = float(ffprobeOutput['streams'][0]['duration'])
    duration = str(datetime.timedelta(seconds=duration_))
    try:
        nb_frames = int(ffprobeOutput['streams'][0]['nb_frames'])
        fps = nb_frames/duration_
    except:
        try: 
            avg_frame_rate = ffprobeOutput['streams'][0]['avg_frame_rate']
            tmp = avg_frame_rate.split('/')
        except:
            r_frame_rate = ffprobeOutput['streams'][0]['r_frame_rate']
            tmp = r_frame_rate.split('/')
        fps = float(tmp[0])/float(tmp[1])
    
    print(width, height, duration, fps)
    return width, height, duration, fps