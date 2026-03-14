# SkyBalance AVL
Backend: Python + FastAPI | Frontend: Angular

## Backend
  cd backend
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload

  API:  http://localhost:8000
  Docs: http://localhost:8000/docs

## Frontend
  cd frontend
  npm install -g @angular/cli
  ng new skybalance-frontend --routing --style=scss
  cd skybalance-frontend
  ng serve