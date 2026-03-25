FROM python:3.12-slim AS builder

WORKDIR /install

COPY backend/requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy application code
COPY backend/app ./app

# Copy knowledge base so it is available at /app/knowledge_base
COPY knowledge_base ./knowledge_base

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
