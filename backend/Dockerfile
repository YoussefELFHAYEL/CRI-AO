FROM python:3.12-slim AS builder

WORKDIR /install

COPY backend/requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy backend app
COPY backend/app ./app

# Copy data folder
COPY backend/data ./data

# Copy scripts
COPY backend/scripts ./scripts

# Copy knowledge base inside /app (Changed this line!)
COPY knowledge_base ./knowledge_base

EXPOSE 8000

CMD ["sh", "-c", "python ./scripts/load_documents.py && python ./scripts/seed_demo_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]