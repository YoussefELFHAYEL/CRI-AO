FROM python:3.12-slim AS builder
WORKDIR /install
COPY backend/requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Copy installed packages and code
COPY --from=builder /install /usr/local
COPY backend/app ./app
COPY backend/data ./data
COPY backend/scripts ./scripts
COPY knowledge_base ./knowledge_base

# 🔥 MAGIC TRICK: Process the documents during the Docker Build!
# We pass dummy variables just to satisfy Pydantic during the build.
RUN GEMINI_API_KEY="AIzaSyALFeW-pWwY2vuBk6fls4iiHfxth5h-ywo" SUPABASE_URL="https://gaxngnkvfquwfbshzkcd.supabase.co" SUPABASE_KEY="sb_publishable_5zpZhDEILKL-9GIcLlc78Q_dNGIJ1PK" \
    python ./scripts/load_documents.py

EXPOSE 8000

# At runtime, we ONLY run the fast demo seeder and start FastAPI
CMD ["sh", "-c", "python ./scripts/seed_demo_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]