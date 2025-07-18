SamanthaAI
A fullstack AI-powered chat assistant with emotional intelligence and reflection capabilities.

Features
React + Vite frontend
Flask backend with Gemini API integration
Emotion-aware responses
Reflection questions every few turns
Memory/context support


Setup Instructions
1. Backend (Flask)
Create and activate a Python virtual environment:
Install dependencies:
Add your Gemini API key to .env:
Start the backend:
2. Frontend (React + Vite)
Install dependencies:
Start the frontend:
The frontend will proxy api requests to the Flask backend.
Environment Variables
.env (backend): GOOGLE_API_KEY=...
.env.local (frontend, optional): GEMINI_API_KEY=... (not required if using backend proxy)
Prompts
Place compassionate_persona.txt and reflection_prompt.txt in prompts.
Troubleshooting
If you see 500 errors, check backend logs for missing prompt files or API key issues.
Make sure the backend and frontend are running on the correct ports.
Use the provided .gitignore to avoid committing sensitive files.
Deployment
For production, use a WSGI server (e.g., Gunicorn) for Flask and build the frontend with npm run build.