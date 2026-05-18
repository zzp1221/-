FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PIP_NO_CACHE_DIR=1
ENV ENABLE_LOCAL_JUDGE=false
ARG INSTALL_LOCAL_JUDGE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY requirements-local-judge.txt /app/requirements-local-judge.txt
RUN pip install --upgrade pip \
 && pip install --timeout 120 --retries 20 --resume-retries 20 -r /app/requirements.txt \
 && if [ "$INSTALL_LOCAL_JUDGE" = "true" ]; then \
      pip install --timeout 120 --retries 20 --resume-retries 20 -r /app/requirements-local-judge.txt; \
    fi

COPY . /app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
