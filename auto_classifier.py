import os
from db_handler import *
from img_class_img import img_class_img
from ocr import OCR

class AUTO_CLASSIFIER():
    def __init__(self):
        self.db_server = db_handler()
        res = self.db_server.query(db_ocr,["_id","content"])
        self.ocr_history = {}
        for row in res:
            self.ocr_history[row.key[0]] = row.key[1]

        res = self.db_server.query(db_sh,["_id","term"])
        self.search_history = {}
        for row in res:
            tmp = []
            for _ in row.key[1]:
                    tmp.append(_)
            self.search_history[row.key[0]] = tmp

        print(self.search_history)

    def classify(self, path):
        print("auto_classifying " + path)
        if path.endswith("jpg") or path.endswith("png") or path.endswith("gif") or path.endswith("jpeg"):
            for t in self.search_history["txt_in_img"]:
                img2txt = OCR([path], lang="tur",search=t)
            img_class_img([path], templates = self.search_history["img_in_img"])
        elif path.endswith("pdf"):
            for t in self.search_history["txt_in_img"]:
                img2txt = OCR([path], lang="tur",search=t, file_type= "pdf")
            img_class_img([path], templates = self.search_history["img_in_img"], file_type = "pdf")
        elif path.endswith("docx") or path.endswith("doc") or path.endswith("odt") or path.endswith("pptx") or path.endswith("ppt") or path.endswith("odp") or path.endswith("xlsx") or path.endswith("xls") or path.endswith("ods"):
            for t in self.search_history["txt_in_txt"]:
                pass
