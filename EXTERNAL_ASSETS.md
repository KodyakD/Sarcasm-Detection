# External Assets (Large models & datasets)

This project references large model checkpoints, tokenizers, and raw datasets which are intentionally excluded from the Git repository to keep the repository small and portable.

Common excluded items:

- Model directories: `marbert*`, `marbert_sarcasm_model`, `marbert2`, `marbert3`, `marbert4`, `sarcasm_model`.
- Checkpoints: `*.safetensors`, `*.pt`, `*.ckpt`, `model.safetensors`.
- Raw datasets and archives: `data/raw/`, `data/archive/` and large CSV/zip files in `data/`.
- Notebook artifacts: `notebooks/artifacts/`.

How to provide assets for evaluation:

1. Create a local `assets/` folder outside the repository or in a separate storage location (recommended).
2. Download or place model files and datasets into that folder, keeping the same relative structure expected by `backend/config.py` or `inference.py`.
3. Set environment variables or update the `backend/config.py` with paths to the downloaded assets. Example env var:

```bash
export SARCASTIC_ASSETS_PATH=/path/to/assets
```

4. If you must include specific small files in the repository for the instructor, add them to `submission/` (see README) instead of the main tree.

Removing large files already tracked by git:

- To stop tracking a file already committed: `git rm --cached path/to/file && git commit -m "Remove large file from tracking"`.
- To purge large files from history, use `git filter-repo` or the BFG Repo-Cleaner (follow tool docs). These operations rewrite history and should be used carefully.

If you want, I can help prepare an `assets/` packaging script or instructions to download prebuilt artifacts from a cloud storage location.
