from settings import MONGODB

import jieba
from gensim import corpora
from gensim import models
from gensim import similarities

l1 = content_list = list(MONGODB.content.find({}))

all_doc_list = []
for doc in l1:
    doc_list = list(jieba.cut_for_search(doc.get("title")))
    all_doc_list.append(doc_list)
dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
lsi = models.LsiModel(corpus)  # 向量
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


def my_sim(a):
    doc_test_list = list(jieba.cut_for_search(a))
    doc_test_vec = dictionary.doc2bow(doc_test_list)  # doc_test_vec "你,今年,多,大,了" 1,6,8,5
    sim = index[lsi[doc_test_vec]]
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    print(cc[0][1])
    if cc[0][1] >= 0.8:
        text = l1[cc[0][0]]
        return text
