# OpenClawWorks

Practical guides for setting up and monetizing [OpenClaw](https://openclaw.ai) — your open-source personal AI assistant.

## Guides

### [Windows 11 Setup Guide](WINDOWS-SETUP.md)

Complete walkthrough for getting OpenClaw running on Windows 11, including:

- Fixing the PowerShell execution policy error
- Prerequisites and installation
- Gateway, memory search, and channel configuration
- Running OpenClaw as a Windows service
- Troubleshooting common issues
- WSL2 setup (recommended for advanced use)

### [Social Media Content Playbook](SOCIAL-MEDIA-PLAYBOOK.md)

Step-by-step guide to using OpenClaw as your AI content manager:

- Complete setup walkthrough (provider, gateway, memory)
- Building your brand memory file so content stays on-voice
- Content generation for X (Twitter), LinkedIn, and Facebook
- Ready-to-use prompt templates for every post type
- Batch content production workflow (1 week of content in 1-2 hours)
- Scheduling tools (free and paid)
- Growth tactics for the first 90 days
- Monetization: sponsorships, products, affiliate, freelance clients

### [Monetization Guide](MONETIZATION-GUIDE.md)

Every practical way to turn OpenClaw into income:

- Freelance development and coding
- Content creation and copywriting
- AI automation services for businesses
- Building and selling AI-powered products
- Consulting and AI strategy
- Data analysis, research, and more
- Cost optimization tips
- Stacking multiple income streams

## Quick Start (Windows 11)

```powershell
# 1. Fix PowerShell execution policy (run as Admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Run setup
openclaw setup

# 3. Fix any issues
openclaw doctor --fix

# 4. Configure your AI provider
openclaw configure --section model

# 5. Start the gateway
openclaw gateway

# 6. Start chatting (terminal UI)
openclaw tui
# Then type: /deliver on
```

## Contributing to OpenClaw

OpenClaw is open source and welcomes community contributions. Here's how to get involved:

### Report Issues and Fixes

- **GitHub Issues**: [github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues) — report bugs, request features, or help triage
- **Pull Requests**: [github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls) — submit fixes and improvements
- **Discussions**: [github.com/openclaw/openclaw/discussions](https://github.com/openclaw/openclaw/discussions) — ask questions, share ideas

### Contribute Skills and Plugins

- Browse community skills on [ClawHub](https://clawhub.openclaw.ai)
- Publish your own: `openclaw clawhub publish`
- Test skills locally: `openclaw skill test <path>`

### Areas Where Help Is Needed

- **Windows support** — testing, bug reports, and fixes for Windows-specific issues
- **Documentation** — guides, tutorials, and translations
- **Skills** — build and share reusable skills
- **Channel adapters** — improve or add messaging platform integrations
- **Security audits** — run `openclaw security check` and report findings

### This Repo (OpenClawWorks)

This repo contains community-written guides. Contributions welcome — if you find an error or want to add a guide, open a PR.

## Links

- [OpenClaw Official Site](https://openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw CLI Reference](https://docs.openclaw.ai/cli)
- [ClawHub (Skills Marketplace)](https://clawhub.openclaw.ai)
