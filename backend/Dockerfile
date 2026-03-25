FROM python:3.12-slim AS builder
WORKDIR /install
COPY backend/requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Copy dependencies
COPY --from=builder /install /usr/local

# Copy application files
COPY backend/app ./app
COPY backend/data ./data
COPY backend/scripts ./scripts

# COPY knowledge_base into /app/knowledge_base (Explicitly!)
RUN mkdir -p /app/knowledge_base
COPY knowledge_base/ /app/knowledge_base/

EXPOSE 8000
RUN ln -s /app/knowledge_base /knowledge_base
CMD ["sh", "-c", "python ./scripts/load_documents.py && python ./scripts/seed_demo_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
