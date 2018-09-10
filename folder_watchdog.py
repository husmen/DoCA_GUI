import os
import hashlib
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from anytree import Node, RenderTree
from db_handler import *
from ocr import OCR
from auto_classifier import AUTO_CLASSIFIER

db_server = db_handler()
file_hashes = []
folder_hashes = []

def list_files_hashes():
    pass
    
def save_file(name, path):
    st = os.stat(path)
    try:
        import pwd # not available on all platforms
        userinfo = pwd.getpwuid(st.st_uid)
    except (ImportError, KeyError):
        print("failed to get the owner name for", f)
    else:
        userinfo = "[ERROR] UNKOWN"
                #print("file {}, owned by: {}".format(f, userinfo[0]))
    atime = time.ctime(st.st_atime)
    mtime = time.ctime(st.st_mtime)
    ctime = time.ctime(st.st_ctime)
    hash_md5 = GetHash(path, algo="md5")
    data = {"path" : path, "name": name, "owner": userinfo, "Last access time": atime , "Last modification time": mtime, "Last information change time": ctime, "hash_md5": hash_md5}

    if path.endswith("mp4") or path.endswith("avi") or path.endswith("mpg") or path.endswith("mp3") or path.endswith("wav"):
        db_server.save(db_f,data, doc_id=path)
    else:
        db_server.save(db_f,data , doc_id=path, attachment=path)

def list_files(startpath):
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
            full_path = os.path.join(root, f)
            abs_path = os.path.abspath(full_path)
            st = os.stat(full_path)
            try:
                import pwd # not available on all platforms
                userinfo = pwd.getpwuid(st.st_uid)
            except (ImportError, KeyError):
                print("failed to get the owner name for", f)
            else:
                userinfo = "[ERROR] UNKOWN"
                #print("file {}, owned by: {}".format(f, userinfo[0]))
            #atime = time.ctime(st.st_atime)
            #mtime = time.ctime(st.st_mtime)
            #ctime = time.ctime(st.st_ctime)
            save_file(f,abs_path)
            #file_hashes.append(hash_sha256)
            #db_server.save(db_f,{"path" : abs_path, "name": f, "hash_sha256": hash_sha256, "hash_md5": hash_md5},doc_id=abs_path)
            #print("Last access time: {}\nLast modification time: {}\nLast information change time: {}\nHash: {}\n".format(atime, mtime, ctime, hash_tmp))
            #tmp = Node((f, None, st), parent = levels[level])
            tmp = Node(f, parent = levels[level])
            #print('{}{}'.format(subindent, f))

    for pre, fill, node in RenderTree(folder_tree):
        #if len(node.name) == 2:
        if isinstance(node.name, str):
            print("%s%s" % (pre, node.name))
            
        else:
            print("%s%s : %s" % (pre, node.name[0], node.name[2][0]))
        #print(node)

def GetHash(path, algo = "md5", verbose=0):
    blocksize = 64*1024
    if algo == "sha256":
        SHAhash = hashlib.sha256()
    elif algo == "md5":
        SHAhash = hashlib.md5()
    else:
        return 0
    if not os.path.exists(path):
        return -1
    with open(path, 'rb') as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            SHAhash.update(data)
    return SHAhash.hexdigest()

def GetHashofDirs(directory, verbose=0):
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


class customEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        super(customEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)
        if event.is_directory:
            #print(GetHashofDirs(event.src_path))
            pass
        else: 
            #print(GetHash(event.src_path))
            save_file(os.path.basename(event.dest_path),os.path.abspath(event.dest_path))

    def on_created(self, event):
        super(customEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)
        if event.is_directory:
            #print(GetHashofDirs(event.src_path))
            pass
        elif os.path.basename(event.src_path)[0] != ".": 

            print("running auto classification")
            
            classifier = AUTO_CLASSIFIER()
            classifier.classify(os.path.abspath(event.src_path))

            print("adding to db")

            hash_tmp = GetHash(event.src_path, algo="sha256")
            print(hash_tmp)
            res = db_server.query(db_f,["_id"], query_key="hash_sha256", query_value=hash_tmp)
            res2 = []
            for row in res:
                res2.append(row.key[0])
            if os.path.abspath(event.src_path) in res2:
                print("previously deleted file recovered!")
            save_file(os.path.basename(event.src_path),os.path.abspath(event.src_path))
            

    def on_deleted(self, event):
        super(customEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)
        if event.is_directory:
            #print(GetHashofDirs(event.src_path))
            pass
        else: 
            print(GetHash(event.src_path))
            

    def on_modified(self, event):
        super(customEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)
        if event.is_directory:
            #print(GetHashofDirs(event.src_path))
            pass
        else: 
            print(GetHash(event.src_path))
            save_file(os.path.basename(event.src_path),os.path.abspath(event.src_path))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '../dosyalar_ornek'
    list_files(path)
    event_handler = customEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
