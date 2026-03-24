# Personal X Assistant (Scheduled Poster)

This project runs a personal assistant that posts to X at configured times.

## What it does

- Reads post templates from `posts.txt` (or from `ASSISTANT_POSTS_JSON`).
- Schedules posts using local timezone + HH:MM times.
- Posts to X using API v2 (`POST /2/tweets`) in **live** mode.
- Defaults to **dry-run** mode so you can test safely first.

## Quick start

1. Install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   - Start with `ASSISTANT_POST_MODE=dry-run`.
   - Add your X credentials before switching to `live`.
   - Set your schedule with comma-separated `HH:MM` values.

3. Run:

   ```bash
   python3 main.py
   ```

## Configuration

Key variables:

- `ASSISTANT_POST_MODE`: `dry-run` or `live`
- `ASSISTANT_TIMEZONE`: e.g. `UTC`, `America/New_York`
- `ASSISTANT_SCHEDULE_TIMES`: e.g. `09:00,13:00,18:00`
- `ASSISTANT_POSTS_FILE`: path to text file with one post per line
- `ASSISTANT_POSTS_JSON`: optional JSON array of post strings
- `ASSISTANT_POST_SELECTION`: `sequential` or `random`
- `ASSISTANT_STATE_FILE`: local state file (for sequential cursor)
- `ASSISTANT_MAX_POST_LENGTH`: default 280
- `X_API_KEY`, `X_API_KEY_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`

Optional:

- `ASSISTANT_RUN_ONCE_ON_START=true` to immediately run one post attempt at startup.
- `ASSISTANT_EXIT_AFTER_RUN_ONCE=true` to exit immediately after that startup run.

## Notes

- If a generated post is longer than the configured max length, it is truncated.
- Template placeholders supported in post text:
  - `{date}` -> `YYYY-MM-DD`
  - `{datetime}` -> `YYYY-MM-DD HH:MM`
