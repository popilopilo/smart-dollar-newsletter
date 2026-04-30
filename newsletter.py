import anthropic
import requests
import json
import os
from datetime import datetime

# ── CONFIG (loaded from GitHub Secrets) ──────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY   = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID    = os.environ["BEEHIIV_PUB_ID"]

# ── AFFILIATE LINKS ───────────────────────────────────────────────────────────
AFFILIATES = {
    "revolut":  "https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",
    "coinbase": "https://coinbase.com/join/RSRGFEP?src=ios-link",
    "etoro":    "https://etoro.tw/4vZbEOP",
    "nordvpn":  "https://refer-nordvpn.com/BrJJQSzaIsM",
}

SUBSCRIBE_URL = "https://arnauds-newsletter-47845f.beehiiv.com"

# ── GENERATE NEWSLETTER WITH CLAUDE ──────────────────────────────────────────
def generate_newsletter():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today  = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are writing today's issue of "The Smart Dollar" — a daily newsletter about personal finance and AI tools.

Today's date: {today}

The newsletter has a Swiss/European audience so mention international tools, not just US-only ones.

Generate a complete newsletter issue as a JSON object with EXACTLY these fields:
{{
  "subject": "catchy email subject under 60 chars",
  "headline": "main headline for today",
  "intro": "2-3 sentence warm intro",
  "story1_tag": "MONEY TIP",
  "story1_title": "title",
  "story1_body": "3-4 sentences of actionable advice",
  "story1_affiliate": null or one of: "revolut", "coinbase", "etoro", "nordvpn",
  "story2_tag": "AI SPOTLIGHT",
  "story2_title": "title",
  "story2_body": "3-4 sentences about an AI tool that saves money or time",
  "story2_affiliate": null or one of: "revolut", "coinbase", "etoro", "nordvpn",
  "story3_tag": "INVEST SMART",
  "story3_title": "title",
  "story3_body": "3-4 sentences on investing",
  "story3_affiliate": null or one of: "revolut", "coinbase", "etoro", "nordvpn",
  "quick_tip": "one punchy tip of the day"
}}

Rules for affiliate matching:
- Use "revolut" in stories about banking, saving, spending, travel money
- Use "coinbase" in stories about crypto
- Use "etoro" in stories about investing, stocks, portfolios
- Use "nordvpn" in stories about security, privacy, online safety
- Each story can have null if no affiliate fits naturally
- Never put the same affiliate in more than one story
- Make the affiliate feel natural, not forced

Return ONLY the JSON object. No markdown. No extra text."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw  = message.content[0].text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


# ── BUILD HTML FOR BEEHIIV ────────────────────────────────────────────────────
def build_html(issue):
    def aff_block(key):
        if not key:
            return ""
        names  = {"revolut": "Revolut 💳", "coinbase": "Coinbase ₿", "etoro": "eToro 📈", "nordvpn": "NordVPN 🔒"}
        descs  = {
            "revolut":  "Join 70M+ users on Revolut — zero-fee banking for the modern age.",
            "coinbase": "Start investing in crypto with as little as $2 on Coinbase.",
            "etoro":    "Copy top investors automatically with eToro — investing made simple.",
            "nordvpn":  "Protect your finances online with NordVPN — one tap, all devices.",
        }
        url = AFFILIATES[key]
        return f"""
        <div style="margin-top:12px;background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);border-radius:8px;padding:12px;">
          <p style="margin:0 0 6px;font-size:13px;color:#666;">{descs[key]}</p>
          <a href="{url}" style="display:inline-block;background:#1a1a2e;color:#ffd700;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:700;text-decoration:none;">
            👉 Try {names[key]}
          </a>
        </div>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Georgia,serif;max-width:600px;margin:0 auto;padding:20px;background:#fff;color:#1a1a2e;">

  <div style="text-align:center;padding:24px 0 16px;border-bottom:2px solid #ffd700;margin-bottom:24px;">
    <h1 style="font-size:28px;font-weight:900;margin:0;color:#1a1a2e;">💰 The Smart Dollar</h1>
    <p style="margin:6px 0 0;color:#888;font-size:13px;">{datetime.now().strftime("%B %d, %Y")} · Finance & AI for Smart People</p>
  </div>

  <h2 style="font-size:24px;font-weight:800;margin-bottom:8px;">{issue['headline']}</h2>
  <p style="font-size:15px;color:#555;line-height:1.7;margin-bottom:28px;">{issue['intro']}</p>

  <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:18px;border-radius:8px;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#16a34a;letter-spacing:2px;">{issue['story1_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0;">{issue['story1_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story1_body']}</p>
    {aff_block(issue.get('story1_affiliate'))}
  </div>

  <div style="background:#eff6ff;border-left:4px solid #2563eb;padding:18px;border-radius:8px;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#2563eb;letter-spacing:2px;">{issue['story2_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0;">{issue['story2_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story2_body']}</p>
    {aff_block(issue.get('story2_affiliate'))}
  </div>

  <div style="background:#fefce8;border-left:4px solid #ca8a04;padding:18px;border-radius:8px;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#ca8a04;letter-spacing:2px;">{issue['story3_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0;">{issue['story3_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story3_body']}</p>
    {aff_block(issue.get('story3_affiliate'))}
  </div>

  <div style="background:#1a1a2e;color:#fff;padding:20px;border-radius:12px;text-align:center;margin-bottom:28px;">
    <p style="font-size:11px;opacity:0.6;margin:0 0 6px;letter-spacing:2px;">💡 TIP OF THE DAY</p>
    <p style="font-size:16px;font-weight:700;margin:0;">{issue['quick_tip']}</p>
  </div>

  <div style="text-align:center;padding:20px 0;border-top:1px solid #eee;margin-top:24px;">
    <p style="font-size:13px;color:#888;margin:0 0 8px;">Enjoying The Smart Dollar?</p>
    <a href="{SUBSCRIBE_URL}" style="display:inline-block;background:#ffd700;color:#1a1a2e;padding:10px 24px;border-radius:8px;font-weight:800;font-size:14px;text-decoration:none;">
      📬 Share with a friend
    </a>
    <p style="font-size:11px;color:#bbb;margin:12px 0 0;">The Smart Dollar · Unsubscribe below</p>
  </div>

</body>
</html>"""


# ── POST TO BEEHIIV ───────────────────────────────────────────────────────────
def post_to_beehiiv(issue, html):
    url     = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/posts"
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
    }
    payload = {
        "title":        issue["subject"],
        "subtitle":     issue["headline"],
        "content_html": html,
        "status":       "confirm",   # auto-sends to all subscribers
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Generating today's Smart Dollar issue...")
    issue = generate_newsletter()
    print(f"✅ Generated: {issue['subject']}")

    html = build_html(issue)
    print("✅ HTML built")

    result = post_to_beehiiv(issue, html)
    print(f"✅ Posted to Beehiiv! Post ID: {result.get('data', {}).get('id', 'unknown')}")
    print("🎉 Done! Your newsletter has been sent automatically.")
