# ================================================
# PRAHARI-NET FRONTEND BUILD
# ================================================

FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build


# ================================================
# PRAHARI-NET PRODUCTION RUNTIME
# ================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "-c", "uvicorn wrapper:app --host 0.0.0.0 --port ${PORT:-8000}"]