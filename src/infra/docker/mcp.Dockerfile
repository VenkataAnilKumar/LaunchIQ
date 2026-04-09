FROM python:3.12-slim

WORKDIR /app

COPY src/apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8001

CMD ["uvicorn", "src.tools.internal.server:app", "--host", "0.0.0.0", "--port", "8001"]
