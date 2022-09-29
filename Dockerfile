# Dockerfile for binder
# Reference: https://mybinder.readthedocs.io/en/latest/dockerfile.html#preparing-your-dockerfile
FROM sagemath/sagemath:9.1-py3
COPY --chown=sage:sage . ${HOME}
# RUN sage -pip install --user --upgrade mclf 
# it would be better to download the current version of mclf: 
RUN apt-get update && apt-get install -y git
RUN sage -pip install git+https://github.com/MCLF/mclf
#USER root
#RUN apt-get -qq update \
# && apt-get -qq install -y --no-install-recommends git \
# && apt-get -qq clean
#USER sage

#RUN sage -pip install git+https://github.com/MCLF/mclf.git
