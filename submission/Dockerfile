FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime
# modified base image to get python3.10 instead of python3.7
ENV PYTERRIER_VERSION='5.7'
ENV PYTERRIER_HELPER_VERSION='0.0.7'

RUN apt-get update \
	&& apt-get install -y git openjdk-11-jdk \
	&& pip3 install python-terrier pandas jupyterlab runnb \
	&& python3 -c "import pyterrier as pt; pt.init(version='${PYTERRIER_VERSION}', helper_version='${PYTERRIER_HELPER_VERSION}');"

ENV PYTHONPATH=/workspace/

# custom stuff below here

RUN pip install imageio mistletoe boilerpy3 debater-python-api ftfy spacy transformers datasets nltk

COPY ./tira_utils.py ./datasets.py ./index.py ./debater_stance.py ./text_extractor.py /workspace/
COPY ./ui/visuals.py /workspace/ui/
COPY ./submission/main.py /workspace/

RUN chmod +x /workspace/main.py