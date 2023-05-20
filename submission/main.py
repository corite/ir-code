#!/usr/bin/env python3

# execute in tira with: 
# PIPELINE_NAME=bm25_chatgpt_args.diff DEBATER_TOKEN=<the-token> EXT_INPUT_FILE=$inputRun/run.txt TIRA_INPUT_DIRECTORY=$inputDataset TIRA_OUTPUT_DIRECTORY=$outputDir ./main.py

import os
import pandas as pd
from tira_utils import get_input_directory_and_output_directory, normalize_run
from pathlib import Path

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

    def find_pipeline(pipeline_path):
        keys = pipeline_path.split('.')
        pipeline = pipelines
        for key in keys:
            pipeline = pipeline[key]
        return pipeline

    pipeline = find_pipeline(PIPELINE_NAME)
    run = eval_queries(apply_stance('PRO') >> pipeline, apply_stance('CON') >> pipeline, dataset.get_topics())

    if not os.path.exists(EXT_INPUT_FILE):
        bundle_data.pack(EXT_INPUT_FILE, CHATGPT_ARGUMENTS, DEBATER_CACHE)
    else:
        print('Bundle file already exists, not packing bundle.')

    # export resuts
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    #normalize_run(run, SYSTEM_NAME).to_csv(output_directory + f'/run-neville-{PIPELINE_NAME}.txt', sep=' ', header=False, index=False)
    normalize_run(run, SYSTEM_NAME).to_csv(output_directory + 'run.txt', sep=' ', header=False, index=False)

    print('Done')
