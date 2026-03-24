# VPS Reddit Setup Status Report

**Generated:** 2026-03-24  
**VPS:** flipblankreact.xyz (176.123.2.208)

---

## VPS Overview

| Property | Value |
|----------|-------|
| OS | Ubuntu 24.04 |
| CPU | 1 Core |
| RAM | 1.5 GB |
| Disk | 10 GB |
| Uptime | 12 days 4:22:57 |
| Bandwidth | IN: 2.12 GB / OUT: 834.3 MB |

---

## Running Services Found

| Port | Service | Status |
|------|---------|--------|
| 80 | GSCF Store Admin Dashboard (nginx → Node.js/Express + MongoDB) | Running |
| 443 / 3000 | MoodMate AI Wellness App (PWA, Gemini AI) | Running |
| 22 | SSH | Running (auth failed) |
| 5432 | PostgreSQL | Bound to localhost only |
| 3306 | MySQL | Bound to localhost only |
| 27017 | MongoDB | Bound to localhost only |
| 6379 | Redis | Bound to localhost only |

---

## Reddit Posting System Status

**Result: NO Reddit automation system found on this VPS.**

After comprehensive investigation:

- No Reddit scheduler or posting script found via any accessible web interface
- No database with Reddit post queue accessible externally
- All database ports (MongoDB, PostgreSQL, MySQL, Redis) are firewalled from external access
- SSH authentication failed — the password visible in the VPS panel screenshot did not authenticate

The VPS is currently hosting:
1. **GSCF Store** — a Telegram-based e-commerce admin dashboard (0 products, 0 orders, 1 seller registered)
2. **MoodMate** — an AI mood-tracking PWA using Google Gemini

Neither of these apps contains a Reddit posting/scheduling system.

---

## GSCF Store Data (from API)

- **Admin user:** `admin` (superadmin), created 2026-03-15
- **Sellers:** 1 (GSCF_SUPPORT, Telegram ID: 7800993199)
- **Products:** 0 items in database
- **Orders:** 0 orders
- **Revenue:** $0

---

## What You Need To Do

To check the Reddit post database and scheduler, you need **SSH access** to the server. Options:

1. **Reset the SSH password** from the VPS control panel (the one in the screenshot may have changed)
2. **Add an SSH key** via the VPS panel's "SSH Keys" section and share the public key
3. **Use the VPS console** from the control panel web UI to directly inspect running processes and databases

Once SSH access is established, run:

```bash
# Check running processes
ps aux | grep -E "(reddit|python|node|pm2)"

# Check PM2 processes (common Node.js process manager)
pm2 list

# Check all running Docker containers
docker ps -a

# Check MongoDB databases
mongo --eval "db.adminCommand('listDatabases')"

# Check for Reddit-related files
find / -name "*.py" -o -name "*.js" | xargs grep -l "reddit" 2>/dev/null | head -20
```

---

## Next Steps for Reddit Scheduler

To build a Reddit post database + scheduler on this VPS, the plan would be:

1. **Database**: Use the existing MongoDB instance to store posts with fields: `title`, `content`, `subreddit`, `scheduled_at`, `status` (pending/posted/failed), `reddit_url`
2. **Scheduler**: A Python/Node.js cron job that queries pending posts and submits them via Reddit API (PRAW/snoowrap)
3. **Admin UI**: A dashboard to add posts, set schedules, and view posting history
4. **Post Queue**: Pre-load 30+ days of content for hands-off operation
