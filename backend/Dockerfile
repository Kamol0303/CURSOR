FROM python:3.12-slim

WORKDIR /srv

COPY backend /srv/backend

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e /srv/backend

WORKDIR /srv/backend

CMD ["sh", "-c", "alembic -c /srv/backend/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
