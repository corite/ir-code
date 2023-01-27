FROM webis/tira-ir-starter-pyterrier:0.0.1-base

COPY ./index.py ./datasets.py ./text_stance.py /ui/visuals.py /workspace/
COPY ./runs/baseline/main.py /workspace/

RUN chmod +x /workspace/main.py