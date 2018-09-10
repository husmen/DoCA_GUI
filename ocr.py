""" module for performing OCR """
import cv2
import couchdb
import numpy as np
import fitz

try:
    import Image
except ImportError:
    from PIL import Image

from wand.image import Image as WandImage
import pytesseract
import textract
from db_handler import *

class OCR():
    def __init__(self, files, lang = None, search = None, file_type = None):
        self.files = files
        self.lang = lang
        self.search = search.lower()
        self.text = []
        self.db_server = db_handler()
        res = self.db_server.query(db_ocr,["_id","content"])
        self.ocr_history = {}
        for row in res:
            self.ocr_history[row.key[0]] = row.key[1]
        #print(self.ocr_history)


        for f in files:
            #print(pytesseract.image_to_string(Image.open(f), lang=None))
            print("# OCR for: {} #".format(f))
            if f in self.ocr_history.keys():
                self.text.append(self.ocr_history[f])

            elif file_type == "pdf":
                doc = fitz.open(f)
                fontlist = doc.getPageFontList(0)
                if fontlist == [] :
                    imgs = self.pdf2img(f)
                    tmp2 = ""
                    for img in imgs:
                        ocv_img = self.img_preprocess(img)
                        tmp = str(pytesseract.image_to_string(ocv_img, lang=self.lang))
                        tmp2 += tmp
                    self.text.append(tmp2)

                else :
                    tmp = textract.process(f, encoding='utf-8')
                    self.text.append(tmp)
                
                self.db_server.save(db_ocr, {'content': tmp},doc_id = f)

            else:   
                pil_img = Image.open(f)
                ocv_img = cv2.imread(f)

                ocv_img = self.img_preprocess(ocv_img)   

                tmp = pytesseract.image_to_string(ocv_img, lang=self.lang)
                self.text.append(tmp)
                #print(tmp)
                self.db_server.save(db_ocr, {'content': tmp},doc_id = f)

        if self.search:
            res = self.db_server.query(db_sh,["term"],query_key="_id", query_value="txt_in_img")
            #print(type(res), res)
            res2 = []
            for row in res:
                for _ in row.key[0]:
                    res2.append(_)
            #print(type(res2), res2)
            
            res3 = set(res2)
            #print(type(res3), res3)

            
            if self.search not in res3:
                res3.add(self.search)
                self.db_server.save(db_sh,{'term' : list(res3)}, doc_id = "txt_in_img")

            for _ in range(0,len(files)):
                self.find(_)
            

    def skew_correction(self, img):
            """ """
            self.img = img
            # flip background and forground
            self.img = cv2.bitwise_not(self.img)
            # threshold the image, setting all foreground pixels to 255 and all background pixels to 0
            thresh = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            #thresh2 = cv2.threshold(img,222,255,cv2.THRESH_BINARY)[1]
            #thresh2 = cv2.threshold(self.img, 255, 0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            #cv2.imshow("thresh1", thresh)
            #cv2.imshow("thresh2", thresh2)
            #cv2.waitKey(0)
            #cv2.imshow("original", img)
            #cv2.imshow("thresh1", thresh)
            #cv2.imshow("thresh2", thresh2)
            #self.img2 = cv2.bitwise_not(thresh)
            #cv2.imshow("flipped", self.img2)

            # grab the (x, y) coordinates of all pixel values that
            # are greater than zero, then use these coordinates to
            # compute a rotated bounding box that contains all
            # coordinates
            coords = np.column_stack(np.where(thresh > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            # the `cv2.minAreaRect` function returns values in the
            # range [-90, 0); as the rectangle rotates clockwise the
            # returned angle trends to 0 -- in this special case we
            # need to add 90 degrees to the angle
            if angle < -45:
                angle = -(90 + angle)
            
            # otherwise, just take the inverse of the angle to make
            # it positive
            else:
                angle = -angle

            # rotate the image to deskew it
            (h, w) = self.img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h),
                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

            # show the output image
            #print("[INFO] angle: {:.3f}".format(angle))
            #cv2.imshow("Input", img)
            #cv2.imshow("Rotated", rotated)
            cv2.waitKey(0)


            return rotated

    def img_denoise(self, img):
        self.img = img
        # adjust contrast
        self.img = cv2.multiply(self.img, 1.2)

        # create a kernel for the erode() function
        kernel = np.ones((1, 1), np.uint8)

        # erode() the image to bolden the text
        self.img = cv2.erode(self.img, kernel, iterations=1)


        return self.img

    def clean_bg(self,img):
        self.img = img
        # Gaussian filtering
        #self.img = cv2.blur(self.img,(3,3),0)
        #blur = cv2.GaussianBlur(self.img,(3,3),0)
        #smooth = cv2.addWeighted(blur,1.5,img,-0.5,0)
        # threshhold
        #self.img = cv2.threshold(self.img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        self.img = cv2.bitwise_not(self.img)
        self.img = cv2.threshold(self.img,200,255,cv2.THRESH_TRUNC)[1]
        self.img = cv2.bitwise_not(self.img)
        #self.img = cv2.bitwise_not(self.img)
        #self.img = cv2.threshold(self.img,255,255,cv2.THRESH_TRUNC)[1]
        #self.img = cv2.bitwise_not(self.img)

        return self.img

        #thresh = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        #thresh2 = cv2.threshold(img,222,255,cv2.THRESH_BINARY)[1]

    
    def find(self, f_index):
        print("# searching for {} in {}".format(self.search, self.files[f_index]))

        self.res = self.find_all(self.search,self.text[f_index].lower())
        self.res2 = list(self.res)
        #print(self.res2)

        if len(self.res2) > 0:
            #data = {'img_id' : self.files[_], 'kullanici': 'kubra', "class" :{self.search: True}, 'locations': str(self.res2) }
            #data = {'img_id' : self.files[_], 'kullanici': 'kubra', "class" :{self.search: True}}
            #self.db_server.save(db_ic_t,data,doc_id = self.files[_])

            db_res = self.db_server.query(db_ic_t,["class"],query_key="_id", query_value=self.files[f_index])
            #print(type(db_res), db_res)
            db_res2 = []
            for row in db_res:
                for _ in row.key[0]:
                    db_res2.append(_)
            #print(type(db_res2), db_res2)
            
            db_res3 = set(db_res2)
            #print(type(db_res3), db_res3)
            if self.search not in db_res3:
                db_res3.add(self.search)
                self.db_server.save(db_ic_t,{'class' : list(db_res3)}, doc_id = self.files[f_index])
            
    def find_all(self, sub, a_str):
        #print(type(sub),type(a_str))
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub) # use start += 1 to find overlapping matches

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

    def img_preprocess(self, img):
        # grayscale
        ocv_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
                # clean background
        ocv_img = self.clean_bg(ocv_img)
                
                # denoising
        ocv_img = cv2.fastNlMeansDenoising(ocv_img,None,15,15,10)
                #ocv_img = self.img_denoise(ocv_img)
                
                # skew correction
        ocv_img = self.skew_correction(ocv_img)

                # resize
        height, width = ocv_img.shape[:2]
        ocv_img = cv2.resize(ocv_img, (4*width,4*height)) 
                #cv2.imwrite("saved.jpg",ocv_img)
                
                # sharpen
                #blurred_image = cv2.blur(resized_image,(3,3))
                #cv2.imwrite("saved_.jpg",blurred_image)

        return ocv_img
