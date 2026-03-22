# OpenClaw Windows 11 Setup Guide

Complete guide to installing, configuring, and running OpenClaw on Windows 11.

---

## Table of Contents

- [Fix: PowerShell Execution Policy Error](#fix-powershell-execution-policy-error)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Post-Install Setup](#post-install-setup)
- [Gateway Configuration](#gateway-configuration)
- [Memory Search Setup](#memory-search-setup)
- [Channel Configuration](#channel-configuration)
- [Running OpenClaw as a Service](#running-openclaw-as-a-service)
- [Troubleshooting](#troubleshooting)
- [Recommended: WSL2 Setup](#recommended-wsl2-setup)

---

## Fix: PowerShell Execution Policy Error

If you see this error when running `openclaw setup`:

```
openclaw : File C:\Users\HP\AppData\Roaming\npm\openclaw.ps1 cannot be loaded because
running scripts is disabled on this system.
```

This is a Windows PowerShell security restriction. Fix it with one of these methods:

### Method 1: Change Execution Policy (Recommended)

Open PowerShell **as Administrator** (right-click > Run as Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run `openclaw setup` again normally.

### Method 2: Bypass for Current Session Only

If you don't want to change the policy permanently:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
openclaw setup
```

This only lasts for the current PowerShell window.

### Method 3: Call Node Directly

Skip the PowerShell wrapper script entirely:

```powershell
node "C:\Users\HP\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs" setup
```

### Method 4: Use Command Prompt Instead

Open **cmd.exe** (not PowerShell) and run:

```cmd
openclaw setup
```

The `.cmd` wrapper doesn't have the PowerShell execution policy restriction.

---

## Prerequisites

| Requirement | Minimum Version | Check Command |
|---|---|---|
| Windows | 10 (1903+) or 11 64-bit | `winver` |
| Node.js | 22+ | `node --version` |
| npm | 10+ | `npm --version` |
| Git | Any recent | `git --version` |
| PowerShell | 5.1+ | `$PSVersionTable.PSVersion` |

### Install Node.js 22+

If Node.js is missing or outdated:

```powershell
# Via winget (built into Windows 11)
winget install OpenJS.NodeJS.LTS

# Or via Chocolatey
choco install nodejs-lts

# Or via Scoop
scoop install nodejs-lts
```

After installing, close and reopen your terminal, then verify:

```powershell
node --version   # Should show v22.x or higher
npm --version    # Should show v10.x or higher
```

---

## Installation Methods

### Method A: npm Global Install (Standard)

```powershell
npm install -g openclaw@latest
```

### Method B: PowerShell One-Liner

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

### Verify Installation

```powershell
openclaw --version
# Should output: OpenClaw 2026.3.x
```

---

## Post-Install Setup

### Step 1: Run Initial Setup

```powershell
openclaw setup
```

This creates the OpenClaw home directory at `C:\Users\<YourName>\.openclaw\` with:

- `openclaw.json` — main configuration file
- `workspace/` — skills, prompts, and memory files
- `credentials/` — API keys and tokens
- `agents/` — session storage
- `memory/` — memory index

### Step 2: Run Doctor

```powershell
openclaw doctor --fix
```

This checks your installation and applies any needed fixes. Run it after every upgrade too.

### Step 3: Configure Your AI Provider

OpenClaw needs at least one LLM provider to function. There are two ways to set this up:

**Method A: Config set (quickest)**

Set API keys directly in the config using the correct path `models.providers.<provider>.apiKey`:

```powershell
# Google Gemini
openclaw config set models.providers.google.apiKey "your-gemini-key"

# Anthropic (Claude)
openclaw config set models.providers.anthropic.apiKey "sk-ant-your-key"

# OpenAI
openclaw config set models.providers.openai.apiKey "sk-your-key"
```

**Method B: `.env` file (recommended for gateway service)**

If the gateway runs as a Scheduled Task or daemon, it may not see user environment variables. Add keys to `~\.openclaw\.env` instead:

```powershell
notepad C:\Users\HP\.openclaw\.env
```

Add one key per line:

```
ANTHROPIC_API_KEY=sk-ant-your-key
OPENAI_API_KEY=sk-your-key
GEMINI_API_KEY=your-gemini-key
```

Save and restart the gateway: `openclaw gateway stop` then `openclaw gateway start`.

**Method C: Interactive wizard**

```powershell
openclaw onboard
```

This walks you through configuring credentials, channels, and agent defaults.

> **Note:** The config path is `models.providers.*`, not `providers.*`. Using just `providers.*` will give a validation error.

### Step 4: Set Default Models

```powershell
openclaw configure
```

Follow the interactive wizard to select your default models. You can also set them directly:

```powershell
openclaw config set agents.defaults.models '["claude-4-sonnet", "gpt-4o", "gemini-2.5-pro"]'
```

---

## Gateway Configuration

The Gateway is the central hub that routes messages between you and your AI agent.

### Start the Gateway

```powershell
openclaw gateway
```

The Gateway runs on `ws://127.0.0.1:18789` by default.

### Install as a Windows Service

To have the Gateway start automatically with Windows:

```powershell
openclaw gateway install
openclaw gateway start
```

### Check Gateway Status

```powershell
openclaw gateway status
openclaw health
```

### Configure Gateway Mode

```powershell
openclaw config set gateway.mode "local"
```

---

## Memory Search Setup

Memory search gives your agent the ability to recall past conversations and stored knowledge. The `openclaw doctor` output you saw indicates it needs an embedding provider.

### Option 1: Use an API Key (Easiest)

If you already set an API key for OpenAI, Gemini, Voyage, or Mistral, memory search will auto-detect it:

```powershell
# Verify with:
openclaw memory status --deep
```

### Option 2: Configure a Specific Provider

```powershell
openclaw config set agents.defaults.memorySearch.provider "openai"
# or "gemini", "voyage", "mistral", "ollama"
```

### Option 3: Local Embeddings (Offline/Private)

For fully local operation using a GGUF model:

```powershell
openclaw config set agents.defaults.memorySearch.provider "local"
```

OpenClaw will auto-download a suitable embedding model on first use.

### Option 4: Disable Memory Search

If you don't need it:

```powershell
openclaw config set agents.defaults.memorySearch.enabled false
```

### Memory Search Configuration Options

Fine-tune how memory search works:

```powershell
# Hybrid search weights (BM25 + vector)
openclaw config set agents.defaults.memorySearch.vectorWeight 0.7
openclaw config set agents.defaults.memorySearch.textWeight 0.3

# Add extra knowledge paths
openclaw config set agents.defaults.memorySearch.extraPaths '["C:\\Users\\HP\\Documents\\notes"]'

# Temporal decay (recent memories rank higher)
openclaw config set agents.defaults.memorySearch.halfLifeDays 30
```

---

## Channel Configuration

Channels are how you communicate with your OpenClaw agent. Set up one or more:

### WhatsApp

```powershell
openclaw channels login whatsapp
```

Scan the QR code with WhatsApp on your phone. Your agent becomes reachable via WhatsApp.

### Telegram

```powershell
openclaw config set channels.telegram.botToken "your-telegram-bot-token"
```

Create a bot via [@BotFather](https://t.me/BotFather) on Telegram first.

### Discord

```powershell
openclaw config set channels.discord.botToken "your-discord-bot-token"
```

Create a bot at the [Discord Developer Portal](https://discord.com/developers/applications).

### Slack

```powershell
openclaw config set channels.slack.botToken "xoxb-your-slack-bot-token"
openclaw config set channels.slack.appToken "xapp-your-slack-app-token"
```

### iMessage (Windows via Bridge)

iMessage integration requires macOS or a macOS bridge. Not natively available on Windows.

### Terminal / CLI Chat

For direct terminal interaction:

```powershell
openclaw tui
```

Once the TUI opens, **type `/deliver on` first** — this enables message delivery to your AI provider (it's off by default). Then type your message and hit Enter.

Alternatively, use the browser-based dashboard:

```powershell
openclaw dashboard
```

**Key TUI commands:**

| Command | What It Does |
|---|---|
| `/deliver on` | Enable AI responses (do this first!) |
| `/model` | Pick which AI model to use |
| `/agent` | List or switch agents |
| `/session` | Manage sessions |
| `/new` | Start a fresh session |
| `/help` | See all commands |
| `Ctrl+L` | Open model picker |
| `Ctrl+D` | Exit the TUI |

---

## Running OpenClaw as a Service

### Install and Start the Gateway Service

```powershell
# Install the service
openclaw gateway install

# Start it
openclaw gateway start

# Check status
openclaw gateway status

# Stop it
openclaw gateway stop

# Restart
openclaw gateway restart
```

### Auto-Start on Login

If the service installer doesn't work on your Windows version, create a scheduled task:

```powershell
# Create a startup task (run in Admin PowerShell)
$action = New-ScheduledTaskAction -Execute "node" -Argument "C:\Users\HP\AppData\Roaming\npm\node_modules\openclaw\openclaw.mjs gateway"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "OpenClaw Gateway" -Description "OpenClaw AI Gateway"
```

---

## Troubleshooting

### "running scripts is disabled on this system"

See [Fix: PowerShell Execution Policy Error](#fix-powershell-execution-policy-error) above.

### "Gateway not running" / "Gateway service not installed"

```powershell
openclaw gateway install
openclaw gateway start
```

### "No embedding provider is configured"

Set at least one API key or configure a local embedding provider. See [Memory Search Setup](#memory-search-setup).

### Node.js Version Too Old

```powershell
# Check version
node --version

# Upgrade via winget
winget upgrade OpenJS.NodeJS.LTS
```

### PATH Issues

If `openclaw` isn't found after install:

```powershell
# Check if npm global bin is in PATH
npm config get prefix

# Add it to PATH (replace with your actual path)
$npmPath = (npm config get prefix)
[System.Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$npmPath", "User")
```

Restart your terminal after changing PATH.

### Port 18789 Already in Use

```powershell
# Find what's using the port
netstat -ano | findstr :18789

# Kill the process (replace PID with the actual number)
taskkill /PID <PID> /F
```

### Reset Configuration

If something goes wrong with your config:

```powershell
# Back up current config
copy C:\Users\HP\.openclaw\openclaw.json C:\Users\HP\.openclaw\openclaw.json.bak

# Re-run setup
openclaw setup
openclaw doctor --fix
```

### Firewall Blocking Gateway

If the Gateway can't accept connections:

1. Open **Windows Defender Firewall**
2. Click **Allow an app or feature through Windows Defender Firewall**
3. Click **Change settings** > **Allow another app**
4. Browse to your Node.js executable (usually `C:\Program Files\nodejs\node.exe`)
5. Check both **Private** and **Public**

---

## Recommended: WSL2 Setup

For the best experience on Windows, consider using WSL2 (Windows Subsystem for Linux). It provides full Linux compatibility and avoids many Windows-specific issues.

### Install WSL2

```powershell
# In Admin PowerShell
wsl --install
```

Restart your computer when prompted.

### Enable systemd in WSL

Edit `/etc/wsl.conf` inside your WSL distribution:

```bash
sudo nano /etc/wsl.conf
```

Add:

```ini
[boot]
systemd=true
```

Restart WSL:

```powershell
wsl --shutdown
wsl
```

### Install OpenClaw in WSL

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw setup
openclaw doctor --fix
```

WSL2 gives you access to the full Linux toolchain while still running on Windows 11.

---

## Quick Reference

| Task | Command |
|---|---|
| Initial setup | `openclaw setup` |
| Health check | `openclaw doctor --fix` |
| Configure provider | `openclaw configure --section model` |
| Start gateway | `openclaw gateway` |
| Install service | `openclaw gateway install` |
| Check memory | `openclaw memory status --deep` |
| Link WhatsApp | `openclaw channels login whatsapp` |
| Chat in terminal | `openclaw tui` (then `/deliver on`) |
| Dashboard UI | `openclaw dashboard` |
| View config | `openclaw config get .` |
| Check status | `openclaw status` |
| View logs | `openclaw logs --follow` |
| Upgrade | `npm install -g openclaw@latest` |
