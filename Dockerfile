# Espoo Work Map — one container for API + built frontend (Render deploy)

# Stage 1: build the frontend
FROM node:22-alpine AS web
WORKDIR /web
COPY app/web/package.json app/web/package-lock.json ./
RUN npm ci
COPY app/web ./
RUN npm run build

# Stage 2: production runtime
FROM python:3.13-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TM_DB_PATH=/tmp/talentmatch.sqlite
WORKDIR /srv

COPY requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app ./app
COPY db/schema.sql ./db/schema.sql
COPY db/seed ./db/seed
COPY scripts ./scripts
COPY --from=web /web/dist ./app/web/dist

RUN useradd --create-home --uid 10001 ewm && chown -R ewm:ewm /srv
USER ewm

EXPOSE 8000
CMD uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
