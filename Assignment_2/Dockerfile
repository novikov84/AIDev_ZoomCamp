# Multi-stage build: build frontend with Node, then serve via FastAPI app on python:3.11-slim

ARG APP_DIR=Assignment_2

FROM node:18-alpine AS client-build
WORKDIR /app/client
COPY ${APP_DIR}/client/package.json ${APP_DIR}/client/package-lock.json* ./ 
RUN npm install
COPY ${APP_DIR}/client/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY ${APP_DIR}/server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy backend source
COPY ${APP_DIR}/server/ ./server/

# Copy built frontend into server static directory
COPY --from=client-build /app/client/dist ./server/dist

# Expose port
EXPOSE 8000

WORKDIR /app/server

CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "8000"]
