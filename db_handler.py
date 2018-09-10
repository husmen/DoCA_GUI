import os
import couchdb

#veritabani baglantisi
user_default = "husmen"
pw_default = "husmen"
server_default = "http://localhost:5984/"

db_dd_p = "docx_diff_par"
db_dd_w = "docx_diff_word"
db_dd_t = "docx_diff_table"

db_xd = "xlsx_diff"
db_pd = "pptx_diff"

db_ds = "docx_similarity"
db_xs = "xlsx_similarity"
db_ps = "pptx_similarity"

db_dc = "doc_class"
db_ac = "audio_class"
db_vc = "vid_class"

db_ic_t = "img_class_txt"
db_ic_i = "img_class_img"

db_sh = "search_history"
db_sh_img = "search_history_img"
db_ocr = "ocr_history"
db_f = "files"
db_names = [db_ac, db_dd_p, db_dd_w, db_dd_t, db_xd, db_pd, db_ps, db_ds, db_xs, db_dc, db_ic_t, db_ic_i, db_vc, db_sh]

class db_handler():
    """"""
    def __init__(self, user = user_default, pw = pw_default, server = server_default):
        if "http://" in server:
            tmp = server.split("http://")
        else:
            print("wrong server address")
            return
        self.couchserver = couchdb.Server("http://{}:{}@{}".format(user,pw,tmp[1]))
        return

    def save(self, db_name, data, doc_id = None, attachment = None):
        if db_name not in self.couchserver:
            db = self.couchserver.create(db_name)
        else:
            db = self.couchserver[db_name]
        if not doc_id:
            doc_id, doc_rev = db.save(data)
        else:
            try:
                db[doc_id] = data
            except:
                doc = db[doc_id]
                for k in data.keys():
                    doc[k] = data[k]
                db[doc_id] = doc
        if attachment:
            with open(attachment, "rb") as f:
                att = f.read()
            ver = 0
            while(True):
                tmp_name = "{}.{}".format(os.path.basename(attachment),ver)
                check = db.get_attachment(db[doc_id], tmp_name , default=None)
                if check:
                    ver += 1
                else:
                    db.put_attachment(db[doc_id], att, filename = tmp_name)
                    break

    def exists(self, db_name, doc_id):
        pass

    def query(self, db_name, keys, order = None, query_key = None, query_value = None):
        self.keys = "["
        for key in keys:
            self.keys = self.keys + "doc." +key + ","
        self.keys = self.keys[:-1]+"]"

        if query_key and query_value:  
            map_fun = '''function(doc) {{
                    if(doc.{} == '{}')
                        emit({}{});
                }}'''.format(query_key, query_value, self.keys, ', doc.'+order if order else '' )
        elif query_key and not query_value:
            print("missing query value")
        elif query_value and not query_key:
            print("missing query key")
        else:
            map_fun = '''function(doc) {{
                    emit({}{});
                }}'''.format(self.keys, ', doc.'+order if order else '' )

        #print(map_fun)
        try:
            db = self.couchserver[db_name]
        except:
            return []
        else:
            res = db.query(map_fun)
            return res

    def delete_all(self):
        for db in self.couchserver:
            if db[0] != "_":
                print("# deleting db: {}".format(db))
                del self.couchserver[db]
            
        

