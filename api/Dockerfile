FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY api/requirements.txt ./api-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r api-requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE 8000

CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
