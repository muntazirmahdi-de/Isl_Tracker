"""
Uploads every file in this folder to your GitHub repo using only Python (no git needed).
Also switches GitHub Pages to "GitHub Actions" mode.

Usage:   python upload_to_github.py            (Windows: py upload_to_github.py)
Test:    python upload_to_github.py --dry-run  (lists files, uploads nothing)
"""
import base64, getpass, json, os, sys, urllib.request, urllib.error

OWNER = "muntazirmahdi-de"     # your GitHub username
REPO  = "Isl_Tracker"          # repo name (create it first on github.com, Public)
BRANCH = "main"
SKIP = {"upload_to_github.py", "GUIDE.md"}
API = "https://api.github.com"
DRY = "--dry-run" in sys.argv


def call(method, path, token, body=None):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "isl-tracker-uploader",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"message": raw.decode(errors="replace")}


def collect_files():
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for root, _, files in os.walk(here):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, here).replace(os.sep, "/")
            if rel in SKIP or rel.endswith((".zip", ".pyc")) or "__pycache__" in rel:
                continue
            out.append((rel, full))
    return sorted(out)


def main():
    files = collect_files()
    print(f"Found {len(files)} files:")
    for rel, _ in files:
        print("  ", rel)
    if DRY:
        print("Dry run only. Nothing uploaded.")
        return

    token = getpass.getpass("Paste your GitHub token (typing is hidden), then Enter: ").strip()
    code, info = call("GET", f"/repos/{OWNER}/{REPO}", token)
    if code != 200:
        sys.exit(f"Cannot open repo {OWNER}/{REPO}: {info.get('message')}\n"
                 "Check the repo name, that it exists, and that the token has access to it.")

    for rel, full in files:
        with open(full, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        # If the file already exists we need its 'sha' to overwrite it.
        code, existing = call("GET", f"/repos/{OWNER}/{REPO}/contents/{rel}?ref={BRANCH}", token)
        body = {"message": f"Add {rel}", "content": content, "branch": BRANCH}
        if code == 200 and isinstance(existing, dict) and "sha" in existing:
            body["sha"] = existing["sha"]
            body["message"] = f"Update {rel}"
        code, res = call("PUT", f"/repos/{OWNER}/{REPO}/contents/{rel}", token, body)
        if code in (200, 201):
            print(f"OK    {rel}")
        else:
            print(f"FAIL  {rel}: {res.get('message')}")
            if code in (401, 403, 404):
                print("      Token problem? It needs Contents: Read and write on this repo.")

    # Turn on Pages with 'GitHub Actions' as the source (needs Pages permission on the token).
    code, res = call("POST", f"/repos/{OWNER}/{REPO}/pages", token, {"build_type": "workflow"})
    if code in (200, 201, 409):
        code, res = call("PUT", f"/repos/{OWNER}/{REPO}/pages", token, {"build_type": "workflow"})
        print("Pages source set to GitHub Actions.")
    else:
        print("Could not set Pages automatically:", res.get("message"))
        print("Do it by hand: repo > Settings > Pages > Source = GitHub Actions.")

    print(f"\nDone. Watch the run here: https://github.com/{OWNER}/{REPO}/actions")
    print(f"Your site (after a green tick): https://{OWNER}.github.io/{REPO}/")


main()
