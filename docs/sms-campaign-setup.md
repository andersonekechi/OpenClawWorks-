# SMS Campaign Setup Guide

## Table of Contents

- [Overview](#overview)
- [10DLC Campaign Registration](#10dlc-campaign-registration)
- [Campaign Failure: Hoop-Season Notifications](#campaign-failure-hoop-season-notifications)
  - [Rejection Details](#rejection-details)
  - [Why It Failed](#why-it-failed)
  - [How to Fix It](#how-to-fix-it)
- [Exact Text to Input for Campaign Resubmission](#exact-text-to-input-for-campaign-resubmission)
- [Compliance Checklist](#compliance-checklist)
- [Sample Compliant Opt-In Page](#sample-compliant-opt-in-page)
- [References](#references)

---

## Overview

To send SMS messages from a US 10DLC (10-Digit Long Code) number, you must register a use case with **The Campaign Registry (TCR)**. TCR reviews campaign registrations and can decline them if they do not meet compliance requirements set by carriers and the DCA (Direct Connect Aggregator).

This document covers common reasons for campaign registration failures and provides actionable steps to resolve them.

---

## 10DLC Campaign Registration

When registering a 10DLC campaign, the following information is shared with TCR:

| Field                  | Description                                                              |
|------------------------|--------------------------------------------------------------------------|
| **Campaign name**      | The name of your messaging campaign                                      |
| **Use case**           | The type of messaging (e.g., Marketing, Mixed, Account Notifications)    |
| **Sub use case**       | More specific categorization of your messaging                           |
| **Use case description** | A detailed description of what messages you will send and to whom      |
| **Sample messages**    | Example messages that will be sent to subscribers                        |
| **Opt-in flow**        | How subscribers consent to receive messages                              |
| **Call-to-action (CTA)** | The mechanism by which users agree to receive SMS messages             |

---

## Campaign Failure: Hoop-Season Notifications

### Rejection Details

| Field                  | Value                                                  |
|------------------------|--------------------------------------------------------|
| **Campaign name**      | Hoop-Season Notifications                              |
| **Campaign ID**        | C0PRYCZ                                                |
| **Use case**           | Mixed                                                  |
| **Sub use case**       | Marketing and Account Notification                     |
| **Registration status**| **Declined**                                           |
| **Rejection category** | `MANDATORY_MESSAGE_TERMINOLOGY`, `CALL_TO_ACTION`      |

**Full rejection message:**

> DCA declined sharing request for campaign C0PRYCZ. Rejection Category: MANDATORY_MESSAGE_TERMINOLOGY, CALL_TO_ACTION. Explanation: Unable to verify, needs compliant and accurate CTA information. Update with specific path for mobile opt-in, HELP instructions, STOP instructions, message frequency disclosure, "message and data rates may apply" disclosure and link to the message program privacy policy, or language referring to the privacy policy. (806) This could be addressed by revising your campaign messaging flow by incorporating a URL to a publicly accessible page that includes a clear opt-in statement (e.g., "I hereby agree to receive SMS") or including screenshots from any mobile app or paper form that uses similar language for consent in cases where consent is not obtained through a webpage.

### Why It Failed

The campaign was rejected for **two categories** of non-compliance:

#### 1. MANDATORY_MESSAGE_TERMINOLOGY

The sample messages or campaign description did not include the required compliance language. Every SMS campaign must ensure that messages contain or reference:

- **STOP instructions** — Subscribers must know how to opt out (e.g., "Reply STOP to unsubscribe").
- **HELP instructions** — Subscribers must know how to get help (e.g., "Reply HELP for help").
- **Message frequency disclosure** — How often messages will be sent (e.g., "Msg frequency varies" or "Up to 4 msgs/month").
- **"Message and data rates may apply"** — Standard carrier cost disclosure.
- **Privacy policy link** — A link to the program's privacy policy, or language referencing it.

#### 2. CALL_TO_ACTION (CTA)

The opt-in flow could not be verified. TCR requires proof that subscribers are giving **express written consent** to receive SMS messages. The submission was missing:

- A **publicly accessible URL** where the opt-in occurs (e.g., a website sign-up form with SMS consent checkbox).
- **Screenshots** of a mobile app or paper form showing the consent language (if opt-in is not web-based).
- A **clear opt-in statement** such as: *"I hereby agree to receive SMS"* or *"By providing your phone number, you consent to receive text messages from Hoop-Season."*

### How to Fix It

Follow these steps to resubmit the campaign successfully:

#### Step 1: Create a Compliant Opt-In Page

Create a **publicly accessible webpage** (or update an existing one) that includes:

1. A clear opt-in checkbox or button that users must actively select.
2. Explicit consent language, for example:
   > "By checking this box, you agree to receive recurring SMS/MMS messages from Hoop-Season Notifications, including order confirmations, delivery updates, promotions, and event alerts. Message frequency varies. Message and data rates may apply. Reply STOP to cancel, HELP for help."
3. A link to your **Terms of Service**.
4. A link to your **Privacy Policy**.

#### Step 2: Update Sample Messages with Required Terminology

Make sure every sample message you provide includes the mandatory disclosures. At minimum, the **first message** a subscriber receives should contain:

```
Welcome to Hoop-Season Notifications! You'll receive order updates, delivery alerts, new product drops, exclusive promos & basketball event alerts. Msg frequency varies. Msg & data rates may apply. Reply HELP for help, STOP to opt out. Privacy: https://yoursite.com/privacy
```

Subsequent messages should include at least:

```
Hoop-Season: Your order #12345 has shipped! Track it here: https://yoursite.com/track/12345. Reply STOP to opt out.
```

#### Step 3: Provide the Opt-In URL or Screenshots

When resubmitting the campaign:

- **If opt-in is on a website:** Provide the full URL to the page where users subscribe (e.g., `https://hoop-season.com/sms-signup`). The page must be **live and publicly accessible** at the time of review.
- **If opt-in is in a mobile app:** Provide **screenshots** of the app screen where consent is collected, showing the full consent language.
- **If opt-in is on a paper form:** Provide **photos or scans** of the form showing the consent language.

#### Step 4: Update the Campaign Description

Ensure the use case description clearly explains:

- **Who** receives messages (opted-in customers).
- **What** types of messages are sent (order confirmations, delivery updates, promotions, event alerts).
- **How** users opt in (web form, app, etc.).
- **How** users opt out (Reply STOP).

#### Step 5: Resubmit the Campaign

After making all the changes above, resubmit the campaign through your 10DLC provider's dashboard (e.g., Twilio, Vonage, Bandwidth, etc.).

---

## Exact Text to Input for Campaign Resubmission

Below is the exact, copy-paste-ready text for every field you need to fill in when resubmitting the Hoop-Season Notifications campaign. Replace `https://hoop-season.com` with your actual domain wherever it appears.

---

### Field: Campaign Name

```
Hoop-Season Notifications
```

### Field: Use Case

```
Mixed
```

### Field: Sub Use Case

```
Marketing and Account Notification
```

### Field: Use Case Description

Copy and paste this into the use case description field:

```
Hoop-Season sends SMS notifications to customers who have explicitly opted in through our website at https://hoop-season.com/sms-signup. Messages include order confirmations, shipping and delivery updates, new product drop announcements, exclusive promotional offers, and basketball event alerts for our e-commerce and entertainment platform. Customers opt in by entering their phone number and checking a consent checkbox on our SMS sign-up page. Customers can opt out at any time by replying STOP. Message frequency varies. Message and data rates may apply.
```

### Field: Sample Message 1 (Welcome / Opt-In Confirmation)

This is the first message a subscriber receives. It **must** contain all required disclosures:

```
Welcome to Hoop-Season Notifications! You've opted in to receive order updates, delivery alerts, new product drops, exclusive promos & basketball event alerts. Msg frequency varies. Msg & data rates may apply. Reply HELP for help. Reply STOP to opt out. Terms: https://hoop-season.com/terms Privacy: https://hoop-season.com/privacy
```

### Field: Sample Message 2 (Order Confirmation — Account Notification)

```
Hoop-Season: Your order #HPS-78432 has been confirmed! We're getting it ready. You'll receive a text when it ships. Reply STOP to opt out.
```

### Field: Sample Message 3 (Shipping Update — Account Notification)

```
Hoop-Season: Your order #HPS-78432 has shipped! Track it here: https://hoop-season.com/track/HPS-78432. Estimated delivery: March 31. Reply STOP to opt out.
```

### Field: Sample Message 4 (Promotional — Marketing)

```
Hoop-Season: March Madness Sale! 25% off all jerseys this weekend only. Shop now: https://hoop-season.com/sale. Reply STOP to opt out.
```

### Field: Sample Message 5 (Event Alert — Marketing)

```
Hoop-Season: Lakers vs Celtics tonight at 7pm ET! Grab your game-day gear: https://hoop-season.com/gameday. Reply STOP to opt out.
```

### Field: Opt-In Flow Description / Call-to-Action (CTA)

Copy and paste this into the opt-in flow / CTA field:

```
Customers opt in to receive SMS messages through a dedicated sign-up page on our website at https://hoop-season.com/sms-signup. On this page, customers enter their phone number and must actively check an unchecked consent checkbox before submitting. The checkbox label reads: "I agree to receive recurring automated SMS/MMS messages from Hoop-Season Notifications at the number provided, including order confirmations, delivery updates, new product drops, exclusive promotions, and basketball event alerts. Message frequency varies. Message and data rates may apply. Consent is not a condition of purchase. Reply STOP to cancel at any time. Reply HELP for help." The page also includes links to our Terms of Service (https://hoop-season.com/terms) and Privacy Policy (https://hoop-season.com/privacy). Only after checking the consent box and clicking "Sign Up" is the customer enrolled.
```

### Field: Opt-In URL

```
https://hoop-season.com/sms-signup
```

### Field: Help Message (auto-reply when user texts HELP)

```
Hoop-Season Notifications Help: For support, visit https://hoop-season.com/help or email support@hoop-season.com. To stop messages, reply STOP. Msg & data rates may apply. Msg frequency varies.
```

### Field: Stop Message (auto-reply when user texts STOP)

```
You have been unsubscribed from Hoop-Season Notifications. You will no longer receive messages. Reply START to re-subscribe. For help, visit https://hoop-season.com/help.
```

---

### What Your Opt-In Page Must Look Like (Before Resubmitting)

Your page at `https://hoop-season.com/sms-signup` must be **live and publicly accessible** when TCR reviews it. It must include the following elements:

**1. Phone number input field**

**2. An unchecked checkbox with this exact consent text next to it:**

```
I agree to receive recurring automated SMS/MMS messages from Hoop-Season Notifications at the phone number provided, including order confirmations, delivery updates, new product drops, exclusive promotions, and basketball event alerts. Message frequency varies. Message and data rates may apply. Consent is not a condition of purchase. Reply STOP to cancel at any time. Reply HELP for help.
```

**3. Links below the checkbox:**

```
By signing up, you agree to our Terms of Service and Privacy Policy.
```

Where "Terms of Service" links to `https://hoop-season.com/terms` and "Privacy Policy" links to `https://hoop-season.com/privacy`.

**4. A "Sign Up" button** that only works when the checkbox is checked.

---

### Quick Reference: All Required URLs You Need Live

| URL | What It Is | Must Be Live? |
|-----|-----------|---------------|
| `https://hoop-season.com/sms-signup` | SMS opt-in page with consent checkbox | **Yes** |
| `https://hoop-season.com/privacy` | Privacy policy page | **Yes** |
| `https://hoop-season.com/terms` | Terms of service page | **Yes** |
| `https://hoop-season.com/help` | Help/support page | Recommended |

> **Important:** Replace `hoop-season.com` with your actual website domain throughout all fields above. All URLs must be live and publicly accessible when you resubmit — TCR will check them.

---

## Compliance Checklist

Use this checklist before submitting any SMS campaign:

- [ ] **Opt-in page** is publicly accessible and live
- [ ] **Opt-in language** explicitly mentions SMS/text messages
- [ ] **Consent is affirmative** (checkbox, button, or keyword — not pre-checked)
- [ ] **STOP instructions** included in sample messages ("Reply STOP to unsubscribe")
- [ ] **HELP instructions** included in sample messages ("Reply HELP for help")
- [ ] **Message frequency** disclosed ("Message frequency varies" or specific count)
- [ ] **"Message and data rates may apply"** included
- [ ] **Privacy policy** linked on the opt-in page and referenced in messages
- [ ] **Terms of service** linked on the opt-in page
- [ ] **Campaign description** accurately reflects message content and audience
- [ ] **Sample messages** are realistic and include all required disclosures

---

## Sample Compliant Opt-In Page

Below is an example of the language your SMS sign-up page should include:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│   📱 Sign Up for Hoop-Season Text Alerts             │
│                                                      │
│   Phone Number: [_______________]                    │
│                                                      │
│   [ ] I agree to receive recurring automated         │
│       SMS/MMS messages from Hoop-Season              │
│       Notifications at the phone number provided,    │
│       including order confirmations, delivery         │
│       updates, new product drops, exclusive           │
│       promotions, and basketball event alerts.        │
│       Message frequency varies. Message and data      │
│       rates may apply. Consent is not a condition     │
│       of purchase. Reply STOP to cancel at any        │
│       time. Reply HELP for help.                      │
│                                                      │
│   By signing up, you agree to our Terms of Service   │
│   (link) and Privacy Policy (link).                  │
│                                                      │
│   [  Sign Up  ]                                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## References

- [CTIA Messaging Principles and Best Practices](https://www.ctia.org/the-wireless-industry/industry-commitments/messaging-principles-and-best-practices)
- [TCR Campaign Registry](https://www.campaignregistry.com/)
- [10DLC Overview — Twilio](https://www.twilio.com/docs/messaging/guides/10dlc)
- [TCPA Compliance Guide](https://www.fcc.gov/consumers/guides/stop-unwanted-robocalls-and-texts)
