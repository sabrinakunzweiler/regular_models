# Dockerfile for binder
# Reference: https://mybinder.readthedocs.io/en/latest/dockerfile.html#preparing-your-dockerfile
FROM sagemath/sagemath:9.1-py3
COPY --chown=sage:sage . ${HOME}
RUN apt-get update \
	&& apt-get install git
RUN sage -pip install git+https://github.com/MCLF/mclf