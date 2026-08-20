FROM node:20-alpine AS base

# Install Python and dependencies for FastAPI
RUN apk add --no-cache python3 py3-pip build-base python3-dev
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Install Python deps
COPY api/requirements.txt ./
RUN pip install -r requirements.txt

# Build Next.js
RUN npm run build

# Start Script to run both FastAPI and Next.js for deployment (e.g. Render)
RUN echo '#!/bin/sh' > start.sh && \
    echo 'uvicorn api.main:app --host 0.0.0.0 --port 8000 &' >> start.sh && \
    echo 'PORT=10000 npm start' >> start.sh && \
    chmod +x start.sh

EXPOSE 10000
EXPOSE 8000

CMD ["./start.sh"]