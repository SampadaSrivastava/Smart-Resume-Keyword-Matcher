# Smart Resume Keyword Matcher

Flask backend + React (Vite) frontend. No database, no login.

## Run (Windows PowerShell) from the smart-resume-matcher folder

Terminal 1 - backend:

    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python app.py

Terminal 2 - frontend:

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173

If PowerShell blocks activation: Set-ExecutionPolicy -Scope Process Bypass
