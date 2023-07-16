#!/usr/bin/env python3

# execute in tira with: 
# PIPELINE_NAME=bm25_chatgpt_args.diff DEBATER_TOKEN=<the-token> EXT_INPUT_FILE=$inputRun/run.txt TIRA_INPUT_DIRECTORY=$inputDataset TIRA_OUTPUT_DIRECTORY=$outputDir ./main.py

import os
import pandas as pd
from tira_utils import get_input_directory_and_output_directory, normalize_run
from pathlib import Path
import pyterrier as pt

from neville.datasets import ToucheDataset
from neville.stance import apply_stance
from neville.pipelines import get_pipelines

import bundle_data

import logging
logging.basicConfig(level=logging.INFO)


def eval_queries(pipeline_pro, pipeline_con, queries, head=10):
    return pd.concat([(pipeline_pro % head)(queries), (pipeline_con % head)(queries)]).rename(columns={'stance': 'Q0'})

if __name__ == '__main__':

    PYTERRIER_INDEX = '/cache/pyterrier-index'
    CLIP_INDEX = '/cache/clip-index.npy'

    DEBATER_TOKEN = os.environ.get('DEBATER_TOKEN')
    EXT_INPUT_FILE = os.environ.get('EXT_INPUT_FILE')
    PIPELINE_NAME = os.environ.get('PIPELINE_NAME')
    SYSTEM_NAME = os.environ.get('TIRA_SYSTEM_NAME', PIPELINE_NAME)

    DEBATER_CACHE = '/tmp/debater.savestate'
    CHATGPT_ARGUMENTS = '/tmp/chatgpt-arguments.json'


    if os.path.exists(EXT_INPUT_FILE):
        bundle_data.unpack(EXT_INPUT_FILE, CHATGPT_ARGUMENTS, DEBATER_CACHE)
    else:
        print('Didn\'t find bundle file, not extracting.')

    input_directory, output_directory = get_input_directory_and_output_directory(default_input=None)
    dataset = ToucheDataset(topics_file=os.path.join(input_directory, 'queries.jsonl'), corpus_dir=os.path.join(input_directory, 'images'))
    pipelines = get_pipelines(dataset, PYTERRIER_INDEX, CLIP_INDEX, DEBATER_CACHE, CHATGPT_ARGUMENTS, DEBATER_TOKEN)


    topics = dataset.get_topics()

    def evaluate(eval_topics, pipelines, names, perquery=False):
        return pd.concat([
            pt.Experiment(
                list(map(lambda model: apply_stance(stance) >> pt.rewrite.tokenise() >> model, pipelines)),
                eval_topics,
                dataset.get_qrels(variant=stance),
                eval_metrics=['P_10', 'recall_10', 'num_rel', 'num_ret'],
                names=list(map(lambda name: name + '_' + stance.lower(), names)),
                perquery=perquery,
                filter_by_qrels=False,
                filter_by_topics=False,
            ) for stance in ['PRO', 'CON']])

    my_pipelines = []
    my_pipeline_names = []
    for name1 in pipelines.keys():
        for name2 in pipelines[name1].keys():
            my_pipelines.append(pipelines[name1][name2])
            my_pipeline_names.append(name1 + '.' + name2)


    print(evaluate(topics,
        my_pipelines,
        my_pipeline_names))

    if not os.path.exists(EXT_INPUT_FILE):
        bundle_data.pack(EXT_INPUT_FILE, CHATGPT_ARGUMENTS, DEBATER_CACHE)
    else:
        print('Bundle file already exists, not packing bundle.')

    print('Done')
