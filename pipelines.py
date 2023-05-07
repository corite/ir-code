import pyterrier as pt
import pandas as pd
from functools import partial

from neville.index import ClipImageIndex, ClipRetrieve, PyTerrierImageIndex
from neville.debater_stance import DebaterStanceDetector
from neville.stance import apply_stance, flip_stance
from neville.api import ArgsMe, LocalCachedChatGPT
from neville.transformer_utils import ScalarTransformer

import logging
logging.basicConfig(level=logging.INFO)

def get_pipelines(dataset, pt_index_path, clip_index_path, debater_cache_path, chatgpt_arguments_path, debater_api_token):

    if not pt.started():
        pt.init(boot_packages=["com.github.terrierteam:terrier-prf:-SNAPSHOT"])

    pt_index = PyTerrierImageIndex(pt_index_path)
    pt_index.build(dataset.get_image_text_iter())
    clip_index = ClipImageIndex(clip_index_path)
    clip_index.build(dataset.images)
    chatgpt_args = LocalCachedChatGPT(chatgpt_arguments_path)

    def remove_rm3_nan(q):
        return q['query'].replace('^nan', '^0')

    tokeniser = pt.autoclass("org.terrier.indexing.tokenisation.Tokeniser").getTokeniser()
    def strip_markup(text):
        return ' '.join(tokeniser.getTokens(text))

    def query_expand_arguments(query_row):
        arguments = filter(lambda argument: argument.is_pro == (query_row['stance'] == 'PRO'), ArgsMe.arguments(strip_markup(query_row['query'])))
        text = ' '.join(map(lambda argument: strip_markup(argument.text), arguments))
        return text

    def query_expand_arguments_chatgpt(query_row, field='text'):
        arguments = filter(lambda argument: argument.is_pro == (query_row['stance'] == 'PRO'), chatgpt_args.by_topic(int(query_row['qid']), field=field))
        text = ' '.join(map(lambda argument: strip_markup(argument.text), arguments))
        return text

    def query_expand_multiple(query_row, field):
        qid = query_row['qid'].iloc[0]
        stance = query_row['stance'].iloc[0]
        arguments = filter(lambda argument: argument.is_pro == (stance == 'PRO'), chatgpt_args.by_topic(int(qid), field=field))
        qid_field_list = [(qid, argument.text) for argument in arguments]
        results = pd.DataFrame(qid_field_list, columns=['qid', 'query'])
        return pd.merge(query_row.drop('query', axis=1), results, on=['qid'])


    debater = DebaterStanceDetector(pt_index.index, dataset.images, debater_api_token, sentences=5, cache_file=debater_cache_path)

    bm25 = pt.BatchRetrieve(pt_index.index, wmodel='BM25') % 500
    clip = ClipRetrieve(pt_index.index, clip_index, dataset.images, 100) % 500

    # query expand
    bm25_chatgpt_args = (pt.apply.query(query_expand_arguments_chatgpt) >> bm25 >> pt.rewrite.reset())
    clip_chatgpt_args = (pt.apply.by_query(partial(query_expand_multiple, field='text'), add_ranks=False) >> clip >> pt.rewrite.reset())
    clip_chatgpt_image_desc = (pt.apply.by_query(partial(query_expand_multiple, field='image_description'), add_ranks=False) >> clip >> pt.rewrite.reset())

    def get_rerank(query_expansion_pipeline):
        # rerank
        diff_scalar = ScalarTransformer(flip_stance() >> query_expansion_pipeline, -0.5)
        my_diff = pt.rewrite.tokenise() >> query_expansion_pipeline + diff_scalar

        rm3 = pt.rewrite.RM3(pt_index.index, fb_terms=10, fb_docs=3)
        my_rm3 = pt.rewrite.tokenise() >> query_expansion_pipeline >> pt.rewrite.tokenise() >> rm3 >> pt.apply.query(remove_rm3_nan) >> bm25

        my_debater = pt.rewrite.tokenise() >> query_expansion_pipeline >> debater

        return {
            'diff': my_diff,
            'rm3': my_rm3,
            'debater': my_debater,
            'raw': query_expansion_pipeline,
        }

    return {
        'bm25_chatgpt_args': get_rerank(bm25_chatgpt_args),
        'clip_chatgpt_args': get_rerank(clip_chatgpt_args),
        'clip_chatgpt_image_des': get_rerank(clip_chatgpt_image_desc),
    }

