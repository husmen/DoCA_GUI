# Load the API (Current warning is related to h5py and has no consequences)
import os
import time
from inaSpeechSegmenter import Segmenter, seg2csv
from db_handler import *

class audio_classifier():
    def __init__(self, files, tags = None):
        self.media = files
        self.results = []
        self.times = []
        self.segmentation = []
        self.results = []
        self.tags = tags
        self.meta = []
        self.db_server = db_handler()
        self.classify()
        self.save_results()
        self.print_results()

    def classify(self):
        self.seg = Segmenter()
        counter = 0
        for audioPath in self.media:
            startTime = int(round(time.time()))
            vid = audioPath.split("/")[-1]
            print("### {}/{} Processing {} ###".format(counter, len(self.media), vid))
            tmp = self.seg(audioPath)
            tmp2 = str(tmp)
            self.segmentation.append(tmp)
            if ("Male" in tmp2 or "Female" in tmp2) and "Music" in tmp2:
                self.results.append("Mixed")
            elif "Music" in tmp2:
                self.results.append("Music")
            elif "Male" in tmp2 or "Female" in tmp2:
                self.results.append("Speech")

            endTime = int(round(time.time()))
            self.times.append(endTime-startTime)
            counter += 1
 
    def save_results(self):
        for i, audioPath in enumerate(self.media):
            vid = audioPath.split("/")[-1]
            data = {'name' : vid, 'path' : audioPath, 'kullanici': user_default, 'class': self.results[i]}
            self.db_server.save(db_ac, data, doc_id=audioPath)

    def print_results(self):
        print("\n\n### Results ###\n")
        correct_counter = 0

        for i, audioPath in enumerate(self.media):
            print(audioPath)
            vid = audioPath.split("/")[-1]
            if self.tags:
                if self.results[i] == self.tags[vid]:
                    correct_counter += 1
                print("# {} # Result: {} # Actual: {} # Time: {}".format(vid, self.results[i], self.tags[vid], self.times[i]))
            else:
                print("# {} # Result: {} # Time: {}".format(vid, self.results[i], self.times[i]))
                
        print("correct answer rate: {}/{}".format(correct_counter, len(self.media)))