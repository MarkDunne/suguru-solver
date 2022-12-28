FROM node as frontend_builder
WORKDIR /app/

COPY frontend/package*.json .
RUN npm install

COPY frontend/ .
RUN ls -la
RUN npm run build

FROM python:3.10-slim
WORKDIR /app/
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY backend/ .
COPY --from=frontend_builder /app/dist/ ./dist/

CMD uvicorn main:app --port 8000 --host 0.0.0.0
