default:
  @just --list


run:
  #!/usr/bin/env bash
  docker build -t suguru-solver .
  docker run -it -p 8000:8000 --rm suguru-solver

install_deps:
  cd backend && pip install -r requirements.txt
  cd frontend && npm install

backend:
  cd backend && uvicorn main:app --reload --port 5001

frontend:
  cd frontend && npm run dev

lint:
  cd backend && black .
  cd frontend && npm run lint

deploy:
  flyctl deploy