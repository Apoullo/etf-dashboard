# ETF Dashboard - GitHub Pages 部署設計

## Context

現有的 ETF 投資組合儀表板是一個 self-contained HTML 檔案，由三個 Python 腳本產生數據後組裝而成。目前只能在本機執行和瀏覽。需求是將它部署成公開網頁，並每天自動更新數據。

## Architecture

```
GitHub Actions (UTC 22:00 = 台灣 06:00, 週一至週五)
  -> ubuntu-latest + Python 3.12
  -> generate_dashboard_data.py   (~60s)
  -> analyze_all_etfs.py          (~6min)
  -> build_dashboard.py           (<1s)
  -> deploy to gh-pages branch
  -> GitHub Pages serves index.html
```

URL: `https://<username>.github.io/etf-dashboard/`

## Changes Required

### 1. Path Refactoring

所有腳本目前使用硬編碼的絕對路徑 `C:/_Programming/_ClaudeCode/OpenBB/charts/`。需改為相對路徑，以 script 所在目錄為基準。

**Files to modify:**
- `generate_dashboard_data.py` - output path
- `analyze_all_etfs.py` - output path
- `build_dashboard.py` - input/output paths

**Pattern:**
```python
ROOT = Path(__file__).parent
OUT_DIR = ROOT / "charts"
```

### 2. New Files

- `requirements.txt` - pin: yfinance, plotly, pandas, numpy
- `.gitignore` - exclude: .venv/, __pycache__/, *.pyc, .claude/
- `.github/workflows/update.yml` - CI/CD pipeline
- `README.md` - project description (minimal)

### 3. GitHub Actions Workflow

```yaml
name: Update Dashboard
on:
  schedule:
    - cron: '0 22 * * 1-5'  # UTC 22:00 Mon-Fri = 台灣 06:00
  workflow_dispatch: {}       # manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python generate_dashboard_data.py
      - run: python analyze_all_etfs.py
      - run: python build_dashboard.py
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./charts
          publish_branch: gh-pages
```

### 4. build_dashboard.py Output Change

Output filename: `charts/index.html` (instead of `charts/dashboard.html`)
This allows GitHub Pages to serve it at the root URL.

### 5. GitHub Repo Setup

- `gh repo create etf-dashboard --public`
- Push all source code to `main`
- Enable GitHub Pages from `gh-pages` branch
- First manual workflow run to populate `gh-pages`

## Data Flow

1. **generate_dashboard_data.py** fetches 10 portfolio tickers (VOO, QQQM, etc.) via yfinance -> `charts/dashboard_data.json`
2. **analyze_all_etfs.py** fetches 71+ catalog tickers via yfinance -> `charts/etf_analysis.json`
3. **build_dashboard.py** reads both JSON files + embedded catalog -> `charts/index.html`
4. GitHub Actions pushes `charts/` contents to `gh-pages` branch
5. GitHub Pages serves `index.html` at public URL

## Rate Limiting

yfinance is free but has undocumented rate limits. Current mitigations:
- 1-second pause every 10 tickers in analyze_all_etfs.py
- Sequential fetching (no parallel requests)
- Running once daily (not hourly)

If rate-limited, the workflow will fail and retry next day. No data corruption risk since old data stays until successfully replaced.

## Out of Scope

- Backend server / API
- User authentication
- Real-time price streaming
- Email/notification alerts
- Custom domain (can add later)
- Database storage

## Verification

1. After deployment, visit `https://<username>.github.io/etf-dashboard/`
2. Verify all 6 tabs load correctly
3. Check "generatedAt" timestamp in browser console (`DATA.generatedAt`)
4. Next trading day, verify timestamp updated automatically
5. Check GitHub Actions tab for successful workflow runs
