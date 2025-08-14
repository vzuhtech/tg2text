FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PORT=8080

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
	ffmpeg \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for better caching
COPY requirements.txt /app/requirements.txt
RUN python -m venv /opt/venv \
	&& . /opt/venv/bin/activate \
	&& pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Use venv
ENV PATH="/opt/venv/bin:$PATH"

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"