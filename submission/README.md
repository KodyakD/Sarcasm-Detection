# Submission folder

This folder should contain a minimal, runnable subset of the project for instructor evaluation.

Recommended contents:

- `backend/` — only required modules to run the API (or a single runnable script).
- `requirements.txt` — minimal dependencies for the submission subset.
- `sample_data/` — a very small CSV or JSON file (a few lines) used for smoke testing.
- `RUNNING.md` — clear, step-by-step instructions to run the service locally.

Do NOT include large model checkpoints or raw datasets here. Instead: place them in an `assets/` folder outside the repo and document their expected paths in `EXTERNAL_ASSETS.md`.

If you want, I can extract the minimal backend into this folder for you now.
