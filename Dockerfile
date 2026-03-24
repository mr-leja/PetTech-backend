# Stage 1: build dependencies
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app
COPY requirements/production.txt .
RUN pip install --no-cache-dir --prefix=/install -r production.txt

# Stage 2: runtime
FROM python:3.12-slim-bookworm AS production
RUN addgroup --system django && adduser --system --ingroup django django
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN chown -R django:django /app
USER django
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
