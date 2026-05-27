"""Upload code files to HF Space via API — avoids binary git push rejection."""
import os
from huggingface_hub import HfApi

TOKEN = os.environ["HF_TOKEN"]
REPO = "evgeniimatveevusa/job-market-pulse"

api = HfApi(token=TOKEN)

files = [
    "dashboard/app.py",
    "dashboard/start.sh",
    "src/extract.py",
    "src/transform.py",
    "src/load.py",
    "src/__init__.py",
    "scripts/download_db.py",
    "scripts/upload_db.py",
    "run_pipeline.py",
    "requirements.txt",
    "Dockerfile",
]

hf_readme = """---
title: Job Market Pulse
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Job Market Pulse

Daily tracking of tech job demand, salaries and remote trends — 10 stacks x 10 US cities + remote.

**Full README + screenshots:** https://github.com/evgeniimatveev/job-market-pulse
"""

with open("_readme_tmp.md", "w", encoding="utf-8") as f:
    f.write(hf_readme)

for path in files:
    api.upload_file(
        path_or_fileobj=path,
        path_in_repo=path,
        repo_id=REPO,
        repo_type="space",
    )
    print("Uploaded:", path)

api.upload_file(
    path_or_fileobj="_readme_tmp.md",
    path_in_repo="README.md",
    repo_id=REPO,
    repo_type="space",
)
os.remove("_readme_tmp.md")
print("All files uploaded to HF Space.")
