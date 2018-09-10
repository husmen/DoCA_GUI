""" """

import json
import gensim
import couchdb
import numpy as np
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from os import listdir
from os.path import isfile, join
from db_handler import *
from open_files import OpenFile
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage, ward
#from sklearn.datasets.samples_generator import make_blobs


tokenizer = RegexpTokenizer(r'\w+')
stopword_set = set(stopwords.words('turkish'))
#This function does all cleaning of data using two objects above
def nlp_clean(data):
            new_data = []
            for d in data:
                new_str = d.lower()
                dlist = tokenizer.tokenize(new_str)
                dlist = list(set(dlist).difference(stopword_set))
                new_data.append(dlist)
            return new_data

class LabeledLineSentence(object):

    def __init__(self, doc_list, labels_list):

        self.labels_list = labels_list
        self.doc_list = doc_list

    def __iter__(self):

        for idx, doc in enumerate(self.doc_list):
              #yield gensim.models.doc2vec.LabeledSentence(doc, [self.labels_list[idx]])
            yield gensim.models.doc2vec.TaggedDocument(doc, [self.labels_list[idx]])

class SimilarityRatio():
    def __init__(self, files, file_format, method= None):

        self.files = files
        self.files_opened = []
        for f in self.files:
            self.files_opened.append(OpenFile(f))
        self.docLabels = []
        self.db_server = db_handler()
        for doc in self.files_opened:
            self.docLabels.append(doc.location)

        #create a list data that stores the content of all text files in order of their names in docLabels
        data = []
        if file_format == "docx" or file_format == "pptx":
            for doc in self.files_opened:
                #data.append(open(doc, encoding='latin-1').read())
                db = db_ds
                data.append(doc.text)
        elif file_format == "xlsx":  
            for doc in self.files_opened:
                #data.append(open(doc, encoding='latin-1').read())
                db = db_xs
                data.append(json.dumps(doc.tables))

        data = nlp_clean(data)
        if method == "fuzzywuzzy":
            for i, f1 in enumerate(data):
                for f2 in data[i+1:]:
                    #print(self.docLabels[i],self.docLabels[i+1])
                    x= fuzz.ratio(f1,f2)
                    y= fuzz.partial_ratio(f1,f2)
                    #print(x,y)
                    db_data = {'dok_id' : {'dok_1' : self.docLabels[i],'dok_2' : self.docLabels[i+1]}, 'kullanici': user_default, 'overall similarity ratio': x, 'partial similarity ratio': y}
                    self.db_server.save(db, db_data,doc_id=self.docLabels[i]+"_"+self.docLabels[i+1])
        else:
            #iterator returned over all documents
            it = LabeledLineSentence(data, self.docLabels)
            model = gensim.models.Doc2Vec(vector_size=300, min_count=0, alpha=0.025, min_alpha=0.025)
            model.build_vocab(it)
            #training of model
            for epoch in range(100):
                #print ('iteration '+str(epoch+1))
                model.train(it, total_examples=model.corpus_count, epochs=3)
                model.alpha -= 0.002
                model.min_alpha = model.alpha

            model.save('doc2vec.model')
            print ("model saved")

            #loading the model
            d2v_model = gensim.models.doc2vec.Doc2Vec.load('doc2vec.model')

            #start testing
            X = []
            # printing the vector of documents in docLabels
            for i, _ in enumerate(self.docLabels):
                docvec = d2v_model.docvecs[i]
                #print(docvec)
                X.append(docvec)
            X = np.array(X)
            #docvec = d2v_model.docvecs[0]
            #print (docvec)
            #docvec = d2v_model.docvecs[1]
            #print (docvec)

            #to get most similar document with similarity scores using document-index
            similar_doc = d2v_model.docvecs.most_similar(0) 
            print(similar_doc)
            
            for doc in similar_doc:
                db_data = {'dok_id' : {'dok_1' : self.docLabels[0],'dok_2' : doc[0]}, 'kullanici': user_default, 'benzerlik orani': str(doc[1])}
                self.db_server.save(db, db_data)
            #similar_doc = d2v_model.docvecs.most_similar(1) 
            #print(similar_doc)  

            #printing the vector of the file using its name
            #docvec = d2v_model.docvecs['shakespeare-hamlet.txt'] #if string tag used in training
            #print(docvec)
            #to get most similar document with similarity scores using document- name
            #sims = d2v_model.docvecs.most_similar('shakespeare-hamlet.txt')
            #print(sims)

            # #############################################################################
            # Compute Affinity 
            # = d2v_model.docvecs
            # print(d2v_model.docvecs)
            # print(d2v_model[d2v_model.wv.vocab])
            # X = d2v_model[d2v_model.wv.vocab]
            # print("### docvecs")
            # print(d2v_model.docvecs[0])
            # print("### vectors")
            # print(d2v_model.wv.vectors)
            # X = d2v_model.wv.vectors

            

            af = AffinityPropagation(preference=-50).fit(X)
            cluster_centers_indices = af.cluster_centers_indices_
            labels = af.labels_
            labels2 = []
            for i, lb in enumerate(labels):
                labels2.append(self.files[i].split('/')[-1])
            print("labels: {}".format(labels))
            print("labels2: {}".format(labels2))
            n_clusters_ = len(cluster_centers_indices)
            print("number of clusters: {}".format(n_clusters_))
            dic = {i: np.where(labels == i)[0] for i in range(n_clusters_)}
            print(dic)

            for key, value in dic.items():
                print(key)
                for e in value:
                    print("{} : {}".format(e,self.files[e].split('/')[-1]))

            # print('Estimated number of clusters: %d' % n_clusters_)
            # print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
            # print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
            # print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
            # print("Adjusted Rand Index: %0.3f"
            #     % metrics.adjusted_rand_score(labels_true, labels))
            # print("Adjusted Mutual Information: %0.3f"
            #     % metrics.adjusted_mutual_info_score(labels_true, labels))
            print("Silhouette Coefficient: %0.3f"
                % metrics.silhouette_score(X, labels, metric='sqeuclidean'))

            # #############################################################################
            # Plot result
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from itertools import cycle

            # plt.close('all')
            # plt.figure(1)
            # plt.clf()

            colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
            for k, col in zip(range(n_clusters_), colors):
                class_members = labels == k
                cluster_center = X[cluster_centers_indices[k]]
                plt.plot(X[class_members, 0], X[class_members, 1], col + '.')
                plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                        markeredgecolor='k', markersize=5)
                for x in X[class_members]:
                    plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)

            plt.title('Estimated number of clusters: %d' % n_clusters_)
            plt.show()


            # ############################################################################
            # second plot
            # plt.close('all')
            # fig = plt.figure()
            # plt.clf()
            # ax = fig.add_subplot(111, projection='3d')

            # for k, col in zip(range(n_clusters_), colors):
            #     class_members = labels == k
            #     cluster_center = X[cluster_centers_indices[k]]
            #     ax.plot(X[class_members, 0], X[class_members, 1], X[class_members, 1], col + '.')
            #     ax.plot(cluster_center[0], cluster_center[1], cluster_center[2], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
            #     for x in X[class_members]:
            #         ax.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], [cluster_center[2], x[2]], c=col, marker='.')

            # plt.title('Estimated number of clusters: %d' % n_clusters_)
            # plt.show()

            # ####################
            # 3rd plot

            plt.close('all')
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            pca = PCA(n_components=3)
            reduced = pca.fit_transform(X)

            # We need a 3 x 944 array, not 944 by 3 (all X coordinates in one list)
            #t = reduced.transpose()
            X = reduced


            for k, col in zip(range(n_clusters_), colors):
                class_members = labels == k
                cluster_center = X[cluster_centers_indices[k]]
                plt.plot(X[class_members, 0], X[class_members, 1], X[class_members, 2], col + '.')
                #plt.plot(cluster_center[0], cluster_center[1], cluster_center[2], 'o', markerfacecolor=col)
                ax.scatter(cluster_center[0], cluster_center[1], cluster_center[2], 'o', c=col, marker='o', s=50)
                for x in X[class_members]:
                    plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], [cluster_center[2], x[2]], col)

            plt.title('Estimated number of clusters: %d' % n_clusters_)
            plt.show()


            
            # #########################
            # hierarchical

            linkage_matrix = []
            #linkage_matrix.append(linkage(X, method='single', metric='euclidean'))
            linkage_matrix.append(linkage(X, method='average', metric='euclidean'))
            #linkage_matrix.append(linkage(X, method='complete', metric='euclidean'))
            #linkage_matrix.append(linkage(X, method='ward', metric='euclidean'))

            #linkage_matrix.append(linkage(X, method='single', metric='seuclidean'))
            linkage_matrix.append(linkage(X, method='average', metric='seuclidean'))
            #linkage_matrix.append(linkage(X, method='complete', metric='seuclidean'))

            for n, l in enumerate(linkage_matrix): 
                # calculate full dendrogram
                plt.figure(figsize=(25, 10))
                plt.title('Hierarchical Clustering Dendrogram')
                plt.ylabel('word')
                plt.xlabel('distance')

                dendrogram(
                    l,
                    leaf_rotation=0.,  # rotates the x axis labels
                    leaf_font_size=16.,  # font size for the x axis labels
                    orientation='left',
                    leaf_label_func=lambda v: str(self.files[v].split('/')[-1])
                )
                plt.savefig('clusters_{}.png'.format(n), dpi=200) #save figure as ward_clusters
                plt.show()

            #linkage_matrix2 = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances