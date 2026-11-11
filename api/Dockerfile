FROM mirror.gcr.io/python:3.12.12-slim-bookworm AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -u 10001 -m lab
COPY api api
COPY docs docs

# One-shot account initialization; administrator credentials are mounted only here.
FROM base AS seed
COPY scripts/seed.py scripts/seed.py
COPY sql/seeds.sql sql/seeds.sql
CMD ["python", "scripts/seed.py"]

FROM base AS api
USER lab
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
