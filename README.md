# Downpour Trade AI

A deterministic, rules-based crypto trade-decision engine for Binance-listed pairs.

**No LLM. No hallucinations. Every number traceable to live exchange data.**

## Quick start (CLI)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python cli.py analyze BTC/USDT --tf 1h
python cli.py scan --top 20 --tf 1h
python cli.py backtest BTC/USDT --months 12
python cli.py calibrate
pytest -v
```

## API (Phase 2)

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

Endpoints: `/health`, `/analyze`, `/scan`, `/history`, `/backtest-stats`, `/pairs`

Deploy `api/` to Railway or Render (Singapore/EU region). Set env vars:

- `ALLOWED_ORIGINS` — your Vercel domain + `http://localhost:3000`
- `DATABASE_URL` — optional, defaults to SQLite at `./data/downpour.db`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — optional alerts
- `SCAN_INTERVAL_MIN`, `TOP_PAIRS_COUNT`

**Recommended for production:** [Hetzner deploy guide](deploy/hetzner/DEPLOY.md) — 4 GB RAM for ~€4–6/mo (Docker + Caddy + HTTPS).

## Web (Phase 2)

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Deploy `web/` to Vercel with `NEXT_PUBLIC_API_URL` pointing at your API.

**Option A (recommended):** Vercel Project Settings → General → **Root Directory** → `web`

**Option B:** Leave Root Directory blank — root `package.json` + `vercel.json` run the build from `web/` automatically.

## Deploy checklist (fix "Failed to fetch")

1. **Render API** (Singapore) must be live. Test: `curl https://YOUR-SERVICE.onrender.com/health`
2. **Vercel env var:** `NEXT_PUBLIC_API_URL` = `https://YOUR-SERVICE.onrender.com` → **Redeploy** (public vars are baked at build time)
3. **Render env var:** `ALLOWED_ORIGINS` = `https://downpour-trade-ai-virid.vercel.app,http://localhost:3000` → Redeploy API
4. First request to Render free tier may take 30–60s (cold start)

## Architecture

```
engine/     Deterministic signal core (unchanged by API/web)
api/        FastAPI wrapper, scheduler, SQLite, Telegram alerts
web/        Next.js dashboard
research/   Walk-forward experiment runner (promotion gate)
research_platform/  Optional PostgreSQL/Timescale MDS (see docs/RESEARCH_PLATFORM.md)
```

**Research:** Before changing lane scores, run `python cli.py research walk-forward --compare` and record results in `research/experiments/`. See `Research_Roadmap.md` and `.cursor/rules/engine-promotion-gate.mdc`.

Four lanes → strict synthesizer → NO-TRADE by default:

| Lane | Source |
|------|--------|
| Technical | EMA, RSI, MACD, ADX |
| Flow | Funding, OI, taker imbalance |
| Structure | S/R levels + order-book walls |
| Regime | Volatility gate + dynamic weights |

## Honest limits

- Win rates come from history; regimes change. Re-run `calibrate` monthly.
- Order-book walls can be spoofed; capped influence reflects that.
- The engine cannot see news. A SHOCK-regime gate stands aside when volatility explodes.
- **Backtest/calibration** use degraded structure (no book) and often no taker flow — see [docs/BACKTEST_FIDELITY.md](docs/BACKTEST_FIDELITY.md).
- **Scale:** SQLite is single-writer; see [docs/INFRASTRUCTURE_SCALE.md](docs/INFRASTRUCTURE_SCALE.md) before multi-replica deploy.
- This is decision support, not financial advice. Risk only what you can afford to lose.
