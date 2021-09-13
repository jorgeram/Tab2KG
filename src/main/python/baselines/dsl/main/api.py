#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is an edited version of https://github.com/minhptx/iswc-2016-semantic-labeling, which was edited to use it as a baseline for Tab2KG (https://github.com/sgottsch/Tab2KG).

"""API for semantic labeling, a dataset is a set of sources"""

import logging
import os
import sys

from elasticsearch import Elasticsearch
from main.logutil import get_logger
from main.semantic_labeler import SemanticLabeler
import ujson
from lib.utils import not_allowed_chars


def is_indexed(dataset):
    """Check if this dataset is indexes in ElasticSearch/Spark

    :param dataset: str
    :return: bool
    """
    es = Elasticsearch()
    
    logger.info("Is indexed: " + dataset)
    is_indexed = es.indices.exists(dataset.lower())
    
    logger.info(is_indexed)
    
    return is_indexed


def get_pairs(filepath):
    pairs = []
    file = open(filepath, 'r') 
    lines = file.read().splitlines()
    
    for line in lines:
        pairs.append(line.split(" "))
    return pairs


def semantic_labeling(train_dataset, test_dataset, pairs_file, reuse_rf_model=True):
    """Doing semantic labeling, train on train_dataset, and test on test_dataset.

    train_dataset2 is optionally provided in case train_dataset, and test_dataset doesn't have overlapping semantic types
    For example, given that train_dataset is soccer domains, and test_dataset is weather domains; the system isn't able
    to recognize semantic types of test_dataset because of no overlapping. We need to provide another train_dataset2, which
    has semantic types of weather domains; so that the system is able to make prediction.

    Train_dataset2 is default to train_dataset. (train_dataset is use to train RandomForest)

    :param train_dataset: str
    :param test_dataset: str
    :param train_dataset2: Optional[str]
    :param evaluate_train_set: bool
    :param reuse_rf_model: bool
    :return:
    """
    logger = get_logger("semantic-labeling-api", format_str='>>>>>> %(asctime)s - %(levelname)s:%(name)s:%(module)s:%(lineno)d:   %(message)s')

    pairs = get_pairs(pairs_file)

#     if train_dataset2 is None:
#         train_dataset2 = train_dataset

    if(not reuse_rf_model):
        datasets = [train_dataset]
    else:
        datasets = []

    for pair in pairs:
        if(not pair[1] in datasets):
            datasets.append(pair[1])
        if(not pair[2] in datasets):
            datasets.append(pair[2])
    
#     else:
#        datasets = [train_dataset, test_dataset, train_dataset2]

    logger.info("Datasets: ", datasets)

    semantic_labeler = SemanticLabeler()
    # read data into memory
    logger.info("Read data into memory")
    semantic_labeler.read_data_sources(list(datasets))
    # index datasets that haven't been indexed before

    not_indexed_datasets = list({dataset for dataset in datasets if not is_indexed(dataset)})
    if len(not_indexed_datasets) > 0:
        logger.info("Index not-indexed datasets: %s" % ",".join(not_indexed_datasets))
        semantic_labeler.train_semantic_types(not_indexed_datasets)

    # remove existing file if not reuse previous random forest model
    if not reuse_rf_model and os.path.exists("model/lr.pkl"):
        os.remove("model/lr.pkl")

    # train the model
    logger.info("Train randomforest... with args ([1], [%s]", train_dataset)
    semantic_labeler.train_random_forest([1], [train_dataset])
    
    for pair in pairs:
        print("Pair: " + pair[1] + ", " + pair[2] + ".")
        # generate semantic typing
        logger.info("Generate semantic typing using: trainset: %s, for testset: %s", pair[1], pair[2])
        result = semantic_labeler.test_semantic_types_from_2_sets(pair[1], pair[2])
        # result = semantic_labeler.test_semantic_types_from_2_sets(train_dataset2, test_dataset)
    
        if not os.path.exists("output"):
            os.mkdir("output")
        file_name = "output/" + test_dataset + "_" + pair[0] + "_result.json"
        with open(file_name, "w") as f:
            ujson.dump(result, f)

#     if evaluate_train_set:
#         logger.info("Generate semantic typing for trainset")
#         result = semantic_labeler.test_semantic_types_from_2_sets(train_dataset2, train_dataset2)
#         with open("output/%s_result.json" % train_dataset2, "w") as f:
#             ujson.dump(result, f)

    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser('Semantic labeling API')
    parser.add_argument('--train_dataset', type=str, help='trainset', required=True)
    parser.add_argument('--test_dataset', type=str, help='testset', required=True)
    # parser.add_argument('--train_dataset2', type=str, default=None, help='default to train_dataset')
    # parser.add_argument('--evaluate_train_set', type=lambda x: x.lower() == "true", default=False, help='default False')
    parser.add_argument('--reuse_rf_model', type=lambda x: x.lower() == "true", default=True, help='default True')
    parser.add_argument('--pairs_file', type=str, help='pairs file', required=True)
    # parser.add_argument('--less', type=str, help='less', required=True)

    args = parser.parse_args()

#     if args.train_dataset2 is None:
#         args.train_dataset2 = args.train_dataset

    logger = get_logger("api-starter", format_str='>>>>>> %(asctime)s - %(levelname)s:%(name)s:%(module)s:%(lineno)d:   %(message)s')
    logger.info("Calling semantic labeling API with args: %s" % args)
    semantic_labeling(args.train_dataset, args.test_dataset, args.pairs_file, args.reuse_rf_model)
