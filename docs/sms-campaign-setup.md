# SMS Campaign Setup Guide — Hoop-Season / Milone Clark

## Table of Contents

- [Company Info on File](#company-info-on-file)
- [What Was Submitted (Original — Rejected)](#what-was-submitted-original--rejected)
- [Exactly What Went Wrong (Problem-by-Problem)](#exactly-what-went-wrong-problem-by-problem)
- [Things You MUST Fix BEFORE Resubmitting](#things-you-must-fix-before-resubmitting)
- [Corrected Text for Every Field (Copy-Paste Ready)](#corrected-text-for-every-field-copy-paste-ready)
- [Compliance Checklist (Go Through Before You Pay $45)](#compliance-checklist-go-through-before-you-pay-45)

---

## Company Info on File

| Field              | Value                                                  |
|--------------------|--------------------------------------------------------|
| Company name       | Milone Clark                                           |
| Display name       | Hoop-Season                                            |
| Website URL        | http://guardubasketball.wixsite.com                    |
| Business Vertical  | Entertainment                                          |
| Email              | gs7@baseflip.net / andy.ekechi@gmail.com               |
| Privacy Policy URL | https://hoop-season-privacy-i0r4a26.gamma.site/        |
| Terms of Service   | https://hoop-season-terms-n5r84zo.gamma.site/          |
| Campaign ID        | C0PRYCZ                                                |
| Use case           | Mixed (Marketing and Account Notification)             |

---

## What Was Submitted (Original — Rejected)

Below is what you submitted last time, field by field.

### Message Flow (what you had)

```
https://hoop-season-privacy-i0r4a26.gamma.site/
https://hoop-season-terms-n5r84zo.gamma.site/
```

### Opt-out Message (what you had)

```
You have been unsubscribed from Hoop-Season messages. You will no longer receive SMS from us. Reply START to resubscribe anytime.
```

### Help Message (what you had)

```
Hoop-Season Support: For help visit https://hoop-season-privacy-i0r4a26.gamma.site/ or email gs7@baseflip.net. Reply STOP to unsubscribe or...
```

### Sample Message 1 (what you had)

```
Hoop-Season: Your order #[ORDER_ID] is confirmed! Track delivery here: [LINK]. Reply STOP to opt out.
```

### Sample Message 2 (what you had)

```
Hoop-Season Alert: New collection just dropped! Limited stock available. Shop now: [LINK]. Reply STOP to opt out.
```

### Sample Message 3 (what you had)

```
Hey [NAME], exclusive deal just for you! 20% off today only. Use code HOOP20 at: [LINK]. Reply STOP to opt out.
```

---

## Exactly What Went Wrong (Problem-by-Problem)

Your campaign was rejected for two categories: **MANDATORY_MESSAGE_TERMINOLOGY** and **CALL_TO_ACTION**. Here is every specific issue.

### Problem 1: Message Flow field only had URLs — no description

**What you did:** You just pasted two URLs (privacy policy and terms).

**What TCR needs:** A detailed written description (200–2000 characters) of exactly HOW customers opt in to receive texts. This must explain where the opt-in happens, what the user sees, what they click, and include the full consent language. Just listing URLs is not enough — the reviewer has to be able to read your description and instantly understand the opt-in process.

### Problem 2: No opt-in page exists

**What TCR needs:** A publicly accessible URL where users can opt in to SMS messages. This is the most important thing. The reviewer will visit this URL to verify it exists, is live, and contains proper consent language.

**The issue:** Your main website `http://guardubasketball.wixsite.com` currently returns a 404 error — it is not accessible. Even if it were accessible, you need a specific page or section on the site where users explicitly opt in to text messages with a checkbox and consent language.

### Problem 3: Sample messages are missing mandatory terminology

Every sample message was missing these required items:

| Required Term                        | Present in your messages? |
|--------------------------------------|---------------------------|
| "Reply STOP to opt out"              | Yes (you had this)        |
| "Reply HELP for help"                | **NO — missing**          |
| "Msg & data rates may apply"         | **NO — missing**          |
| Message frequency disclosure         | **NO — missing**          |
| Privacy policy link or reference     | **NO — missing**          |
| Brand name (Hoop-Season)             | Mostly yes                |

The **first message** a subscriber receives (the opt-in confirmation / welcome message) MUST contain ALL of these. You did not have a welcome/opt-in confirmation message at all — your Sample Message 1 was an order confirmation, which means the very first mandatory message was missing entirely.

### Problem 4: Help message linked to the privacy page

**What you had:** The HELP auto-reply linked to `https://hoop-season-privacy-i0r4a26.gamma.site/` — this is a privacy policy page, not a help/support page.

**What TCR requires:** The HELP message must contain: brand name, contact information (email OR phone OR website for support), opt-in keyword, opt-out keyword, and "Msg & data rates may apply."

### Problem 5: Privacy Policy is missing the required SMS opt-in data sentence

**What TCR specifically requires** in your privacy policy (word for word):

> "Text messaging opt-in data and consent will not be shared with any third parties."

Your privacy policy at `https://hoop-season-privacy-i0r4a26.gamma.site/` says "We do not sell your personal information" — but that is NOT specific enough. TCR requires an explicit statement about **text messaging opt-in data** specifically. This exact sentence must be added to your privacy policy.

### Problem 6: Opt-in consent language must be SMS-specific only

TCR requires that the opt-in language is **exclusively for text messages**. It cannot be bundled with email consent, phone call consent, or general marketing consent. It must be a separate, standalone checkbox or action just for SMS.

---

## Things You MUST Fix BEFORE Resubmitting

Do NOT pay $45 to resubmit until ALL of these are done. The reviewer will check each one.

### Fix 1: Make your website accessible

Your website `http://guardubasketball.wixsite.com` currently returns 404 (page not found). You need to either:
- Fix the Wix site so it loads properly, OR
- Use a different URL that is live

The website URL you registered with the brand must be working.

### Fix 2: Create an SMS opt-in page on your website

You need a page on your website (e.g., `http://guardubasketball.wixsite.com/sms-signup` or a section on your homepage) that has:

1. A phone number input field
2. An **unchecked** checkbox (must NOT be pre-checked) with this consent text:

```
By providing your phone number and checking this box, you consent to receive recurring
automated SMS/MMS messages from Hoop-Season, including order confirmations, delivery
updates, new product drops, exclusive promotions, and basketball event alerts. Message
frequency varies. Message and data rates may apply. Consent is not a condition of
purchase. Reply STOP to cancel at any time. Reply HELP for help.
```

3. Links to your Privacy Policy and Terms of Service directly under the checkbox
4. A "Sign Up" or "Subscribe" button

**The phone number field should NOT be marked as required** — TCR considers a mandatory phone field as "forced opt-in."

### Fix 3: Add the required sentence to your Privacy Policy

Open your privacy policy at `https://hoop-season-privacy-i0r4a26.gamma.site/` and add this exact text to the SMS section (Section 3):

```
Text messaging opt-in data and consent will not be shared with any third parties.
We will not share your opt-in to an SMS campaign with any third party for purposes
unrelated to providing you with the services of that campaign. We may share your
Personal Data, including your SMS opt-in or consent status, with third parties that
help us provide our messaging services, including but not limited to platform providers,
phone companies, and any other vendors who assist us in the delivery of text messages.
```

### Fix 4: Verify all your links are live

Before resubmitting, open each of these in a browser and confirm they load:

| URL | Status You Need |
|-----|-----------------|
| `http://guardubasketball.wixsite.com` | Must load (currently 404!) |
| `https://hoop-season-privacy-i0r4a26.gamma.site/` | Currently working |
| `https://hoop-season-terms-n5r84zo.gamma.site/` | Currently working |
| Your SMS opt-in page URL | Must be live and show the consent form |

---

## Corrected Text for Every Field (Copy-Paste Ready)

Replace `[YOUR-SMS-SIGNUP-URL]` below with the actual URL of your SMS opt-in page once you create it (e.g., `http://guardubasketball.wixsite.com/sms-signup`).

---

### Field: Message Flow

This is the most important field. Copy and paste this entire block:

```
Customers opt in to receive SMS messages through a dedicated sign-up section on our
website at [YOUR-SMS-SIGNUP-URL]. On this page, customers enter their phone number
and must actively check an unchecked consent checkbox before submitting. The checkbox
label reads: "By providing your phone number and checking this box, you consent to
receive recurring automated SMS/MMS messages from Hoop-Season, including order
confirmations, delivery updates, new product drops, exclusive promotions, and
basketball event alerts. Message frequency varies. Message and data rates may apply.
Consent is not a condition of purchase. Reply STOP to cancel at any time. Reply HELP
for help." The page includes links to our Privacy Policy
(https://hoop-season-privacy-i0r4a26.gamma.site/) and Terms of Service
(https://hoop-season-terms-n5r84zo.gamma.site/). Only after checking the consent
checkbox and clicking "Sign Up" is the customer enrolled in SMS messaging. The
phone number field is optional and not forced. Opt-in is exclusively for text
messages and is separate from any email or phone call consent.

Privacy Policy: https://hoop-season-privacy-i0r4a26.gamma.site/
Terms of Service: https://hoop-season-terms-n5r84zo.gamma.site/
```

---

### Field: Opt-out Keywords

```
STOP
```

---

### Field: Opt-out Message

```
Hoop-Season: You have been unsubscribed and will no longer receive SMS messages from Hoop-Season. No further messages will be sent. Reply START to re-subscribe. Msg & data rates may apply.
```

**What changed from your original:** Added brand name at the start, added "No further messages will be sent" (required by TCR), added "Msg & data rates may apply."

---

### Field: Help Keywords

```
HELP
```

---

### Field: Help Message

```
Hoop-Season: For help, visit https://hoop-season-terms-n5r84zo.gamma.site/ or email gs7@baseflip.net. Msg frequency varies. Msg & data rates may apply. Reply STOP to opt out of SMS. Reply START to subscribe.
```

**What changed from your original:** Removed link to privacy page (that's not a help page). Added message frequency, data rates, and opt-in/opt-out keywords — all required by TCR for the HELP response.

---

### Field: Opt-in Keywords

```
START
```

---

### Field: Opt-in Message (Opt-in Confirmation / Welcome Message)

```
Hoop-Season: You're now signed up for SMS notifications! You'll receive order confirmations, delivery updates, new product drops, exclusive promos & basketball event alerts. Msg frequency varies. Msg & data rates may apply. Reply HELP for help. Reply STOP to opt out. Privacy: https://hoop-season-privacy-i0r4a26.gamma.site/ Terms: https://hoop-season-terms-n5r84zo.gamma.site/
```

**Why this matters:** This is the FIRST message every subscriber receives. TCR requires it to contain: brand name, what messages they'll receive, frequency, data rates, HELP keyword, STOP keyword, and links to privacy/terms. You did not have this message at all in your original submission.

---

### Field: Sample Message 1 (Order Confirmation — Account Notification)

```
Hoop-Season: Your order #HPS-78432 is confirmed! Track delivery here: https://guardubasketball.wixsite.com/track. Reply HELP for help. Reply STOP to opt out. Msg & data rates may apply.
```

**What changed from your original:** Added "Reply HELP for help" and "Msg & data rates may apply." Replaced `[ORDER_ID]` with a realistic example and `[LINK]` with a realistic URL. TCR reviewers want to see realistic sample messages, not templates with placeholders.

---

### Field: Sample Message 2 (New Product Drop — Marketing)

```
Hoop-Season Alert: New collection just dropped! Limited stock available. Shop now: https://guardubasketball.wixsite.com/shop. Reply HELP for help. Reply STOP to opt out. Msg & data rates may apply.
```

**What changed from your original:** Added "Reply HELP for help" and "Msg & data rates may apply." Replaced `[LINK]` with a realistic URL.

---

### Field: Sample Message 3 (Promotional — Marketing)

```
Hoop-Season: Exclusive deal for you! 20% off today only. Use code HOOP20 at: https://guardubasketball.wixsite.com/shop. Reply HELP for help. Reply STOP to opt out. Msg & data rates may apply.
```

**What changed from your original:** Removed "Hey [NAME]" (placeholders look unprofessional to reviewers). Added "Reply HELP for help" and "Msg & data rates may apply." Added brand name at start. Replaced `[LINK]` with realistic URL.

---

### Field: Use Case Description

```
Hoop-Season sends SMS notifications to customers who have explicitly opted in through our website at [YOUR-SMS-SIGNUP-URL]. Messages include order confirmations, shipping and delivery updates, new product drop announcements, exclusive promotional offers, and basketball event alerts for our e-commerce and entertainment platform. Customers opt in by entering their phone number and checking a consent checkbox on our SMS sign-up page. Opt-in is exclusively for SMS and is separate from email or other communications. Customers can opt out at any time by replying STOP. Message frequency varies. Message and data rates may apply.
```

---

## Compliance Checklist (Go Through Before You Pay $45)

Go through every single item. Do NOT submit until every box is checked.

### Website & Pages

- [ ] `http://guardubasketball.wixsite.com` loads successfully (no 404)
- [ ] SMS opt-in page exists at a specific URL and is publicly accessible
- [ ] Opt-in page has a phone number field (NOT marked as required)
- [ ] Opt-in page has an **unchecked** checkbox with the full consent text
- [ ] Consent text mentions: SMS messages, Hoop-Season brand, message types, frequency varies, data rates, STOP, HELP
- [ ] Consent text is **only for SMS** — does NOT bundle email or phone call consent
- [ ] Privacy Policy and Terms of Service are linked directly on the opt-in page
- [ ] `https://hoop-season-privacy-i0r4a26.gamma.site/` loads correctly
- [ ] `https://hoop-season-terms-n5r84zo.gamma.site/` loads correctly

### Privacy Policy

- [ ] Privacy policy contains the sentence: "Text messaging opt-in data and consent will not be shared with any third parties."
- [ ] Privacy policy mentions STOP to opt out
- [ ] Privacy policy mentions HELP for assistance

### Campaign Registration Fields

- [ ] **Message Flow** describes the full opt-in process (not just URLs)
- [ ] **Message Flow** includes the opt-in page URL
- [ ] **Message Flow** includes the full consent checkbox language
- [ ] **Message Flow** states the phone number field is optional
- [ ] **Message Flow** states opt-in is exclusively for SMS
- [ ] **Opt-out message** includes brand name, confirmation no more messages, and START keyword
- [ ] **Help message** includes brand name, contact info, frequency, data rates, STOP and START keywords
- [ ] **Opt-in confirmation message** includes brand name, message types, frequency, data rates, HELP, STOP, privacy link, terms link

### Sample Messages

- [ ] Every sample message starts with "Hoop-Season" (brand name)
- [ ] Every sample message includes "Reply STOP to opt out"
- [ ] Every sample message includes "Reply HELP for help"
- [ ] Every sample message includes "Msg & data rates may apply"
- [ ] No placeholder text like `[NAME]`, `[LINK]`, `[ORDER_ID]` — use realistic examples
- [ ] At least one sample message is for account notifications (order confirmation)
- [ ] At least one sample message is for marketing (promo/product drop)
- [ ] Sample messages match the "Mixed" use case (both marketing AND account notification)

---

## Summary of All Changes From Original Submission

| Field | What Was Wrong | What to Fix |
|-------|---------------|-------------|
| Message Flow | Only had 2 URLs, no description | Full written description of opt-in process |
| Opt-in page | Did not exist | Create one on your website with consent checkbox |
| Website | Returns 404 | Fix so it loads |
| Privacy Policy | Missing required SMS data-sharing sentence | Add "Text messaging opt-in data and consent will not be shared with any third parties" |
| Sample Messages | Missing HELP, data rates, frequency | Add to every message |
| Welcome Message | Did not exist | Add opt-in confirmation with all disclosures |
| Help Message | Linked to privacy page, missing terms | Link to support/terms, add frequency and data rates |
| Opt-out Message | Missing brand name at start, missing "no further messages" | Add both |
| Sample Message placeholders | Had [NAME], [LINK], [ORDER_ID] | Replace with realistic examples |
