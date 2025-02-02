# This is an edited version of https://github.com/minhptx/iswc-2016-semantic-labeling, which was edited to use it as a baseline for Tab2KG (https://github.com/sgottsch/Tab2KG).

import os

from gensim.models import Word2Vec

from pyspark import SparkContext, SQLContext

sc = SparkContext()
sql_context = SQLContext(sc)

root_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), '..'))
data_dir = os.path.join(root_dir, "data/datasets")
train_model_dir = os.path.join(root_dir, "data/train_models")

# word2vec = Word2Vec.load_word2vec_format(os.path.join("/Users/minhpham/tools/", 'GoogleNews-vectors-negative300.bin'), binary=True)

file_write = open('debug.txt', 'w')

logger = sc._jvm.org.apache.log4j
logger.LogManager.getLogger("org").setLevel(logger.Level.FATAL)
logger.LogManager.getLogger("akka").setLevel(logger.Level.FATAL)
