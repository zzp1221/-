FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-dri \
    libegl-mesa0 \
    libglfw3 \
    xvfb \
    xauth \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY wheels /app/wheels

RUN grep -Ev '^(torch|torchaudio)([<>=].*)?$' /app/requirements.txt > /tmp/requirements-no-torch.txt \
 && pip install --upgrade pip \
 && pip install --timeout 120 --retries 20 --resume-retries 20 -r /tmp/requirements-no-torch.txt \
 && pip install --timeout 120 --retries 20 --resume-retries 20 /app/wheels/torch-2.11.0+cu129-cp311-cp311-manylinux_2_28_x86_64.whl --extra-index-url https://pypi.nvidia.com \
 && pip install --timeout 120 --retries 20 --resume-retries 20 \
    torchvision==0.26.0+cu129 \
    torchaudio==2.11.0+cu129 \
    --index-url https://download.pytorch.org/whl/cu129 \
    --extra-index-url https://pypi.nvidia.com \
    --no-deps \
 && pip install --timeout 120 --retries 20 --resume-retries 20 pyyaml \
 && pip install --timeout 120 --retries 20 --resume-retries 20 "mediapipe>=0.10,<0.10.10"

COPY . /app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
