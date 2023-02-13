import os
import json

def ensure_pyterrier_is_loaded():
    import pyterrier as pt
    
    if 'PYTERRIER_VERSION' not in os.environ or 'PYTERRIER_HELPER_VERSION' not in os.environ:
        raise ValueError(f'I expect to find the environment variables PYTERRIER_VERSION and PYTERRIER_HELPER_VERSION. Current environment variables: {os.environ}')
    
    pt_version = os.environ['PYTERRIER_VERSION']
    pt_helper_version = os.environ['PYTERRIER_HELPER_VERSION']
    
    if not pt.started():
        print(f'Start PyTerrier with version={pt_version}, helper_version={pt_helper_version}, no_download=True')
        pt.init(version=pt_version, helper_version=pt_helper_version, no_download=True)


def get_input_directory_and_output_directory(default_input):
    input_directory = os.environ.get('TIRA_INPUT_DIRECTORY', None)

    if input_directory:
        print(f'I will read the input data from {input_directory}.')
    else:
        input_directory = default_input
        print(f'I will use a small hardcoded example located in {input_directory}.')

    output_directory = os.environ.get('TIRA_OUTPUT_DIRECTORY', '/tmp/')
    print(f'The output directory is {output_directory}')
    
    return (input_directory, output_directory)


def normalize_run(run, system_name, depth=1000):
    try:
        run['qid'] = run['qid'].astype(int)
    except:
        pass

    run['system'] = system_name
    run = run.copy().sort_values(["qid", "score", "docno"], ascending=[True, False, False]).reset_index()
    run = run.groupby("qid")[["qid", "Q0", "docno", "rank", "score", "system"]].head(1000)

    # Make sure that rank position starts by 1
    run["rank"] = 1
    run["rank"] = run.groupby("qid")["rank"].cumsum()
    
    return run[['qid', 'Q0', 'docno', 'rank', 'score', 'system']]


ensure_pyterrier_is_loaded()