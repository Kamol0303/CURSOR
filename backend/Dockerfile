FROM python:3.12-slim

# Docker Desktop proxy can block pip during build — allow override from compose build args
ARG HTTP_PROXY=
ARG HTTPS_PROXY=
ARG http_proxy=
ARG https_proxy=
ENV HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    http_proxy=${http_proxy} \
    https_proxy=${https_proxy} \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

RUN apt-get update && apt-get install -y --no-install-recommends openssl bash && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
        --index-url https://pypi.org/simple/ \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org

COPY . .

RUN chmod +x scripts/entrypoint.sh scripts/dev_bootstrap.sh scripts/staging_bootstrap.sh scripts/production_bootstrap.sh

ENV PYTHONPATH=/app
ENV JWT_PRIVATE_KEY_PATH=/secrets/jwt_private.pem
ENV JWT_PUBLIC_KEY_PATH=/secrets/jwt_public.pem

EXPOSE 8000

ENTRYPOINT ["sh", "./scripts/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
