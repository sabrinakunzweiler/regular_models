# Dockerfile for binder
# Reference: https://mybinder.readthedocs.io/en/latest/dockerfile.html#preparing-your-dockerfile
FROM sagemath/sagemath:9.1-py3
COPY --chown=sage:sage . ${HOME}
# it would be better to download the current version of mclf: 
# RUN sage -pip install git+https://github.com/MCLF/mclf
RUN sage -pip install --user --upgrade mclf