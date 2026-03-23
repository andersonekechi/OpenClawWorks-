# Social Media Content Creation Playbook

Step-by-step guide to using OpenClaw as your AI content manager for X (Twitter), LinkedIn, and Facebook. From zero to a running content machine.

---

## Table of Contents

- [Step 0: Where You Are Now](#step-0-where-you-are-now)
- [Step 1: Run Doctor and Finish Setup](#step-1-run-doctor-and-finish-setup)
- [Step 2: Set Up Your AI Provider](#step-2-set-up-your-ai-provider)
- [Step 3: Configure OpenClaw for Content Creation](#step-3-configure-openclaw-for-content-creation)
- [Step 4: Build Your Brand Memory File](#step-4-build-your-brand-memory-file)
- [Step 5: Generate Content for X (Twitter)](#step-5-generate-content-for-x-twitter)
- [Step 6: Generate Content for LinkedIn](#step-6-generate-content-for-linkedin)
- [Step 7: Generate Content for Facebook](#step-7-generate-content-for-facebook)
- [Step 8: Batch Content Production Workflow](#step-8-batch-content-production-workflow)
- [Step 9: Scheduling and Posting Tools](#step-9-scheduling-and-posting-tools)
- [Step 10: Growing and Monetizing Your Audience](#step-10-growing-and-monetizing-your-audience)
- [Prompt Templates Library](#prompt-templates-library)
- [Weekly Content Calendar Template](#weekly-content-calendar-template)
- [Monetization Paths for Social Media](#monetization-paths-for-social-media)

---

## Step 0: Where You Are Now

You've completed:
- [x] OpenClaw installed on Windows 11
- [x] `openclaw setup` ran successfully
- [ ] `openclaw doctor --fix` (do this next)
- [ ] AI provider configured
- [ ] Gateway running

Let's finish the setup, then get straight into content creation.

---

## Step 1: Run Doctor and Finish Setup

**Yes, run this now:**

```powershell
openclaw doctor --fix
```

This will:
- Check your installation is healthy
- Fix any configuration issues
- Set up missing components

After it finishes, note any warnings. The memory search warning is fine for now — we'll configure it in Step 3.

Then run:

```powershell
openclaw doctor
```

Make sure there are no critical errors. Warnings about memory search or gateway service are OK — we'll handle those.

---

## Step 2: Set Up Your AI Provider

You need an API key from at least one AI provider. For content creation, these are the best options:

### Option A: Google Gemini — Good Free Tier to Start

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API Key** > **Create API key**
4. Copy the key
5. Run:

```powershell
openclaw config set models.providers.google.apiKey "paste-your-key-here"
```

### Option B: OpenAI (GPT-4o) — Best for Natural-Sounding Social Content

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** > **Create new secret key**
4. Copy the key (starts with `sk-`)
5. Run:

```powershell
openclaw config set models.providers.openai.apiKey "sk-paste-your-key-here"
```

### Option C: Anthropic (Claude) — Best for Thoughtful, Long-Form Content

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to **API Keys** > **Create Key**
4. Copy the key (starts with `sk-ant-`)
5. Run:

```powershell
openclaw config set models.providers.anthropic.apiKey "sk-ant-paste-your-key-here"
```

### Alternative: `.env` File or Interactive Setup

If the gateway runs as a service/scheduled task, add keys to `~\.openclaw\.env`:

```powershell
notepad C:\Users\HP\.openclaw\.env
```

Add one key per line (e.g., `ANTHROPIC_API_KEY=sk-ant-your-key`), save, then restart the gateway.

Or use the interactive wizard:

```powershell
openclaw onboard
```

> **Note:** The config path is `models.providers.*`, not `providers.*`. Using just `providers.*` gives a validation error.

### Set Your Default Model

Use the `models set` command with the `provider/model` format:

```powershell
# Google Gemini (free tier available)
openclaw models set google/gemini-2.5-pro

# Or OpenAI
openclaw models set openai/gpt-4o

# Or Anthropic
openclaw models set anthropic/claude-4-sonnet
```

You must include the provider prefix (e.g., `google/`, `openai/`, `anthropic/`). Restart the gateway after changing: `openclaw gateway stop && openclaw gateway start`.

---

## Step 3: Configure OpenClaw for Content Creation

### Start the Gateway

```powershell
openclaw gateway
```

Leave this terminal running. Open a **new** terminal for the next commands.

### Enable Browser Tool (for Research)

```powershell
openclaw config set agents.defaults.tools '["browser", "shell"]'
```

### Enable Memory Search

This lets OpenClaw remember your brand voice, past content, and audience insights:

```powershell
openclaw config set agents.defaults.memorySearch.enabled true
```

If you set up an API key in Step 2, memory search will auto-detect your embedding provider.

### Verify Everything Works

```powershell
openclaw doctor
openclaw health
```

Then test with a quick chat:

```powershell
openclaw tui
```

Once the TUI opens, **type `/deliver on` first** — this enables message delivery to your AI provider (it's off by default). Then type your message and hit Enter.

Alternatively, open the browser-based dashboard:

```powershell
openclaw dashboard
```

**Key TUI commands:**
- `/deliver on` — enable AI responses (do this first!)
- `/model` — pick which AI model to use
- `/help` — see all available commands
- `/new` — start a fresh session
- `Ctrl+D` — exit the TUI

If you get a response from the AI, you're ready.

---

## Step 4: Build Your Brand Memory File

This is the most important step. OpenClaw's persistent memory means it will learn and remember your brand voice. Set this up once and every piece of content it creates will be consistent.

Open this file in Notepad or any editor:

```
C:\Users\HP\.openclaw\workspace\MEMORY.md
```

Or create it:

```powershell
notepad C:\Users\HP\.openclaw\workspace\MEMORY.md
```

Paste and customize this template:

```markdown
# My Brand

## Who I Am
- Name: [Your Name]
- Title/Role: [e.g., AI Enthusiast, Tech Entrepreneur, Digital Marketer]
- Niche: [e.g., AI tools, productivity, tech for beginners]
- Location: [City/Country — helps with local relevance]

## Brand Voice
- Tone: [e.g., Casual but knowledgeable, like explaining to a smart friend]
- Style: [e.g., Short punchy sentences. Use analogies. No corporate speak.]
- Personality: [e.g., Optimistic, practical, slightly humorous]
- Avoid: [e.g., Jargon without explanation, clickbait, negativity]

## Target Audience
- Who: [e.g., Young professionals 22-35 who want to use AI to work smarter]
- Pain points: [e.g., Overwhelmed by AI tools, don't know where to start]
- What they want: [e.g., Simple actionable tips, tool recommendations, real results]

## Content Pillars (Main Topics)
1. [e.g., AI tools and how to use them]
2. [e.g., Productivity and automation tips]
3. [e.g., Making money with tech skills]
4. [e.g., Behind-the-scenes of my journey]

## Platform-Specific Notes

### X (Twitter)
- Max 280 characters per tweet (threads for longer content)
- Use hooks in the first line
- Hashtags: 1-2 max
- Best times: 8-10 AM, 12-1 PM, 5-6 PM
- Reply to others in my niche daily

### LinkedIn
- Professional but not stiff
- Share lessons, not just wins
- Use line breaks for readability
- Stories and personal experiences do well
- Tag relevant people and companies
- Best times: Tuesday-Thursday, 8-10 AM

### Facebook
- More personal, community-focused
- Longer posts OK
- Questions drive engagement
- Share behind-the-scenes content
- Best times: 1-4 PM

## Hashtags I Use
- X: #AI #Productivity #TechTips #OpenClaw #BuildInPublic
- LinkedIn: #ArtificialIntelligence #Productivity #FutureOfWork #TechCareers
- Facebook: varies by post

## Content I've Posted (Recent)
- [Update this as you post — OpenClaw will remember and avoid repeating]

## Competitors / Accounts I Admire
- [List 3-5 accounts in your niche you like the style of]
```

Save the file. OpenClaw will index it and use it as context for all content generation.

---

## Step 5: Generate Content for X (Twitter)

Open a chat session:

```powershell
openclaw tui
```

Type `/deliver on` first to enable AI responses, then start prompting. Or use `openclaw dashboard` for a browser-based UI.

### Generate Individual Tweets

Tell OpenClaw exactly what you want:

```
Write 5 tweets about using AI tools to save time at work.
Make them punchy, no more than 250 characters each.
Include a hook in the first line of each.
Match my brand voice from my memory file.
```

### Generate Tweet Threads

```
Write a Twitter thread (8 tweets) about how I set up an AI assistant
on my Windows laptop and what it can do.
First tweet should be a strong hook.
Last tweet should be a call to action.
Keep my brand voice.
```

### Generate Engagement Tweets

```
Write 5 reply-style tweets I can use to engage with popular tech
accounts. They should be insightful, not generic. Topics: AI
productivity, automation, working smarter.
```

### Generate a Daily Tweet Batch

```
Create my tweets for today. I need:
- 1 value tweet (teaching something useful)
- 1 hot take or opinion
- 1 engagement question
- 1 personal story or observation
- 1 promotional tweet about OpenClaw

All matching my brand voice. Keep them under 270 characters.
```

---

## Step 6: Generate Content for LinkedIn

### Professional Posts

```
Write a LinkedIn post about how AI is changing the way solo
entrepreneurs work. Use a personal storytelling angle — talk about
how I set up OpenClaw on my Windows laptop this week.
Include line breaks for readability. End with a question to drive
comments. 150-250 words.
```

### Carousel Scripts (for PDF/Image Carousels)

```
Write a 10-slide LinkedIn carousel script about "10 Ways AI Saves
You Time Every Day."
Each slide should have:
- A bold headline (5-8 words)
- 2-3 lines of supporting text
- A visual suggestion

Slide 1 = hook, Slide 10 = CTA.
```

### Article Ideas

```
Give me 10 LinkedIn article ideas in my niche that would position
me as a thought leader. For each, give me the title, a 2-sentence
hook, and 3 key points to cover.
```

---

## Step 7: Generate Content for Facebook

### Community Posts

```
Write a Facebook post for my page about getting started with AI
tools as a complete beginner. Make it friendly and approachable.
Ask a question at the end to encourage comments.
Use emojis sparingly. 100-200 words.
```

### Group Content

```
Write 3 Facebook group posts I can share in tech/AI groups:
1. A question that starts a discussion about AI tools
2. A helpful tip post with a personal story
3. A "what would you do" scenario about AI automation

Make them feel genuine, not promotional.
```

### Facebook Reels/Video Scripts

```
Write a 60-second video script about "I let AI manage my social
media for a week — here's what happened."
Include: hook (first 3 seconds), story, results, CTA.
Keep it conversational like I'm talking to a friend.
```

---

## Step 8: Batch Content Production Workflow

This is how you produce a full week of content in one sitting.

### The Sunday Session (1-2 Hours)

Open OpenClaw:

```powershell
openclaw tui
```

Then run through this sequence:

**1. Generate the week's content calendar:**

```
Create my social media content calendar for this week
(Monday through Friday).

For each day, generate:
- 3 tweets (1 value, 1 engagement, 1 personal)
- 1 LinkedIn post (alternating between short post, story, and carousel script)
- 1 Facebook post (alternating between tip, question, and behind-the-scenes)

My content pillars are: AI tools, productivity, making money with tech, my journey.
Match my brand voice from memory. Make sure nothing repeats themes from last week.
```

**2. Review and edit:** Read through everything. Keep what's good, ask OpenClaw to rewrite anything that doesn't feel right:

```
Rewrite Tuesday's LinkedIn post — make it more personal and less
generic. Add a specific example.
```

**3. Generate visual suggestions:**

```
For each post this week, suggest what image or graphic I should
pair with it. Be specific — describe the visual, text overlay,
and colors.
```

**4. Schedule everything** (see Step 9 for tools).

### Daily Touch-Ups (15 Minutes)

```
Write 3 replies I can post on trending tweets in the AI/tech space
today. Make them insightful and on-brand.
```

---

## Step 9: Posting to X (Twitter) and Other Platforms

### Important: X/Twitter Is Not a Native Channel

OpenClaw supports many chat channels (Telegram, Discord, WhatsApp, Slack, etc.) but **X/Twitter is not a built-in channel**. There are three ways to post to X:

**Method 1: Browser tool (OpenClaw controls your browser)**

OpenClaw can control a real browser, log into X.com, and post tweets directly:

```powershell
openclaw browser login
```

Navigate to X.com and log in. After that, you can instruct OpenClaw to post tweets through the browser during a TUI or agent session.

**Method 2: Telegram bot as your content pipeline**

If you already have a Telegram bot connected to OpenClaw, you can have it generate and deliver tweet drafts to you on Telegram. Then you copy-paste or use a scheduling tool to post to X.

Set up Telegram (if not already done):

```powershell
openclaw channels login telegram
```

**Method 3: Scheduling tools (recommended for consistency)**

Use a third-party tool to schedule and auto-post content that OpenClaw generates:

### Scheduling and Posting Tools

### Free Options

| Tool | Platforms | Free Tier |
|---|---|---|
| [Buffer](https://buffer.com) | X, LinkedIn, Facebook, Instagram | 3 channels, 10 posts/channel |
| [Later](https://later.com) | X, LinkedIn, Facebook, Instagram | 1 social set, 5 posts/profile |
| [Meta Business Suite](https://business.facebook.com) | Facebook, Instagram | Unlimited (Meta platforms only) |

### Paid Options (Worth It as You Scale)

| Tool | Platforms | Price | Best For |
|---|---|---|---|
| [Buffer](https://buffer.com) (paid) | All major | $6/month/channel | Simple scheduling |
| [Hootsuite](https://hootsuite.com) | All major | $99/month | Full management |
| [Typefully](https://typefully.com) | X (Twitter) | $12.50/month | Twitter-focused creators |
| [Shield](https://shieldapp.ai) | LinkedIn | $8/month | LinkedIn analytics |
| [Publer](https://publer.io) | All major | $12/month | Budget all-in-one |
| [Hypefury](https://hypefury.com) | X, LinkedIn | $19/month | Growth-focused |

### Recommended Starter Stack (Low Cost)

1. **Buffer Free** — schedule X + LinkedIn + Facebook (10 posts each)
2. **Meta Business Suite** — unlimited Facebook/Instagram scheduling
3. **Typefully Free** — draft and preview Twitter threads
4. Total cost: **$0/month** to start

### Workflow: OpenClaw to Scheduler

1. Generate content with `openclaw tui` (or `openclaw dashboard`)
2. Copy posts into your scheduler
3. Set dates and times
4. Let the scheduler auto-post

---

## Step 10: Growing and Monetizing Your Audience

### Growth Tactics (First 90 Days)

**X (Twitter):**
- Post 3-5 times daily
- Reply to 10+ accounts in your niche daily
- Join Twitter Spaces about AI/tech
- Retweet and quote-tweet with added value
- Run a weekly thread on a useful topic
- Target: 1,000 followers in 90 days

**LinkedIn:**
- Post once daily (weekdays)
- Comment thoughtfully on 5-10 posts daily
- Connect with 10-20 people in your niche daily
- Publish 1 long-form article per week
- Target: 500+ connections, 5,000+ impressions/week in 90 days

**Facebook:**
- Post 1-2 times daily on your page
- Share in 5-10 relevant groups daily
- Go live once a week
- Build an email list from Facebook
- Target: 500+ page followers in 90 days

### Use OpenClaw to Automate Growth Tasks

```
Write 10 thoughtful LinkedIn comments I can post on popular AI
industry posts today. Each should add value and include a subtle
reference to my experience.
```

```
Write 5 quote tweets for popular AI/tech tweets. Add genuine
insight, not just agreement. Make me look like someone worth
following.
```

---

## Prompt Templates Library

Copy-paste these into `openclaw tui` (or the dashboard) whenever you need them.

### Daily Tweet Generator

```
Today is [DAY]. Generate my daily tweets:

1. VALUE TWEET: Teach one useful thing about [TOPIC]. Under 250 chars.
   Hook first line. No hashtags in the tweet body.

2. ENGAGEMENT TWEET: Ask a question that my audience would want to
   answer about [TOPIC]. Under 200 chars.

3. PERSONAL TWEET: Share a quick observation or mini-story from my
   experience with [TOPIC]. Under 270 chars. Be authentic.

4. THREAD IDEA: Give me a 1-line thread concept I could expand later.

Match my brand voice.
```

### LinkedIn Post Generator

```
Write a LinkedIn post about [TOPIC].

Format:
- Hook line (stops the scroll)
- Short paragraphs (1-2 sentences each)
- Line breaks between paragraphs
- Personal story or example
- Key insight or lesson
- End with a question

Length: 150-300 words. Match my brand voice.
```

### Facebook Post Generator

```
Write a Facebook post about [TOPIC].

Make it:
- Conversational and friendly
- Include a personal angle
- End with a question or call to action
- Use 1-2 relevant emojis (no more)
- 100-200 words

Match my brand voice.
```

### Weekly Content Calendar Generator

```
Create my content calendar for next week ([DATES]).

For each day (Mon-Fri), generate:

X (Twitter):
- 1 value tweet
- 1 engagement tweet
- 1 personal/story tweet

LinkedIn:
- 1 post (vary format: story, listicle, hot take, carousel script, lesson)

Facebook:
- 1 post (vary: tip, question, behind-the-scenes, community)

My content pillars: [LIST YOUR PILLARS]
Avoid repeating themes from this week.
Match my brand voice from memory.
```

### Viral Hook Generator

```
Give me 20 hook lines for [PLATFORM] posts about [TOPIC].
Each hook should make someone stop scrolling.
Mix styles: curiosity, controversy, numbers, story, question.
```

### Hashtag Research

```
Research and give me the best hashtags for [TOPIC] on [PLATFORM].
Group them:
- High volume (1M+ posts)
- Medium volume (100K-1M)
- Niche (10K-100K — easier to rank)
Give me 5 in each category.
```

### Repurposing Content

```
Take this LinkedIn post and repurpose it into:
1. A Twitter thread (6-8 tweets)
2. A Facebook post
3. 3 standalone tweets
4. An Instagram caption

Here's the original post:
[PASTE POST]
```

---

## Weekly Content Calendar Template

Use this as a starting framework. Adjust based on what performs best.

| Day | X (Twitter) | LinkedIn | Facebook |
|---|---|---|---|
| **Monday** | Value tweet + Engagement question | Story post (weekend learning) | Motivational tip |
| **Tuesday** | How-to thread (5-8 tweets) | Listicle or framework | Behind-the-scenes |
| **Wednesday** | Hot take + Quote tweets | Carousel script | Community question |
| **Thursday** | Tool recommendation + Personal story | Lesson learned post | Helpful tip + resource |
| **Friday** | Week recap + Ask for opinions | Thought leadership piece | Fun/personal post |
| **Saturday** | Casual/personal tweet | — | — |
| **Sunday** | Plan next week's content | — | — |

---

## Monetization Paths for Social Media

Once you're posting consistently and growing, here's how to turn followers into income:

### Path 1: Brand Deals & Sponsorships (Fastest)

| Followers | Typical Rate per Post |
|---|---|
| 1,000–5,000 | $50–200 |
| 5,000–25,000 | $200–1,000 |
| 25,000–100,000 | $1,000–5,000 |
| 100,000+ | $5,000+ |

Where to find sponsors:
- [Passionfroot](https://passionfroot.me) — creator sponsorship marketplace
- [Collabstr](https://collabstr.com) — brand deal marketplace
- Direct outreach to brands in your niche
- Once you pass 5K followers, brands will DM you

### Path 2: Sell Your Own Products

- **Digital products**: eBooks, templates, checklists, prompt packs
- **Courses**: "How to use AI for [X]" — sell on Gumroad or Teachable
- **Consulting**: DM-based or Calendly booking from your bio
- **Community**: Paid Discord, Skool, or Circle community

Use OpenClaw to create these products too:

```
Create an outline for a $29 eBook called "The Beginner's Guide to
AI Productivity Tools." Include chapter titles, key topics per
chapter, and a compelling sales page description.
```

### Path 3: Affiliate Marketing

Promote tools you genuinely use and earn commissions:

| Program | Commission | Cookie Duration |
|---|---|---|
| OpenAI affiliate (if available) | Varies | Varies |
| Hosting (Vercel, DigitalOcean) | $25–200/signup | 30-90 days |
| SaaS tools (Buffer, Notion, etc.) | 20-30% recurring | 30-90 days |
| Course platforms (Teachable, etc.) | 30% | 30 days |
| Amazon Associates | 1-10% | 24 hours |

### Path 4: Freelance Clients from Social Media

Your content serves as your portfolio. When people see your AI/tech expertise, they'll hire you for:
- AI automation consulting
- Content creation for their business
- Social media management
- Technical implementation

Add to your bio: "DM me for [your service]" or link to a booking page.

### Path 5: X (Twitter) Premium Revenue Sharing

Once you're in the X Premium program (requires Premium subscription + enough impressions), you earn money directly from impressions on your posts. High-engagement content = passive income.

---

## Next Steps After This Guide

1. Run `openclaw doctor --fix` right now
2. Set up your AI provider (Step 2)
3. Start the gateway and test `openclaw tui`
4. Fill in your `MEMORY.md` brand file (Step 4) — this is critical
5. Generate your first week of content using the batch workflow (Step 8)
6. Sign up for Buffer (free) and schedule everything
7. Post consistently for 90 days
8. Once you have traction, layer on monetization (sponsorships, products, affiliate)

The key: **consistency beats perfection.** Post every day, engage with others, and let OpenClaw handle the heavy lifting of content creation while you focus on being authentic and building relationships.
