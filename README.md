# HedgeMath OS MVP

MVP robot hedging operating system theo kiến trúc Agent + FSM + Risk Guard + Grid Math + Winner Genes.

## Chạy nhanh

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

### Giao diện mới
Giao diện hiện tại đã được thay bằng app `QuantDinger-Vue` trong thư mục `frontend`.

```bash
cd frontend
pnpm install
pnpm dev
```

Mặc định app frontend sẽ kết nối tới backend tại `http://127.0.0.1:8000`.

## Safety

Live trading bị tắt mặc định bằng `ALLOW_LIVE_EXECUTION=false`. Đây là bản MVP mô phỏng/paper-first, không phải lời khuyên đầu tư.
