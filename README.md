# ISL Visa Tracker — GitHub Pages

Free hosting, no server. A GitHub Actions workflow scrapes the source site every ~10 minutes,
writes `data/applicants.json`, and deploys the static site to GitHub Pages.

## Setup
1. Push this folder to a **public** GitHub repo (public = unlimited free Actions minutes).
2. Repo → **Settings → Pages → Source: GitHub Actions**.
3. Repo → **Actions** tab → run **Update data and deploy** once (or just push).
4. Your site: `https://<username>.github.io/<repo>/`

## Notes
- Data is up to ~10–15 min old (GitHub cron is best-effort, 5 min minimum).
- Optional: add a repo variable `DASHBOARD_URL` (Settings → Secrets and variables → Actions → Variables) if the source site address changes.
- `api/` is no longer used on Pages; it only matters if you deploy to Vercel again.
