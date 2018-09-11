""" module for comparing 2 files """

import webbrowser
import couchdb
from db_handler import *
from open_files import OpenFile

import pandas as pd
import diff_match_patch as dmp_module
dmp = dmp_module.diff_match_patch()

differences = {"0": "same", "-1": "paragraph removed", "1": "paragraph added", "2": "paragraph modified"}
differences_2 = {"0": "same", "-1": "removed", "1": "added"}

class CompareFiles():
    def __init__(self, files, file_format = None):
        self.files = files
        self.files_opened = []
        self.file_format = file_format
        self.db_server = db_handler()

        for f in self.files:
            self.files_opened.append(OpenFile(f))

        if file_format == None:
            pass

        elif file_format == "docx":
            for i, f1 in enumerate(self.files_opened):
                for f2 in self.files_opened[i+1:]:
                    print("# Comparing {} and {} #".format(f1.location,f2.location))
                    self.compare_docx(f1,f2)
        elif file_format == "pptx":
            for i, f1 in enumerate(self.files_opened):
                for f2 in self.files_opened[i+1:]:
                    print("# Comparing {} and {} #".format(f1.location,f2.location))
                    self.compare_docx(f1,f2, pptx=True)
        elif file_format == "xlsx":
            for i, f1 in enumerate(self.files_opened):
                for f2 in self.files_opened[i+1:]:
                    print("# Comparing {} and {} #".format(f1.location,f2.location))
                    self.compare_xlsx(f1,f2,mod="diff")
                    #self.compare_xlsx(f1,f2,mod="pd")

        return

    def compare_pptx(self,sld1,sld2):
        pass

    def compare_xlsx(self,tbl1,tbl2,mod):

        if mod == "diff":
            diff = dmp.diff_main(str(tbl1.tables), str(tbl2.tables))
            #print(diff)
            self.diff_html(diff,"table.html")

            row_diff = []
            tmp = []
            for df in diff:
                if "]" in df[1]:
                    tmp2 = df[1].split("]")
                    for i in range(0,len(tmp2)-1):
                        tmp2[i] = tmp2[i] + ']'
                    for t in tmp2:
                        if t:
                            tmp.append((df[0],t))
                            if t[-1] == "]":
                                row_diff.append(tmp)
                                tmp = []        
                else:
                    tmp.append(df)

            data = {'dok_id' : {'dok_1' : tbl1.location,'dok_2' : tbl2.location}, 'kullanici': user_default, 'diff': row_diff}
            self.db_server.save(db_xd, data, doc_id=tbl1.location+"_"+tbl2.location, attachment="html/table.html")

            #for row in row_diff:
            #    print(row)
                    
        elif mod == "pd":
            diff_panel = pd.Panel(dict(df1=tbl1.tables2[0],df2=tbl2.tables2[0]))
            #print("\n### diff_panel ###\n")
            #print(diff_panel)
            #Apply the diff function
            diff_output = diff_panel.apply(self.report_diff, axis=0)

            #print("\n### diff_output ###\n")
            #print(diff_output)


            # Flag all the changes
            diff_output['has_change'] = diff_output.apply(self.has_change, axis=1)

            #Save the changes to excel but only include the columns we care about
            #diff_output[(diff_output.has_change == 'Y')].to_excel('my-diff.xlsx',index=False)

            #print("\n### diff_output - changed ###\n")
            diff_changed = diff_output[(diff_output.has_change == 'Y')]
            #print(diff_changed)
            for row in diff_changed.itertuples():
                #print(row)
                for cell in row:
                    #print(cell)
                    if "--->" in str(cell):
                        #print(row[0], row.index(cell), cell)
                        tmp = cell.split(" ---> ")
                        data = {'dok_id' : {'dok_1' : tbl1.location,'dok_2' : tbl2.location}, 'kullanici': user_default, 'value': {'old': str(tmp[0]), 'new': str(tmp[1]) }, 'cell':{'row': str(row[0]), 'col': str(row.index(cell)) }}
                        #doc_id, doc_rev = db_4.save({'dok_id' : {'dok_1' : tbl1.location,'dok_2' : tbl1.location}, 'kullanici': user_default, 'value': {'old': str(tmp[0]), 'new': str(tmp[1]) }, 'cell':{'row': str(row[0]), 'col': str(row.index(cell)) }})
                        self.db_server.save(db_xd, data, doc_id=tbl1.location+"_"+tbl2.location, attachment="html/table.html")
            #for row in diff_changed.iterrows():
            #    print(row[0])
            #    for col in row:
            #        print(col)

            #for d in diff_output[(diff_output.has_change == 'Y')]:
            #    print(diff_output[d])
        

    def compare_docx(self, txt1, txt2, pptx = False):

        # farkliklar listesi
        diff = dmp.diff_main(txt1.text, txt2.text)
        dmp.diff_cleanupSemantic(diff)
        diff_delta = dmp.diff_toDelta(diff)

        self.diff_html(diff,"diff.html")

        #print("\n## diff_main ##")
        #print(diff)
        #print("\n## diff_toDelta ##")
        #print(diff_delta)

        boyut = len(diff)
        #print("boyut: {}".format(boyut))

        par_diff = []
        tmp = []
        for df in diff:
            if "\n" in df[1]:
                tmp2 = df[1].split("\n")
                for i in range(0,len(tmp2)-1):
                    tmp2[i] = tmp2[i] + '\n'
                for t in tmp2:
                    if t:
                        tmp.append((df[0],t))
                        if t[-1] == "\n":
                            par_diff.append(tmp)
                            tmp = []        
            else:
                tmp.append(df)
        #print("\n## par_diff_main ##")
        #for line in par_diff:
        #    print(line)

        par_status = []
        for line in par_diff:
            tmp = self.get_status(line)
            par_status.append(tmp)

        try:
            par_diff2,par_status2 = self.rearrange(par_diff,par_status)
        except:
            par_diff2 = par_diff
            par_status2 = par_status

        #print("\n## par_diff_2 ##")
        #for line in par_diff2:
        #    print(line)

        actual_p_nbr = []
        p1 = 0
        p2 = 0
        for line in par_diff2:
                tmp = self.get_status(line)
                if tmp == 0 or tmp == 2:
                    p1 = p1 + 1
                    p2 = p2 + 1
                if tmp == -1:
                    p1 = p1 + 1
                if tmp == 1:
                    p2 = p2 + 1
                actual_p_nbr.append([p1,p2])
            #print(par_status2)
            #print(actual_p_nbr)
            #for d in diff:
            #    print("{}\t{}".format(d[0],d[1]))

        diff2 = []
        for line in par_diff2:
                for t in line:
                    diff2.append(t)
        self.diff_html(diff2,"diff2.html")

        data = {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default}
        data2 = {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default}

        for i in range(0,len(par_status2)):
                #print(i)
                if par_status2[i] == -1:
                    data[str(i)] = {'paragraf no': str(actual_p_nbr[i][0]),
                                    'paragraf icerigi': str(txt1.paragraphs[actual_p_nbr[i][0]-1] if actual_p_nbr[i][0]-1 < len(txt1.paragraphs) else "[ERROR] Index Out Of range"),
                                    'farktipi': differences[str(par_status2[i])]}

                if par_status2[i] == 1:
                    data[str(i)] = {'paragraf no': str(actual_p_nbr[i][1]),
                                    'paragraf icerigi': str(txt2.paragraphs[actual_p_nbr[i][1]-1] if actual_p_nbr[i][1]-1 < len(txt2.paragraphs) else "[ERROR] Index Out Of range"),
                                    'farktipi': differences[str(par_status2[i])]}
                    
                if par_status2[i] == 2:
                    #print(actual_p_nbr[i][0]-1)
                    data[str(i)] = {'paragraf no': str(actual_p_nbr[i][0]) + " -> " + str(actual_p_nbr[i][1]),
                                    'old paragraf icerigi': str(txt1.paragraphs[actual_p_nbr[i][0]-1] if actual_p_nbr[i][0]-1 < len(txt1.paragraphs) else "[ERROR] Index Out Of range"),
                                    'new paragraf icerigi': str(txt2.paragraphs[actual_p_nbr[i][1]-1] if actual_p_nbr[i][1]-1 < len(txt2.paragraphs) else "[ERROR] Index Out Of range"),
                                    'farktipi': differences[str(par_status2[i])]}
                    
                    
                    actual_k_nbr = []
                    kelime_1 = 0
                    kelime_2 = 0
                    kar_1 = 0
                    kar_2 = 0
                    for di in par_diff2[i]:
                        kelime_len = len(di[1].split(" "))
                        kar_len = len(di[1])
                        if di[0] == 0:
                            kelime_1 = kelime_1 + kelime_len
                            kelime_2 = kelime_2 + kelime_len
                            kar_1 = kar_1 + kar_len
                            kar_2 = kar_2 + kar_len
                        if di[0] == -1:
                            tmp_kelime = kelime_1
                            kelime_1 = kelime_1 + kelime_len
                            tmp_kar = kar_1
                            kar_1 = kar_1 + kar_len
                            #print("{} kelime {}'dan itibaren silinmis: {}".format(kelime_len,tmp_kelime, di[1]))
                            #print("{} karakter {}'dan itibaren silinmis".format(kar_len,tmp_kar))
                            data2[str(i)] = {'paragraf no': str(actual_p_nbr[i][0]),
                                    'fark': str(di[1]), 'farktipi': differences_2[str(di[0])], 'baslangis kelime no': str(tmp_kelime), 'kelime sayisi': str(kelime_len), 'baslangis kar no': str(tmp_kar), 'kar sayisi': str(kar_len) }
                            
                            #doc_id, doc_rev = db_2.save(
                            #        {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'paragraf no': str(actual_p_nbr[i][0]),
                            #        'fark': str(di[1]), 'farktipi': differences_2[str(di[0])], 'baslangis kelime no': str(tmp_kelime), 'kelime sayisi': str(kelime_len), 'baslangis kar no': str(tmp_kar), 'kar sayisi': str(kar_len) })
                        if di[0] == 1:
                            tmp_kelime = kelime_2
                            tmp_kar = kar_2
                            kelime_2 = kelime_2 + kelime_len
                            kar_2 = kar_2 + len(di[1])
                            #print("{} kelime {}'dan itibaren eklendi: {}".format(kelime_len,tmp_kelime, di[1]))
                            #print("{} karakter {}'dan itibaren eklendi".format(kar_len,tmp_kar))
                        actual_k_nbr.append([kar_1,kar_2])

        if pptx:
            self.db_server.save(db_pd, data2, doc_id=txt1.location+"_"+txt2.location, attachment="html/diff.html")        
        
        else:
            self.db_server.save(db_dd_p, data, doc_id=txt1.location+"_"+txt2.location, attachment="html/diff.html")
            self.db_server.save(db_dd_w, data2, doc_id=txt1.location+"_"+txt2.location)        

        if txt1.tables and txt2.tables:
                #print("tables present")
                for t1 in txt1.tables:
                    for t2 in txt2.tables:
                        if t1 != t2:
                            data = {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'fark': str(t), 'farktipi': "Tablo değiştirme" }
                            self.db_server.save(db_dd_t, data)      
                            #print("table changed")
                            #self.compare_xlsx(t1,t2,mod='emb')
                            #TODO compare all tables
        elif txt1.tables:
                #print("table removed")
                data = {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'fark': str(t), 'farktipi': "Tablo silme" }
                self.db_server.save(db_dd_t, data)        
                #doc_id, doc_rev = db_3.save({'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'fark': str(t), 'farktipi': "Tablo silme" })
        elif txt2.tables:
                for t in txt2.tables:
                    #print("table added")
                    data = {'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'fark': str(t), 'farktipi': "Tablo eklemek" }
                    self.db_server.save(db_dd_t, data)
                    #doc_id, doc_rev = db_3.save({'dok_id' : {'dok_1' : txt1.location,'dok_2' : txt2.location}, 'kullanici': user_default, 'fark': str(t), 'farktipi': "Tablo eklemek" })



    def diff_html(self, diff,file):
        tmp = dmp.diff_prettyHtml(diff)
        if not os.path.exists("html"):
            os.makedirs("html")
        f = open("html/" + file, 'w')

        message = """<meta http-equiv="content-type" content="text/html;charset= utf-8 " />
    <html><head></head><body>"""
        f.write(message)

        f.write(tmp)
        message = """</body></html>"""
        f.write(message)
        f.close()
        #webbrowser.open_new_tab("html/" + file)

    def get_status(self, par):
            adds = 0
            removes = 0
            sames = 0
            for item in par:
                if(item[0] == 0):
                    sames = sames + 1
                if(item[0] == 1):
                    adds = adds + 1
                if(item[0] == -1):
                    removes = removes + 1

            if(removes and sames == 0 and adds == 0):
                #print("paragraph removed")
                return -1
            elif(adds and sames == 0 and removes == 0):
                #print("paragraph added")
                return 1
            elif(sames and adds == 0 and removes == 0):
                #print("paragraph stayed the same")
                return 0
            elif(adds or removes):
                #print("paragraph changed")
                return 2


    def rearrange(self, changes, status):
        for i in range(0,len(status)):
            tmp = []
            p = False
            if status[i] == 2 and changes[i][-1][0] == -1:
                tmp = i
                #print("# MUST REARRANGE")
                for j in range(i+1,len(status)):
                    if status[i] == 2 and changes[j][-1][0] != -1:
                        changes[tmp].append(changes[j][-1])
                        changes[tmp][-2] = (changes[tmp][-2][0],changes[tmp][-2][1][:-1])
                        del changes[j][-1]
                        tmp_t = (changes[j][-1][0],changes[j][-1][1]+'\n')
                        del changes[j][-1]
                        changes[j].append(tmp_t)
                        status[j] = self.get_status(changes[j])
                        for k in range(j+1,len(status)):
                            if len(changes[k][-1][1]) <= 2:
                                changes[k][-2] = (changes[k][-2][0], changes[k][-2][1] + changes[k][-1][1])
                                del changes[k][-1]
                                break
                        break

        return changes, status

    # Define the diff function to show the changes in each field
    def report_diff(self,x):
        return x[0] if x[0] == x[1] else '{} ---> {}'.format(*x)

    # We want to be able to easily tell which rows have changes
    def has_change(self, row):
        if "--->" in row.to_string():
            return "Y"
        else:
            return "N"