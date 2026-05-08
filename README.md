# Intelligent Sarcasm & Irony Detection System

This project provides a local multilingual sarcasm and irony detection platform with:

- FastAPI backend for inference and API serving
- React frontend for interactive analysis
- Notebook workflow for training and evaluation artifacts

## Project Structure

- `backend/` API service and backend tests
- `frontend/` SPA client
- `data/` cleaned and source datasets
- `notebooks/` training and evaluation notebooks
- `submission/` minimal packaging guidance

## Exposed API Endpoints

- `POST /analyze`
- `POST /analyze-file`
- `GET /history`
- `GET /health`

## Quick Start

Backend:

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Note: model binaries are excluded from this repository. Place checkpoints locally and configure `MODEL_DIR` as described in `EXTERNAL_ASSETS.md`.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## External Assets

- See `EXTERNAL_ASSETS.md` for model checkpoints and large datasets that are intentionally excluded from GitHub.

## Validation Commands

Backend tests:

```bash
cd backend
source ../.venv/Scripts/activate
pytest -q
```

Frontend typecheck:

```bash
cd frontend
npm run typecheck
```

## Submission guidance

To prepare a clean submission for evaluation by your instructor:

1. Keep the repository small: large model checkpoints and raw datasets are intentionally excluded. See `EXTERNAL_ASSETS.md` for details.
2. Create a `submission/` folder containing only what the instructor needs: minimal backend code, a small sample dataset (or links), and a `README.md` with run steps.
3. Ensure `.gitignore` excludes large models and raw data (already configured).
4. If large files were previously committed, remove them from tracking with:

```bash
git rm --cached path/to/large_file
git commit -m "Remove large file from tracking"
```

5. To completely remove large files from history, use `git filter-repo` or BFG — I can help if you want.

If you'd like, I can now create a `submission/` skeleton with minimal runnable instructions and a tiny sample data file.
