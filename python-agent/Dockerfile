FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV ENABLE_LOCAL_JUDGE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install --timeout 120 --retries 20 --resume-retries 20 -r /app/requirements.txt

COPY . /app
RUN chmod +x /app/entrypoint.sh

# Copy local judge model (optional, used when ENABLE_LOCAL_JUDGE=true)
COPY grpo_output/judge_model.gguf /app/models/judge_model.gguf

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
