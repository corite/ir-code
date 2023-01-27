#!/usr/bin/env python3
import os
import pyterrier as pt
from tira_utils import get_input_directory_and_output_directory, normalize_run

from index import ClipImageIndex, ClipImageSearch
from ui.visuals import pro_con, image_results
from datasets import ToucheImageDataset, ToucheTopics
from text_stance import TextProcessor

# execute in tira with: 
# TIRA_INPUT_DIRECTORY=$inputDataset TIRA_OUTPUT_DIRECTORY=$outputDir /workspace/main.py 


if __name__ == "__main__":
    SYSTEM_NAME = os.environ.get('TIRA_SYSTEM_NAME' ,'neville-longbottom-baseline')

    if not pt.started():
        # tira_utils above should already have done started pyterrier with this configuration to ensure that no internet connection is required (for reproducibility)
        pt.init(version=os.environ['PYTERRIER_VERSION'], helper_version=os.environ['PYTERRIER_HELPER_VERSION'], no_download=True)

    input_directory, output_directory = get_input_directory_and_output_directory(default_input='/workspace/sample-input/full-rank')
    print(input_directory)
    print(output_directory)

    ## TODO do shit


    # export resuts
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    normalize_run(run, SYSTEM_NAME).to_csv(output_directory + '/run.txt', sep=' ', header=False, index=False)




