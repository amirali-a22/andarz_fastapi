# Frontend GUI for Cryptocurrency Price Checker

![Cryptocurrency Price Checker](crypto.png)

## نحوه اجرا

### 1. اجرای FastAPI (Backend)

```bash
# از پوشه اصلی پروژه
python3 -m venv .venv

pip install -r requirements.txt

fastapi dev main.py
```

سرور روی `http://localhost:8000` اجرا می‌شود.

### 2. اجرای Frontend

```bash
# از پوشه frontend
cd frontend
python -m http.server 8080
```

سپس در مرورگر باز کنید: `http://localhost:8080`

## نکته مهم

برای کارکرد frontend، باید CORS را در `main.py` فعال کنید:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
