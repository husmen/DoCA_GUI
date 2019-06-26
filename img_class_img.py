import os
import numpy as np
import cv2
from wand.image import Image as WandImage
from wand.color import Color as WandColor
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
                print(row)
                #for _ in row.key[0]:
                for _ in row['term']:
                    res2.append(_)
            #print(type(res2), res2)
            
        res3 = set(res2)
            #print(type(res3), res3)

        for tmplt in templates:
            if tmplt not in res3:
                    res3.add(tmplt)
                    self.db_server.save(db_sh,{'term' : list(res3)}, doc_id = "img_in_img")

        # Initiate SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initiate SURF detector
        self.surf = cv2.xfeatures2d.SURF_create(400) # Hessian Threshold to 300-500

        # Initiate BFMatcher
        self.bf = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=False)

        self.algo = "surf"

        for f in self.files:
            if file_type == "pdf":
                imgs = self.pdf2img(f)
            else:
                img_t = cv2.imread(f) # trainImage
            for tmplt in self.templates:
                img_q = cv2.imread(tmplt) # queryImage
                good = []

                # get descriptors of query image
                kps_q, descs_q = self.get_desc(img_q, self.algo)

                print("# searching for {} in {}".format(tmplt, f))
                if file_type == "pdf" and imgs != []:
                    for p_img in imgs:
                        img_t = p_img # trainImage

                        kps_t, descs_t = self.get_desc(img_t, self.algo)

                        if descs_t is not None:
                            matches = self.get_matches(descs_q, descs_t)
   
                            # ratio test as per Lowe's paper
                            if matches is not None:
                                for m,n in matches:
                                    if m.distance < 0.5*n.distance:
                                        good.append([m])
                    
                else:    
                    kps_t, descs_t = self.get_desc(img_t, self.algo)

                    if descs_t is not None:
                        matches = self.get_matches(descs_q, descs_t)
                        # ratio test as per Lowe's paper
                        if matches is not None:
                            for m,n in matches:
                                if m.distance < 0.5*n.distance:
                                    good.append([m])

                if good != []:
                    db_res = self.db_server.query(db_ic_i,["class"],query_key="_id", query_value=f)
                    #print(type(db_res), db_res)
                    db_res2 = []
                    for row in db_res:
                        for _ in row['class']:
                            db_res2.append(_)
                    #print(type(db_res2), db_res2)
                    
                    db_res3 = set(db_res2)
                    #print(type(db_res3), db_res3)
                    if tmplt not in db_res3:
                        db_res3.add(tmplt)
                        self.db_server.save(db_ic_i,{'class' : list(db_res3)}, doc_id = f)

    def get_desc(self, img, algo):
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        try:
            if algo == "sift":
                (kps, descs) = self.sift.detectAndCompute(img, None)
            elif algo == "surf":
                (kps, descs) = self.surf.detectAndCompute(img, None)
        except:
            return None, None

        return kps, descs

    def get_matches(self, d1, d2):
        try:
            matches = self.bf.knnMatch(d1,d2, k=2)
        except:
            return None
            #try:
            #    matches = self.bf.match(d1,d2)
            #except:
            #    return None
        
        return matches

    def sift_run(self, img_q, img_t):
        #print(img_q.shape, img_t.shape)
        if len(img_q.shape) == 3:
            img_q = cv2.cvtColor(img_q, cv2.COLOR_BGR2GRAY)
        if len(img_t.shape) == 3:
            img_t = cv2.cvtColor(img_t, cv2.COLOR_BGR2GRAY)

        # extract normal SIFT descriptors
        try:
            (kps_t, descs_t) = self.sift.detectAndCompute(img_t, None)
            (kps_q, descs_q) = self.sift.detectAndCompute(img_q, None)
        except:
            return []
        
        # BFMatcher with default params
        bf = cv2.BFMatcher(normType=cv2.NORM_L1, crossCheck=False)
        matches = bf.knnMatch(descs_q,descs_t, k=2)
        return matches

    def surf_run(self, img_q, img_t):
        #print(img_q.shape, img_t.shape)
        if len(img_q.shape) == 3:
            img_q = cv2.cvtColor(img_q, cv2.COLOR_BGR2GRAY)
        if len(img_t.shape) == 3:
            img_t = cv2.cvtColor(img_t, cv2.COLOR_BGR2GRAY)

        # extract normal SURF descriptors
        try:
            (kps_t, descs_t) = self.surf.detectAndCompute(img_t, None)
            (kps_q, descs_q) = self.surf.detectAndCompute(img_q, None)
        except:
            return []
        
        # BFMatcher with default params
        bf = cv2.BFMatcher(normType=cv2.NORM_L1, crossCheck=False)
        matches = bf.knnMatch(descs_q,descs_t, k=2)
        return matches

    def pdf2img(self, file):
        name = os.path.basename(file)
        print("### Processing {} ###".format(name))
        img_list = []
        img_buffer = None
        try:
            all_pages = WandImage(filename=file, resolution=200)
        except:
            print("Error opening PDF file")
        else:
            for i, page in enumerate(all_pages.sequence):
                if i >= 1:
                    break
                with WandImage(page) as img:
                    img.format = 'png'
                    img.background_color = WandColor('white')
                    img.alpha_channel = 'remove'
                    try:
                        img_buffer=np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
                    except:
                        pass
                if img_buffer is not None:
                    retval = cv2.imdecode(img_buffer, cv2.IMREAD_UNCHANGED)
                    img_list.append(retval)
                    img_buffer = None

        return img_list    
    
    def pdf2img2(self, file):
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



