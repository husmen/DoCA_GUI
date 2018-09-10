import os
import numpy as np
import cv2
from wand.image import Image as WandImage
from db_handler import *

class img_class_img():
    def __init__(self, files, templates, file_type = None):
        self.files = files
        self.templates = templates
        self.results = []
        self.db_server = db_handler()

        res = self.db_server.query(db_sh,["term"],query_key="_id", query_value="img_in_img")
        #print(type(res), res)
        res2 = []
        for row in res:
                for _ in row.key[0]:
                    res2.append(_)
            #print(type(res2), res2)
            
        res3 = set(res2)
            #print(type(res3), res3)

        for tmplt in templates:
            if tmplt not in res3:
                    res3.add(tmplt)
                    self.db_server.save(db_sh,{'term' : list(res3)}, doc_id = "img_in_img")

        # Initiate SIFT detector
        self.sift = sift = cv2.xfeatures2d.SIFT_create()

        for f in self.files:
            if file_type == "pdf":
                imgs = self.pdf2img(f)
            else:
                img_t = cv2.imread(f) # trainImage
            for tmplt in self.templates:
                img_q = cv2.imread(tmplt) # queryImage
                good = []
                print("# searching for {} in {}".format(tmplt, f))
                if file_type == "pdf":
                    tmp2 = ""
                    for p_img in imgs:
                        img_t = p_img # trainImage
                        matches = self.sift_run(img_q,img_t)       
                        # ratio test as per Lowe's paper
                        for m,n in matches:
                            if m.distance < 0.5*n.distance:
                                good.append([m])
                    
                else:    
                    matches = self.sift_run(img_q,img_t)  
                    # Apply ratio test as per Lowe's paper  
                    for m,n in matches:
                        if m.distance < 0.5*n.distance:
                            good.append([m])

                if good != []:
                    db_res = self.db_server.query(db_ic_i,["class"],query_key="_id", query_value=f)
                    #print(type(db_res), db_res)
                    db_res2 = []
                    for row in db_res:
                        for _ in row.key[0]:
                            db_res2.append(_)
                    #print(type(db_res2), db_res2)
                    
                    db_res3 = set(db_res2)
                    #print(type(db_res3), db_res3)
                    if tmplt not in db_res3:
                        db_res3.add(tmplt)
                        self.db_server.save(db_ic_i,{'class' : list(db_res3)}, doc_id = f)

    def sift_run(self, img_q, img_t):
        img_q = cv2.cvtColor(img_q, cv2.COLOR_BGR2GRAY)
        img_t = cv2.cvtColor(img_t, cv2.COLOR_BGR2GRAY)

        # extract normal SIFT descriptors
        try:
            (kps_t, descs_t) = self.sift.detectAndCompute(img_t, None)
        except:
            return []
        (kps_q, descs_q) = self.sift.detectAndCompute(img_q, None)
        # BFMatcher with default params
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descs_q,descs_t, k=2)
        return matches

    def pdf2img(self, file):
        name = os.path.basename(file)
        print("### Processing {} ###".format(name))
        img_list = []
        img_buffer=None

        with WandImage(filename=file, resolution=200) as img:
            #img_list.append(img)
            img_buffer=np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
        if img_buffer is not None:
            retval = cv2.imdecode(img_buffer, cv2.IMREAD_UNCHANGED)
            img_list.append(retval)

        return img_list            



