#!/usr/bin/env python3
"""
Artisan Coat — Blog GitHub Publisher
Pushes one or more files to the artisancoat GitHub repo via the GitHub API.
Usage: python push-to-github.py <file_path_in_repo> <local_file_path> [commit_message]
Example: python push-to-github.py blog/my-post.html /path/to/my-post.html "Add blog post"
"""

import sys
import json
import base64
import os

try:
    import requests
except ImportError:
    os.system("pip install requests --break-system-packages -q")
    import requests

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def push_file(repo_path, local_path, commit_message, config):
    """Push a single file to GitHub via the API."""
    token = config["github_token"]
    owner = config["github_owner"]
    repo = config["github_repo"]
    branch = config["github_branch"]

    if token == "YOUR_GITHUB_TOKEN_HERE":
        print("ERROR: Please fill in your GitHub token in blog-automation/config.json")
        print("  Get one at: https://github.com/settings/tokens (needs 'repo' scope)")
        return False

    # Read local file
    with open(local_path, "rb") as f:
        content = f.read()
    content_b64 = base64.b64encode(content).decode("utf-8")

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Check if file exists (need SHA to update)
    get_resp = requests.get(url, headers=headers, params={"ref": branch})
    sha = None
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")

    payload = {
        "message": commit_message,
        "content": content_b64,
        "branch": branch
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(url, headers=headers, json=payload)

    if put_resp.status_code in (200, 201):
        action = "Updated" if sha else "Created"
        print(f"  ✓ {action}: {repo_path}")
        return True
    else:
        print(f"  ✗ Failed to push {repo_path}: {put_resp.status_code} — {put_resp.text[:200]}")
        return False

def push_posts_manifest(posts_manifest_local_path, config):
    """Push the posts.json manifest."""
    return push_file(
        config["posts_manifest_path"],
        posts_manifest_local_path,
        "Update blog posts manifest",
        config
    )

def push_blog_post(local_html_path, slug, config):
    """Push a single blog post HTML file."""
    repo_path = f"{config['blog_path']}/{slug}.html"
    commit_msg = f"Add blog post: {slug}"
    return push_file(repo_path, local_html_path, commit_msg, config)

if __name__ == "__main__":
    config = load_config()

    if len(sys.argv) < 3:
        print("Usage: python push-to-github.py <repo_path> <local_path> [commit_message]")
        print("Example: python push-to-github.py blog/my-post.html /tmp/my-post.html")
        sys.exit(1)

    repo_path = sys.argv[1]
    local_path = sys.argv[2]
    commit_msg = sys.argv[3] if len(sys.argv) > 3 else f"Update {repo_path}"

    print(f"Pushing {local_path} → {repo_path}")
    success = push_file(repo_path, local_path, commit_msg, config)
    sys.exit(0 if success else 1)
