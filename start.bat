@echo off
echo Lancement du backend (FastAPI)...
start "Backend" cmd /k "python main.py"

echo Lancement du frontend (Next.js)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo L'application est en cours de demarrage...
echo Le backend sera accessible sur http://localhost:8000
echo Le frontend sera accessible sur http://localhost:3000
