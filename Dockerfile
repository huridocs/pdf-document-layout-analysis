FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    apt-get install --fix-missing -y -q --no-install-recommends git ninja-build g++ && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/src /app/models

RUN python -m venv $VIRTUAL_ENV

COPY requirements.txt requirements.txt
RUN uv pip install --upgrade pip && \
    uv pip install --no-cache -r requirements.txt

WORKDIR /app

RUN git clone --depth 1 https://github.com/facebookresearch/detectron2 src/detectron2 && \
    cd src/detectron2 && \
    git fetch --depth 1 origin b599f139756bd3646a26a909caf86a1a159e53a7 && \
    git checkout b599f139756bd3646a26a909caf86a1a159e53a7 && \
    uv pip install --no-cache --no-build-isolation . && \
    cd /app && \
    rm -rf src/detectron2
RUN uv pip install --no-cache pycocotools==2.0.11

FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime

RUN apt-get update && \
    apt-get install --fix-missing -y -q --no-install-recommends \
        curl \
        ffmpeg \
        libgomp1 \
        libsm6 \
        libxext6 \
        ocrmypdf \
        pandoc \
        pdftohtml \
        qpdf \
        tesseract-ocr-ara \
        tesseract-ocr-chi-sim \
        tesseract-ocr-deu \
        tesseract-ocr-ell \
        tesseract-ocr-fra \
        tesseract-ocr-hin \
        tesseract-ocr-kor \
        tesseract-ocr-kor-vert \
        tesseract-ocr-mya \
        tesseract-ocr-rus \
        tesseract-ocr-spa \
        tesseract-ocr-tam \
        tesseract-ocr-tha \
        tesseract-ocr-tur \
        tesseract-ocr-ukr && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/src /app/models && \
    addgroup --system python && \
    adduser --system --group python && \
    chown -R python:python /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder --chown=python:python /app/.venv /app/.venv

WORKDIR /app

COPY ./start.sh ./start.sh
COPY --chown=python:python ./src/. ./src
USER python
COPY --chown=python:python ./src/download_models.py ./src/download_models.py
RUN python src/download_models.py
COPY --chown=python:python ./src/. ./src

ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_VERBOSITY=error
ENV TRANSFORMERS_NO_ADVISORY_WARNINGS=1
