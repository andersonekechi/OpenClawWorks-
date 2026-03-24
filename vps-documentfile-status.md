# VPS Status Report — documentfile.shop (217.156.64.90)

**Generated:** 2026-03-24  
**VPS:** documentfile.shop / 217.156.64.90  
**Uptime:** 22 days 08:32:11

---

## VPS Overview

| Property | Value |
|----------|-------|
| OS | Ubuntu 24.04 |
| CPU | 1 Core (load: 0.00) |
| RAM | 1.4 GB total / 438 MB used |
| Disk | 8.7 GB total / 3.7 GB used (43%) |
| Bandwidth | IN: 2.61 GB / OUT: 2.36 GB |

---

## Running Services

| Service | Status | Details |
|---------|--------|---------|
| **bacehelpr.service** | ACTIVE / RUNNING | BaceHelpr Reddit Crypto Scanner Telegram Bot |
| Apache2 | Running | Ports 80 + 443 (serving documentfile.shop) |
| SSH | Running | Port 22 |

---

## BaceHelpr Bot — Full Status

The bot is **live and healthy** — polling Telegram every 10 seconds continuously.

### What It Does

1. **Scans Reddit** every 12 hours across 13 crypto subreddits (Solana, Ethereum, DeFi, web3, NFT, etc.)
2. **Categorizes posts** by: Investors/Jobs, Newbies Needing Help, Devs Stuck on Problems, Building/Collabs
3. **Generates tweet threads** ("articles") — ready-to-post Twitter/X content from Reddit signal
4. **Telegram bot interface** — you open it in Telegram, browse posts by category, click any post to get the ready-to-copy tweet, and mark it as posted

### Bot Access

- **Telegram token:** `8703453273:AAG_Hcc_eJDBDIyr0Q_yIQuwQMiBlj9raM8`
- **Your Telegram ID:** `7800993199`
- **Admin IDs:** `7800993199`, `6162101530`

---

## Database Status — bacehelpr.db (SQLite, 1.2 MB)

### Summary

| Metric | Count |
|--------|-------|
| **Total Reddit posts scanned** | 509 |
| **Posts NOT YET used (acted_on=0)** | **488** |
| **Posts already used** | 21 |
| **Total tweet threads (articles)** | 122 |
| **Article threads NOT YET used** | **122** |
| **Date range of scans** | Mar 8 – Mar 24, 2026 |

### Content by Category (Unposted)

| Category | Total | Not Posted |
|----------|-------|------------|
| Building & Collabs | 210 | **207** |
| Investors & Jobs | 120 | **112** |
| Newbies Need Help | 103 | **99** |
| Devs Stuck on Problems | 76 | **70** |

### Content Supply Estimate

At moderate usage rates:
- **488 unposted posts** → ~122 days (17 weeks) of content at 4/day
- **122 unposted article threads** → ~61 days at 2/day
- **New posts added daily** (10-24 per day from Reddit scans) → keeps growing automatically

### Content Coverage by Subreddit

| Subreddit | Posts |
|-----------|-------|
| r/defi | 78 |
| r/solana | 78 |
| r/ethdev | 62 |
| r/cryptocurrency | 59 |
| r/CryptoTechnology | 55 |
| r/CoinBase | 47 |
| r/web3 | 36 |
| r/ethereum | 34 |
| r/solanadev | 27 |
| r/NFT | 21 |

### Top Unposted Posts (Highest Match Score)

| Category | Score | Post Title | Subreddit |
|----------|-------|------------|-----------|
| investor | 17.3 | Active Accelerators & Growth Programs For Solana Builders | r/solana |
| building | 16.1 | I built a free tool that makes blockchain transactions human-readable | r/ethereum |
| building | 14.5 | Blockchain Payroll Platform | r/defi |
| newbie_help | 14.0 | Looking to earn some crypto as a beginner — where do I start | r/ethdev |
| building | 13.7 | I built a non-custodial HD wallet Chrome extension for Ethereum | r/web3 |
| stuck_dev | 13.6 | Phantom on iPhone not showing Solana Devnet balance | r/solana |
| investor | 13.5 | Web3 developer wanted | r/ethdev |
| investor | 12.5 | [HIRING] Marketing Cofounder — Equity Only — DeFi Super-App | r/ethdev |

---

## How to Use the Bot

Open your Telegram bot and:
1. Tap a category (e.g. "Building & Collabs")
2. Browse the list of Reddit posts with dates
3. Tap any post to get the ready-to-copy tweet text
4. Copy → paste to X/Twitter → tap "Mark as Posted"
5. Tap "Articles (Long Threads)" for multi-tweet threads

The bot tracks what you've posted so you never repeat content.

---

## Conclusion

**Everything is working great.** The VPS is healthy, the bot has been running for 22 days, and the database is loaded with content:

- **488 individual posts** ready to turn into tweets
- **122 full article threads** ready to post
- **Daily auto-scans** continuously adding fresh content
- At current pace, you have **2-4 months of content** banked up

