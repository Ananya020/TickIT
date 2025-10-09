### Prereqs
- Python 3.10+ and Node.js 18+/PNPM or NPM
- MySQL (optional if using default SQLite). If using MySQL, have a database created and credentials ready

### Environment variables
Create a `.env` file in `backend/` (or set these in your shell):
```
DATABASE_URL=sqlite:///./tickit.db
JWT_SECRET_KEY=change_me
FRONTEND_URL=http://localhost:3000
# Optional AI keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```
If you use MySQL, set instead:
```
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/DBNAME
```

Create a `.env.local` in `tickit-frontend/`:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Start Backend (Windows PowerShell)
```
cd backend
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
# ensure DB driver if using MySQL
# pip install pymysql

# run server
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs to verify.

### Start Frontend
In a new terminal:
```
cd tickit-frontend
npm install    # or pnpm install
npm run dev    # or pnpm dev
```
Open http://localhost:3000

### Smoke tests
- Register a user via Swagger: POST `/auth/register`
- Login: POST `/auth/login` → copy `access_token`
- Call a protected route like GET `/tickets/all` with `Authorization: Bearer <token>`
- In the UI, log in and verify tickets load

### Common issues
- ModuleNotFoundError (e.g., `jose`): run `pip install -r requirements.txt` in the backend venv
- MySQL driver missing: `pip install pymysql` and use `mysql+pymysql://` URI
- CORS errors: ensure `FRONTEND_URL` matches your frontend URL and `NEXT_PUBLIC_API_URL` points to the backend
