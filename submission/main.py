#!/usr/bin/env python3

# execute in tira with: 
# DEBATER_TOKEN=<the-token> TIRA_INPUT_DIRECTORY=$inputDataset TIRA_OUTPUT_DIRECTORY=$outputDir ./main.py 

import os
import pyterrier as pt
import pandas as pd
from tira_utils import get_input_directory_and_output_directory, normalize_run
from pathlib import Path

from neville.datasets import ToucheDataset
from neville.index import ClipImageIndex, ClipRetrieve, PyTerrierImageIndex
from neville.debater_stance import DebaterStanceDetector
from neville.stance import apply_stance

import logging
logging.basicConfig(level=logging.INFO)


def eval_queries(pipeline_pro, pipeline_con, queries, head=10):
    return pd.concat([(pipeline_pro % head)(queries), (pipeline_con % head)(queries)]).rename(columns={'stance': 'Q0'})

if __name__ == '__main__':

    SYSTEM_NAME = os.environ.get('TIRA_SYSTEM_NAME' ,'neville-longbottom-run0')
    PYTERRIER_INDEX = '/cache/pyterrier-index'
    CLIP_INDEX = '/cache/clip-index.npy'
    DEBATER_CACHE = '/cache/debater-cache'

    if not pt.started():
        # tira_utils above should already have done started pyterrier with this configuration to ensure that no internet connection is required (for reproducibility)
        pt.init(version=os.environ['PYTERRIER_VERSION'], helper_version=os.environ['PYTERRIER_HELPER_VERSION'], no_download=True)

    input_directory, output_directory = get_input_directory_and_output_directory(default_input=None)

    debater_token = os.environ.get('DEBATER_TOKEN')

    dataset = ToucheDataset(topics_file=os.path.join(input_directory, 'queries.jsonl'), corpus_dir=os.path.join(input_directory, 'images'))

    clip_index = ClipImageIndex(CLIP_INDEX)
    clip_index.build(dataset.images)
    pt_index = PyTerrierImageIndex(PYTERRIER_INDEX)
    pt_index.build(dataset.get_image_text_iter())

    def remove_questionmark(q):
        return q['query'].replace('?', '')

    debater = DebaterStanceDetector(pt_index.index, dataset.images, debater_token, sentences=5, cache_file=DEBATER_CACHE)

    bm25 = pt.apply.query(remove_questionmark) >> pt.BatchRetrieve(pt_index.index, wmodel='BM25') % 20 >> pt.apply.doc_score(debater, batch_size=1000)
    clip = ClipRetrieve(clip_index, dataset.images, 20) >> pt.apply.doc_score(debater, batch_size=1000)

    bm25_pro = apply_stance('PRO') >> bm25
    bm25_con = apply_stance('CON') >> bm25
    clip_pro = apply_stance('PRO') >> clip
    clip_con = apply_stance('CON') >> clip

    run = eval_queries(bm25_pro, bm25_con, dataset.get_topics())

    # export resuts
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    normalize_run(run, SYSTEM_NAME).to_csv(output_directory + '/run.txt', sep=' ', header=False, index=False)
