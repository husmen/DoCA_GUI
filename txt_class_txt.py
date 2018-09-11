""" module for performing OCR """
from open_files import OpenFile
from db_handler import *

class txt_class_txt():
    def __init__(self, files, search = None):
        self.files = files
        self.files_opened = []
        #self.lang = lang
        self.search = search.lower()
        self.text = []
        self.db_server = db_handler()
        for f in self.files:
            self.files_opened.append(OpenFile(f))
        
        for i, f in enumerate(self.files):
            if f.endswith("xlsx") or f.endswith("xls") or f.endswith("ods"):
                self.text.append(str(self.files_opened[i].tables))
            else:
                self.text.append(self.files_opened[i].text)
                     
        if self.search:
            res = self.db_server.query(db_sh,["term"],query_key="_id", query_value="txt_in_txt")
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
                self.db_server.save(db_sh,{'term' : list(res3)}, doc_id = "txt_in_txt")

            for _ in range(0,len(files)):
                self.find(_)
    
    def find(self, f_index):
        print("# searching for {} in {}".format(self.search, self.files[f_index]))

        self.res = self.find_all(self.search,self.text[f_index].lower())
        self.res2 = list(self.res)
        #print(self.res2)

        if len(self.res2) > 0:
            #data = {'img_id' : self.files[_], 'kullanici': 'kubra', "class" :{self.search: True}, 'locations': str(self.res2) }
            #data = {'img_id' : self.files[_], 'kullanici': 'kubra', "class" :{self.search: True}}
            #self.db_server.save(db_ic_t,data,doc_id = self.files[_])

            db_res = self.db_server.query(db_dc,["class"],query_key="_id", query_value=self.files[f_index])
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
                self.db_server.save(db_dc,{'class' : list(db_res3)}, doc_id = self.files[f_index])
            
    def find_all(self, sub, a_str):
        print(type(sub),type(a_str))
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub) # use start += 1 to find overlapping matches
