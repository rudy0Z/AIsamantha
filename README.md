

---

# 🌸 SamanthaAI

*A fullstack AI-powered chat assistant with emotional intelligence and reflection capabilities.*

---

## ✨ Features

* 🧠 Emotion-aware, compassionate responses
* 🔁 Reflection questions every few turns
* 🧾 Memory and context support
* ⚛️ **Frontend:** React + Vite
* 🐍 **Backend:** Flask with Gemini API integration

---

## 📁 Project Structure

```
├── api/
│   ├── main.py
│   ├── memory_manager.py
│   └── prompts/
│       ├── compassionate_persona.txt
│       └── reflection_prompt.txt
├── components/
├── hooks/
├── services/
├── App.tsx
├── index.tsx
├── index.html
├── requirements.txt
├── package.json
├── vite.config.ts
├── .env (backend)
├── .env.local (frontend, optional)
```

---

## ⚙️ Setup Instructions

### 1. Backend (Flask)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

* Add your **Gemini API key** to a `.env` file in the `backend/` directory:

  ```
  GOOGLE_API_KEY=your-gemini-api-key-here
  ```

* Start the backend server:

  ```bash
  python app.py
  ```

---

### 2. Frontend (React + Vite)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

> The frontend is configured to **proxy API requests** to the Flask backend.

---

## 🔐 Environment Variables

### Backend (`.env`)

```
GOOGLE_API_KEY=your-gemini-api-key
```


## 🛠️ Troubleshooting

* If you encounter **500 errors**, check:

  * That your API key is valid
  * That all prompt files are present in the correct directory
* Ensure the backend (e.g. port `5000`) and frontend (e.g. port `5173`) are running and not blocked
* Use the provided `.gitignore` to avoid committing sensitive files like `.env`

---

## 🧠 More Info

Refer to the source code and inline comments for deeper understanding of how SamanthaAI works.

---
