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

# COPY knowledge_base into /app/knowledge_base
RUN mkdir -p /app/knowledge_base
COPY knowledge_base/ /app/knowledge_base/

# Symlink so both /knowledge_base and /app/knowledge_base work
RUN ln -s /app/knowledge_base /knowledge_base

# Pre-download ML models during build (not at runtime)
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); \
from sentence_transformers import CrossEncoder; \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

EXPOSE 8000

CMD ["sh", "-c", "python ./scripts/load_documents.py && python ./scripts/seed_demo_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
