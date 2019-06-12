import jieba
from gensim import corpora
from gensim import models
from gensim import similarities

lst = ['你今年几岁了', '你今年多大了', '祖国祖国我们爱你']  # 语料库,我们说的话要到这里面匹配

all_doc_list = []
for doc in lst:
    doc_list = list(jieba.cut_for_search(doc))
    all_doc_list.append(doc_list)

dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
# print('词袋有什么==>', dictionary)
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]  # doc2bow词袋里的词组成[(0,1),(2,6)]形式的
# print(corpus)

# 将你说的话先做成分词列表,然后做成语料库
word = '祖国我爱你'
doc_test_list = (list(jieba.cut_for_search(word)))
doc_test_vec = dictionary.doc2bow(doc_test_list)
# print(doc_test_vec)

# 将语料库使用lsi模型训练
lsi = models.LsiModel(corpus)
# print('corpus的训练结果>>>', lsi[corpus])

index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))
# print(index, type(index))
# 将 语料库doc_test_vec 在 语料库corpus的训练结果 中的 向量表示 与 语料库corpus的 向量表示 做矩阵相似度计算
sim = index[lsi[doc_test_vec]]
# print("sim", sim, type(sim))

# 对下标和相似度结果进行一个排序,拿出相似度最高的结果
res = sorted(enumerate(sim), key=lambda item: -item[1])
print(res)
text = lst[res[0][0]]  # 找到lst中与数据最匹配的索引位置

print(word, text)
