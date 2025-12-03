# Multi-stage build: build frontend with Node, then serve via FastAPI app on python:3.11-slim

FROM node:18-alpine AS client-build
WORKDIR /app/client
COPY client/package.json client/package-lock.json* ./ 
RUN npm install
COPY client/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy backend source
COPY server/ ./server/

# Copy built frontend into server static directory
COPY --from=client-build /app/client/dist ./server/dist

# Expose port
EXPOSE 8000

WORKDIR /app/server

CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "8000"]
