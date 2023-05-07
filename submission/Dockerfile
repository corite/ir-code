FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime
# modified base image to get python3.10 instead of python3.7

ENV PYTERRIER_VERSION='5.7'
ENV PYTERRIER_HELPER_VERSION='0.0.7'

RUN apt-get update \
	&& apt-get install -y git openjdk-11-jdk \
	&& pip3 install python-terrier pandas \
	&& python3 -c "import pyterrier as pt; pt.init(version='${PYTERRIER_VERSION}', helper_version='${PYTERRIER_HELPER_VERSION}', boot_packages=['com.github.terrierteam:terrier-prf:-SNAPSHOT']);"

ENV PYTHONPATH=/workspace/

# custom stuff below here

RUN pip install imageio mistletoe boilerpy3 debater-python-api ftfy spacy transformers datasets nltk savestate

WORKDIR /workspace

COPY ./api.py ./datasets.py ./debater_stance.py ./index.py ./__init__.py ./pipelines.py ./stance.py ./text_extractor.py ./transformer_utils.py ./neville/
COPY ./submission/tira_utils.py ./submission/main.py ./submission/eval.py ./submission/bundle_data.py ./

RUN chmod +x ./main.py
RUN chmod +x ./eval.py

# download nltk and transformers models into docker image
RUN python3 -c "import main"
