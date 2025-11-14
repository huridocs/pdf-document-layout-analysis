FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install --fix-missing -y -q --no-install-recommends \
    libgomp1 ffmpeg libsm6 pdftohtml libxext6 git ninja-build g++ qpdf pandoc curl \
    ocrmypdf tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-deu tesseract-ocr-ara \
    tesseract-ocr-mya tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-tha \
    tesseract-ocr-chi-sim tesseract-ocr-tur tesseract-ocr-ukr tesseract-ocr-ell \
    tesseract-ocr-rus tesseract-ocr-kor tesseract-ocr-kor-vert \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY ./src/. ./src
COPY ./models/. ./models/
COPY ./start.sh ./start.sh

# Setup detectron2 with --no-build-isolation since torch is already installed
RUN cd src && git clone https://github.com/facebookresearch/detectron2 && \
    cd detectron2 && git checkout 70f454304e1a38378200459dd2dbca0f0f4a5ab4 && \
    uv pip install --no-build-isolation -e .

RUN uv pip install pycocotools==2.0.8
RUN uv run python src/download_models.py

RUN uv run python -c "import detectron2; print(f'detectron2 installed at: {detectron2.__file__}')"

ENV PYTHONPATH="${PYTHONPATH}:/app/src"
ENV TRANSFORMERS_VERBOSITY=error
ENV TRANSFORMERS_NO_ADVISORY_WARNINGS=1
