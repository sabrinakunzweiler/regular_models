# Dockerfile for binder
# Reference: https://mybinder.readthedocs.io/en/latest/dockerfile.html#preparing-your-dockerfile
FROM sagemath/sagemath:9.0
COPY --chown=sage:sage . ${HOME}
RUN sage -pip install --user --upgrade mclf
