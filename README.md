# AI Digest

Automated weekly roundup of trending AI repositories, models, and research.

## What it tracks

- **GitHub**: trending AI/ML repos, new projects, agent frameworks
- **HuggingFace**: trending models, most downloaded, daily papers
- **Local inference**: models that run on consumer hardware

## How it works

A GitHub Action runs every Monday at 9am UTC, fetches the latest data, and commits a markdown digest to `digests/`.

You can also run it manually from the Actions tab or locally:

```bash
python scripts/fetch_digest.py
```

## Digests

Browse the `digests/` folder or check `digests/latest.md` for the most recent roundup.
