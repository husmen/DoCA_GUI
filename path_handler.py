import os
import hashlib
import time
import couchdb
from anytree import Node, RenderTree
from db_handler import *

#user = "husmen"
#password = "husmen"
#couchserver = couchdb.Server("http://%s:%s@localhost:5984/" % (user, password))

class path_handler():
    def __init__(self, path, db_name = None, file_type = None, key=None, proc="path2list2"):
        self.path = path
        self.key = key
        self.file_type = file_type
        self.db_name = db_name
        self.db_server = db_handler()

        #self.files = []
        self.docx = []
        self.xlsx = []
        self.pptx = []
        self.pdf = []
        self.img = []
        self.vid = []
        self.audio = []

        if proc == "path2list2":
            self.path2list2(self.path)
        elif proc == "list_files":
            self.list_files(self.path, self.db_name, self.key)
        return

    def path2list2(self, path):
        for root, dirs, files in os.walk(self.path):
            for f in files:
                #self.files.append(os.path.join(root, f))
                if f.endswith("docx") or f.endswith("doc") or f.endswith("odt"):
                    self.docx.append(os.path.join(root, f))
                elif f.endswith("xlsx") or f.endswith("xls") or f.endswith("ods"):
                    self.xlsx.append(os.path.join(root, f))
                elif f.endswith("pptx") or f.endswith("ppt") or f.endswith("odp"):
                    self.pptx.append(os.path.join(root, f))
                elif f.endswith("pdf"):
                    self.pdf.append(os.path.join(root, f))
                elif f.endswith("png") or f.endswith("jpg") or f.endswith("jpeg") or f.endswith("gif"):
                    self.img.append(os.path.join(root, f))
                elif f.endswith("mp4") or f.endswith("mpg") or f.endswith("avi"):
                    self.vid.append(os.path.join(root, f))
                elif f.endswith("mp3") or f.endswith("wav"):
                    self.audio.append(os.path.join(root, f))

    def list_files(self, startpath, db_name, key):
        #tree_root = Node(startpath)
        folder_tree = Node(startpath)
        levels = []
        for root, dirs, files in os.walk(startpath):
            levels.append(None)
            level = root.replace(startpath, '').count(os.sep)
            if level == 0:
                levels[level] = folder_tree
            else:
                levels[level] = Node(os.path.basename(root), parent=levels[level-1])
            #indent = ' ' * 4 * (level)
            #print('{}{}/'.format(indent, os.path.basename(root)))
            #subindent = ' ' * 4 * (level + 1)
            for f in files:
                st = os.stat(os.path.join(root, f))
                try:
                    import pwd # not available on all platforms
                    userinfo = pwd.getpwuid(st.st_uid)
                except (ImportError, KeyError):
                    print("failed to get the owner name for", f)
                else:
                    #print("file {}, owned by: {}".format(f, userinfo[0]))
                    pass
                #atime = time.ctime(st.st_atime)
                #mtime = time.ctime(st.st_mtime)
                #ctime = time.ctime(st.st_ctime)
                hash_tmp = self.GetHash(os.path.join(root, f))
                #file_hashes.append(hash_tmp)
                #print("Last access time: {}\nLast modification time: {}\nLast information change time: {}\nHash: {}\n".format(atime, mtime, ctime, hash_tmp))
                #tmp = Node((f, None, st), parent = levels[level])
                tmp = Node(f, parent = levels[level])
                #print('{}{}'.format(subindent, f))
        if key:
            res = self.db_server.query(db_name, ['name', 'path'], query_key="class", query_value=key)
            #res = db3.query(map_fun)
            res2 = []
            for row in res:      
                #print(row.key)
                res2.append(row.key[0])
            #print(res)
            #print(res2)

            for pre, fill, node in RenderTree(folder_tree):
                #if len(node.name) == 2:
                if isinstance(node.name, str):
                    if ("." in node.name and node.name in res2) or "." not in node.name:
                        print("%s%s" % (pre, node.name))
                        
                elif node.name[0] in res2:
                    print("%s%s : %s" % (pre, node.name[0], node.name[2][0]))
                #print(node)
        else:
            for pre, fill, node in RenderTree(folder_tree):
                if isinstance(node.name, str):
                    print("%s%s" % (pre, node.name))
                    
                else:
                    print("%s%s : %s" % (pre, node.name[0], node.name[2][0]))

                

    def GetHash(self, path, verbose=0):
        blocksize = 64*1024
        SHAhash = hashlib.sha256()
        if not os.path.exists(path):
            return -1
        with open(path, 'rb') as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                SHAhash.update(data)
        return SHAhash.hexdigest()

    def GetHashofDirs(self, directory, verbose=0):
        #import hashlib, os
        blocksize = 64*1024
        #SHAhash = hashlib.md5()
        SHAhash = hashlib.sha256()
        if not os.path.exists(directory):
            return -1

        try:
            for root, dirs, files in os.walk(directory):
                for names in files:
                    if verbose == 1:
                        print('Hashing', names)
                    filepath = os.path.join(root, names)
                    with open(filepath, 'rb') as fp:
                        while True:
                            data = fp.read(blocksize)
                            if not data:
                                break
                            SHAhash.update(data)

        except:
            import traceback
            # Print the stack traceback
            traceback.print_exc()
            return -2

        return SHAhash.hexdigest()