"""
Weekly AI Digest Generator

Fetches trending AI repos from GitHub, trending models from HuggingFace,
and compiles a markdown digest.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone


def github_search(query, sort="stars", order="desc", per_page=15):
    """Search GitHub repos via the search API."""
    params = urllib.parse.urlencode({
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
    })
    url = f"https://api.github.com/search/repositories?{params}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ai-digest-bot",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_trending_ai_repos():
    """Fetch AI/ML repos created or pushed to recently, sorted by stars."""
    now = datetime.now(timezone.utc)
    one_week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    one_month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    sections = []

    queries = [
        (
            "Trending AI/ML Repositories (past week)",
            f"artificial-intelligence machine-learning llm pushed:>{one_week_ago} stars:>100",
            "stars",
            15,
        ),
        (
            "New AI Projects (past month)",
            f"AI agents LLM created:>{one_month_ago} stars:>50",
            "stars",
            10,
        ),
        (
            "Trending Agent Frameworks",
            f"ai-agent framework agentic pushed:>{one_week_ago} stars:>20",
            "stars",
            10,
        ),
    ]

    for title, query, sort, count in queries:
        try:
            result = github_search(query, sort=sort, per_page=count)
            repos = result.get("items", [])
            if repos:
                lines = [f"### {title}\n"]
                for repo in repos:
                    name = repo["full_name"]
                    stars = repo["stargazers_count"]
                    desc = (repo.get("description") or "No description")[:120]
                    url = repo["html_url"]
                    lang = repo.get("language") or "Unknown"
                    lines.append(
                        f"- **[{name}]({url})** - {stars:,} stars ({lang}) — {desc}"
                    )
                sections.append("\n".join(lines))
        except Exception as e:
            sections.append(f"### {title}\n\n_Error fetching: {e}_")

    return "\n\n".join(sections)


def fetch_huggingface_trending():
    """Fetch trending models from HuggingFace."""
    sections = []

    endpoints = [
        ("Most Liked Models (recent)", "https://huggingface.co/api/models?sort=likes7d&direction=-1&limit=15"),
        (
            "Most Downloaded Models",
            "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=10",
        ),
    ]

    for title, url in endpoints:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ai-digest-bot"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                models = json.loads(resp.read().decode())

            lines = [f"### {title}\n"]
            for model in models:
                model_id = model.get("id", "unknown")
                downloads = model.get("downloads", 0)
                likes = model.get("likes", 0)
                pipeline = model.get("pipeline_tag", "unknown")
                lines.append(
                    f"- **[{model_id}](https://huggingface.co/{model_id})** — "
                    f"{downloads:,} downloads, {likes:,} likes ({pipeline})"
                )
            sections.append("\n".join(lines))
        except Exception as e:
            sections.append(f"### {title}\n\n_Error fetching: {e}_")

    return "\n\n".join(sections)


def fetch_huggingface_papers():
    """Fetch trending papers from HuggingFace daily papers."""
    try:
        url = "https://huggingface.co/api/daily_papers?limit=10"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ai-digest-bot"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            papers = json.loads(resp.read().decode())

        lines = ["### Trending AI Papers\n"]
        for paper in papers:
            p = paper.get("paper", {})
            title = p.get("title", "Untitled")
            paper_id = p.get("id", "")
            likes = paper.get("numLikes", 0)
            url = f"https://huggingface.co/papers/{paper_id}" if paper_id else "#"
            lines.append(f"- **[{title}]({url})** — {likes} likes")
        return "\n".join(lines)
    except Exception as e:
        return f"### Trending AI Papers\n\n_Error fetching: {e}_"


def build_digest():
    """Build the full weekly digest."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    week_of = datetime.now(timezone.utc).strftime("%B %d, %Y")

    print("Fetching GitHub trending repos...")
    github_section = fetch_trending_ai_repos()

    print("Fetching HuggingFace trending models...")
    hf_section = fetch_huggingface_trending()

    print("Fetching HuggingFace papers...")
    papers_section = fetch_huggingface_papers()

    digest = f"""# AI Weekly Digest — {week_of}

> Auto-generated weekly roundup of trending AI repositories, models, and research.

---

## GitHub Trending

{github_section}

---

## HuggingFace

{hf_section}

{papers_section}

---

## Models to Watch (Local Inference)

> Models that can run on consumer hardware (Mac Mini, gaming PC, etc.)

| Size Class | Notable Models | Min RAM |
|-----------|---------------|---------|
| ~3-4B | Gemma 4 E2B, Phi-3 Mini | 8GB |
| ~7-9B | Qwen 3.5 9B, Llama 3.1 8B, Gemma 4 E4B | 16GB |
| ~14-20B | Qwen 2.5 14B, DeepSeek-R1 14B | 24GB |
| ~26-34B | Gemma 4 26B-A4B (MoE), Qwen 2.5 32B | 32-48GB |

---

*Generated on {today} by [ai-digest](https://github.com/jeeminhan/ai-digest)*
"""
    return today, digest


def main():
    today, digest = build_digest()

    # Write to digests directory
    output_path = f"digests/{today}.md"
    os.makedirs("digests", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(digest)
    print(f"Digest written to {output_path}")

    # Also write as latest.md for easy access
    with open("digests/latest.md", "w") as f:
        f.write(digest)
    print("Digest written to digests/latest.md")


if __name__ == "__main__":
    main()
