FROM webis/tira-ir-starter-pyterrier:0.0.1-base

COPY ./tira_utils.py ./datasets.py ./ui/visuals.py ./index.py ./debater_stance.py ./text_extractor.py /workspace/
COPY ./runs/run0/main.py /workspace/

RUN chmod +x /workspace/main.py