# Dockerfile for binder
# Reference: https://mybinder.readthedocs.io/en/latest/dockerfile.html#preparing-your-dockerfile
FROM sagemath/sagemath:9.1-py3
RUN sage -pip install git+https://github.com/MCLF/mclf.git@master
COPY --chown=sage:sage . ${HOME}
