# Multi-stage Dockerfile for Next.js + FastAPI Application
# Target size: ~150MB | Security: Non-root user execution

# ==========================================
# Stage 1: Build Node.js dependencies & standalone Next.js app
# ==========================================
FROM node:20-alpine AS next-builder
WORKDIR /app

# Copy package files and install production & build dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application source code and build Next.js with standalone output
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# ==========================================
# Stage 2: Build Python virtual environment
# ==========================================
FROM python:3.11-alpine AS python-builder
WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

COPY api/requirements.txt ./
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 3: Minimal Runtime Image
# ==========================================
FROM node:20-alpine AS runner
WORKDIR /app

# Install runtime dependencies for Python & PostgreSQL client libs
RUN apk add --no-cache python3 libpq && \
    addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=10000 \
    HOST=0.0.0.0

# Copy Python virtual environment from python-builder
COPY --from=python-builder /opt/venv /opt/venv

# Copy Next.js standalone build artifacts and static assets
COPY --from=next-builder --chown=appuser:appgroup /app/public ./public
COPY --from=next-builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=next-builder --chown=appuser:appgroup /app/.next/static ./.next/static

# Copy FastAPI backend code
COPY --from=next-builder --chown=appuser:appgroup /app/api ./api

# Copy start script
COPY --chown=appuser:appgroup start.sh ./start.sh
RUN chmod +x ./start.sh

# Switch to non-root user
USER appuser:appgroup

EXPOSE 10000 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:10000/ || exit 1

CMD ["./start.sh"]
