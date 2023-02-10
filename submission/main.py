#!/usr/bin/env python3
import os
import pyterrier as pt
from tira_utils import get_input_directory_and_output_directory, normalize_run
from pathlib import Path

from datasets import ToucheDataset
from ui.visuals import pt_results
from index import ClipImageIndex, ClipRetrieve
from debater_stance import DebaterStanceDetector
from text_extractor import extract_content

# execute in tira with: 
# DEBATER_TOKEN=<the-token> TIRA_INPUT_DIRECTORY=$inputDataset TIRA_OUTPUT_DIRECTORY=$outputDir /workspace/main.py 
def remove_questionmark(q):
    return q['query'].replace('?', '')

def cutoff(func, limit):
    return lambda image: (z[1] for z in zip(range(limit), func(image)))

if __name__ == "__main__":
    SYSTEM_NAME = os.environ.get('TIRA_SYSTEM_NAME' ,'neville-longbottom-run0')
    PYTERRIER_INDEX = '/data/pyterrier-index'

    if not pt.started():
        # tira_utils above should already have done started pyterrier with this configuration to ensure that no internet connection is required (for reproducibility)
        pt.init(version=os.environ['PYTERRIER_VERSION'], helper_version=os.environ['PYTERRIER_HELPER_VERSION'], no_download=True)

    input_directory, output_directory = get_input_directory_and_output_directory(default_input='/workspace/sample-input/full-rank')

    dataset = ToucheDataset(topics_file= input_directory + 'queries.jsonl', corpus_dir= input_directory + "/images")

    if not os.path.exists(PYTERRIER_INDEX):
        iter_indexer = pt.IterDictIndexer(PYTERRIER_INDEX, overwrite=False, meta={'docno': 25, 'image_id': 10})
        index = iter_indexer.index(dataset.get_corpus_iter())

    debater_token = os.environ.get('DEBATER_TOKEN')

    #TODO
    index = pt.IndexFactory.of(PYTERRIER_INDEX)

    bm25 = pt.apply.query(remove_questionmark) >> pt.BatchRetrieve(index, wmodel='BM25') % 500 >> pt.apply.doc_score(DebaterStanceDetector('PRO', dataset.images, cutoff(extract_content, 10), debater_token, cache_file='/data/cache/debater-cache').rerank(), batch_size=1000)


    # export resuts
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    normalize_run(bm25, SYSTEM_NAME).to_csv(output_directory + '/run.txt', sep=' ', header=False, index=False)
