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

# 6. Start chatting
openclaw chat
```

## Links

- [OpenClaw Official Site](https://openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Documentation](https://openclaws.io)
