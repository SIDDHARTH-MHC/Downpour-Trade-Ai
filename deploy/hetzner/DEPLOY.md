# Deploy Downpour Trade AI API on Hetzner

Host the **FastAPI backend** on a Hetzner VPS. Keep the **Next.js frontend on Vercel**.

```
Browser → Vercel (web) → Hetzner VPS (API + Caddy HTTPS) → Binance
```

**Recommended server:** CX22 (~€4–6/mo) — 2 vCPU, 4 GB RAM, 40 GB disk  
**Region:** Falkenstein or Nuremberg (EU — works with Binance futures data)

---

## 1. Create the VPS

1. Sign up at [hetzner.com/cloud](https://www.hetzner.com/cloud)
2. **New Project** → **Add Server**
3. Location: **Falkenstein** or **Nuremberg**
4. Image: **Ubuntu 24.04**
5. Type: **CX22** (or CPX11 if CX22 unavailable)
6. Networking: IPv4 + IPv6
7. SSH key: add yours (recommended) or use password
8. Create server — note the **IP address**

---

## 2. Point a domain (required for HTTPS)

Buy a domain (Namecheap, Cloudflare, etc.) and add an **A record**:

| Type | Name | Value |
|------|------|-------|
| A | `api` | `YOUR_HETZNER_IP` |

Example: `api.yourdomain.com` → `123.456.789.0`

Wait 5–15 minutes for DNS to propagate.

---

## 3. SSH into the server

```bash
ssh root@YOUR_HETZNER_IP
```

---

## 4. Install Docker

```bash
apt update && apt upgrade -y
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin git
```

Verify:

```bash
docker --version
docker compose version
```

---

## 5. Clone the repo

```bash
mkdir -p /opt/downpour && cd /opt/downpour
git clone https://github.com/SIDDHARTH-MHC/Downpour-Trade-Ai.git .
```

---

## 6. Configure environment

```bash
cd deploy/hetzner
cp .env.example .env
nano .env
```

Set at minimum:

```env
DOMAIN=api.yourdomain.com
ALLOWED_ORIGINS=https://downpour-trade-ai-virid.vercel.app,http://localhost:3000
SCAN_PAIR_LIMIT=5
```

Save and exit.

---

## 7. Open firewall ports

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

Hetzner Cloud Console → your server → **Firewalls** (if using cloud firewall): allow TCP 80, 443, 22.

---

## 8. Start the stack

```bash
cd /opt/downpour/deploy/hetzner
docker compose up -d --build
```

First build takes ~3–5 minutes.

Check logs:

```bash
docker compose logs -f api
```

---

## 9. Verify API

```bash
curl https://api.yourdomain.com/health
```

Expected:

```json
{"status":"ok","app":"Downpour Trade AI",...}
```

Trigger first scan:

```bash
curl -X POST "https://api.yourdomain.com/scan?tf=1h&refresh=true&limit=5"
```

Trigger calibration (optional):

```bash
curl -X POST "https://api.yourdomain.com/calibrate?months=6"
```

---

## 10. Update Vercel frontend

Vercel → Project → **Settings** → **Environment Variables**

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.yourdomain.com` |

**Redeploy** Vercel (required — public env vars bake at build time).

---

## 11. Smoke test

1. Open `https://downpour-trade-ai-virid.vercel.app`
2. Dashboard should load within 1–2 minutes (after scan completes)
3. Backtests → **Run calibration** → wait 10–20 min on 4 GB RAM

---

## Day-2 operations

### Update after git push

```bash
cd /opt/downpour
git pull
cd deploy/hetzner
docker compose up -d --build
```

### View logs

```bash
docker compose logs -f api
docker compose logs -f caddy
```

### Restart

```bash
docker compose restart api
```

### Data persistence

SQLite DB and parquet cache live in Docker volume `downpour-data`. Survives restarts and redeploys.

### Backup (optional)

```bash
docker compose exec api tar czf - /app/data > ~/downpour-backup-$(date +%F).tar.gz
```

---

## Optional: GitHub Actions auto-deploy

Add secrets to GitHub repo → **Settings** → **Secrets**:

- `HETZNER_HOST` — server IP
- `HETZNER_SSH_KEY` — private SSH key

Create `.github/workflows/deploy-hetzner.yml` (see repo if added later) to run `git pull && docker compose up -d --build` on push to `main`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CORS error in browser | Check `ALLOWED_ORIGINS` includes exact Vercel URL, restart API |
| 502 from Caddy | `docker compose logs api` — API may still be starting |
| Scan slow | Normal first time; 4 GB RAM handles 5 pairs well |
| SSL fails | DNS not propagated yet; wait 15 min, check `DOMAIN` in `.env` |
| Binance errors | EU region is fine; do **not** use US datacenter |

---

## Cost summary

| Service | Cost |
|---------|------|
| Hetzner CX22 | ~€4–6/mo |
| Domain | ~€1/mo (optional first year deals) |
| Vercel (frontend) | Free |
| **Total** | **~€5–7/mo** |

Compare: Render Starter $7 with 512 MB RAM vs Hetzner 4 GB for similar price.
