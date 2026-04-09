FROM python:3.12-slim

WORKDIR /app

COPY src/apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["celery", "-A", "src.apps.api.workers.celery_app.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
