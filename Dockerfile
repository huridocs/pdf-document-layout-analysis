FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu24.04 AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    git \
    ninja-build \
    g++ \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3.12 -m venv "$VIRTUAL_ENV"

COPY requirements.txt .
RUN uv pip install --no-cache --python "$VIRTUAL_ENV/bin/python" -r requirements.txt

RUN git init /tmp/detectron2 && \
    cd /tmp/detectron2 && \
    git remote add origin https://github.com/facebookresearch/detectron2 && \
    git fetch --depth 1 origin b599f139756bd3646a26a909caf86a1a159e53a7 && \
    git checkout FETCH_HEAD && \
    uv pip install --no-cache --no-build-isolation --python "$VIRTUAL_ENV/bin/python" . && \
    rm -rf /tmp/detectron2

RUN uv pip install --no-cache --python "$VIRTUAL_ENV/bin/python" pycocotools==2.0.11


FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV HF_HOME=/app/models/.cache/huggingface
ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_VERBOSITY=error
ENV TRANSFORMERS_NO_ADVISORY_WARNINGS=1

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    python3.12 \
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
    tesseract-ocr-ukr \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/src /app/models && \
    addgroup --system python && \
    adduser --system --group --home /app python && \
    chown -R python:python /app

WORKDIR /app

COPY --from=builder --chown=python:python /app/.venv /app/.venv
COPY --chown=python:python --chmod=755 ./start.sh ./start.sh
COPY --chown=python:python ./src/download_models.py ./src/download_models.py
COPY --chown=python:python ./src/configuration.py ./src/configuration.py

USER python

RUN python src/download_models.py
COPY --chown=python:python ./src/. ./src