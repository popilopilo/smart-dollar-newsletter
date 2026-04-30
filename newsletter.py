import anthropic
import requests
import json
import os
import random
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# ── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY      = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID       = os.environ["BEEHIIV_PUB_ID"]
BLOGGER_API_KEY      = os.environ.get("BLOGGER_API_KEY", "")
BLOGGER_BLOG_ID      = os.environ.get("BLOGGER_BLOG_ID", "")
PINTEREST_TOKEN      = os.environ.get("PINTEREST_TOKEN", "")
PINTEREST_BOARD_ID   = os.environ.get("PINTEREST_BOARD_ID", "")

SUBSCRIBE_URL = "https://arnauds-newsletter-47845f.beehiiv.com"

# ── ALL AFFILIATE LINKS ───────────────────────────────────────────────────────
AFFILIATES = {
    "revolut":  {
        "url":   "https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",
        "label": "Revolut", "emoji": "💳",
        "desc":  "Join 70M+ users — zero-fee banking & spending abroad",
        "tags":  ["banking", "spending", "travel", "saving", "international"],
    },
    "coinbase": {
        "url":   "https://coinbase.com/join/RSRGFEP?src=ios-link",
        "label": "Coinbase", "emoji": "₿",
        "desc":  "Start investing in crypto with as little as $2",
        "tags":  ["crypto", "bitcoin", "ethereum", "digital assets"],
    },
    "etoro": {
        "url":   "https://etoro.tw/4vZbEOP",
        "label": "eToro", "emoji": "📈",
        "desc":  "Copy top investors automatically — investing made simple",
        "tags":  ["investing", "stocks", "portfolio", "trading", "ETF"],
    },
    "nordvpn": {
        "url":   "https://refer-nordvpn.com/BrJJQSzaIsM",
        "label": "NordVPN", "emoji": "🔒",
        "desc":  "Protect your finances online — one tap, all devices",
        "tags":  ["security", "privacy", "VPN", "online safety", "hacking"],
    },
    "neon": {
        "url":   "http://onelink.to/neon",
        "code":  "SDB98A",
        "label": "Neon", "emoji": "🇨🇭",
        "desc":  "Switzerland's best free bank account — use code SDB98A",
        "tags":  ["swiss bank", "switzerland", "free account", "CHF", "neobank"],
    },
    "yuh": {
        "url":   "https://www.yuh.com/download",
        "code":  "uzwi60",
        "label": "Yuh", "emoji": "💰",
        "desc":  "Pay, save and invest in one Swiss app — use code uzwi60",
        "tags":  ["swiss", "invest", "save", "pay", "all-in-one"],
    },
    "binance": {
        "url":   "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00Z6UROXWP",
        "label": "Binance", "emoji": "🟡",
        "desc":  "World's largest crypto exchange — trade 350+ coins",
        "tags":  ["crypto", "trading", "altcoins", "binance", "exchange"],
    },
    "alpian": {
        "url":   "https://onelink.to/download-alpian",
        "code":  "PCXTNB",
        "label": "Alpian", "emoji": "🏔️",
        "desc":  "Swiss private banking app — get CHF 25 bonus with code PCXTNB",
        "tags":  ["swiss", "private banking", "wealth", "investment", "CHF"],
    },
}

# ── CLAUDE CLIENT ─────────────────────────────────────────────────────────────
def claude(prompt, max_tokens=1500):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    return raw.replace("```json", "").replace("```", "").strip()


# ══════════════════════════════════════════════════════════════════════════════
# 1. NEWSLETTER
# ══════════════════════════════════════════════════════════════════════════════
def generate_newsletter():
    today = datetime.now().strftime("%B %d, %Y")
    aff_list = "\n".join([f'- "{k}": {v["tags"]}' for k, v in AFFILIATES.items()])

    prompt = f"""Write today's issue of "The Smart Dollar" newsletter for a Swiss/European audience.
Date: {today}

Available affiliates and their relevant topics:
{aff_list}

Return ONLY a JSON object:
{{
  "subject": "catchy subject under 60 chars",
  "headline": "main headline",
  "intro": "2-3 sentence intro",
  "story1_tag": "MONEY TIP",
  "story1_title": "title",
  "story1_body": "3-4 sentences, actionable, specific numbers",
  "story1_affiliate": null or affiliate key from the list above,
  "story2_tag": "AI SPOTLIGHT",
  "story2_title": "title",
  "story2_body": "3-4 sentences about AI tool saving money/time",
  "story2_affiliate": null or affiliate key,
  "story3_tag": "INVEST SMART",
  "story3_title": "title",
  "story3_body": "3-4 sentences on investing, Switzerland-relevant",
  "story3_affiliate": null or affiliate key,
  "quick_tip": "one punchy tip",
  "seo_keyword": "main keyword phrase this targets (e.g. best swiss investing app)"
}}

Rules: Each affiliate used max once. Match affiliate to story topic naturally. Be specific with numbers."""

    return json.loads(claude(prompt))


def build_newsletter_html(issue):
    today = datetime.now().strftime("%B %d, %Y")

    def aff_block(key):
        if not key or key not in AFFILIATES:
            return ""
        a = AFFILIATES[key]
        code_line = f"<p style='margin:4px 0 6px;font-size:12px;color:#888;'>Use code: <strong>{a['code']}</strong></p>" if a.get("code") else ""
        return f"""<div style="margin-top:12px;background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px;">
          <p style="margin:0 0 4px;font-size:13px;color:#666;">{a['emoji']} {a['desc']}</p>
          {code_line}
          <a href="{a['url']}" style="display:inline-block;background:#1a1a2e;color:#ffd700;padding:7px 14px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none;">Try {a['label']} →</a>
        </div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="font-family:Georgia,serif;max-width:600px;margin:0 auto;padding:20px;color:#1a1a2e;">
  <div style="text-align:center;padding:20px 0;border-bottom:3px solid #ffd700;margin-bottom:24px;">
    <h1 style="font-size:26px;font-weight:900;margin:0;">💰 The Smart Dollar</h1>
    <p style="margin:6px 0 0;color:#888;font-size:12px;">{today} · Finance & AI for Smart People</p>
  </div>
  <h2 style="font-size:22px;font-weight:800;">{issue['headline']}</h2>
  <p style="font-size:15px;color:#555;line-height:1.7;margin-bottom:24px;">{issue['intro']}</p>
  <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px;border-radius:8px;margin-bottom:18px;">
    <span style="font-size:10px;font-weight:800;color:#16a34a;letter-spacing:2px;">{issue['story1_tag']}</span>
    <h3 style="font-size:17px;font-weight:800;margin:6px 0;">{issue['story1_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story1_body']}</p>
    {aff_block(issue.get('story1_affiliate'))}
  </div>
  <div style="background:#eff6ff;border-left:4px solid #2563eb;padding:16px;border-radius:8px;margin-bottom:18px;">
    <span style="font-size:10px;font-weight:800;color:#2563eb;letter-spacing:2px;">{issue['story2_tag']}</span>
    <h3 style="font-size:17px;font-weight:800;margin:6px 0;">{issue['story2_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story2_body']}</p>
    {aff_block(issue.get('story2_affiliate'))}
  </div>
  <div style="background:#fefce8;border-left:4px solid #ca8a04;padding:16px;border-radius:8px;margin-bottom:18px;">
    <span style="font-size:10px;font-weight:800;color:#ca8a04;letter-spacing:2px;">{issue['story3_tag']}</span>
    <h3 style="font-size:17px;font-weight:800;margin:6px 0;">{issue['story3_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.7;margin:0;">{issue['story3_body']}</p>
    {aff_block(issue.get('story3_affiliate'))}
  </div>
  <div style="background:#1a1a2e;color:#fff;padding:18px;border-radius:10px;text-align:center;margin-bottom:24px;">
    <p style="font-size:10px;opacity:0.6;margin:0 0 4px;letter-spacing:2px;">💡 TIP OF THE DAY</p>
    <p style="font-size:15px;font-weight:700;margin:0;">{issue['quick_tip']}</p>
  </div>
  <div style="text-align:center;padding:16px 0;border-top:1px solid #eee;">
    <p style="font-size:13px;color:#888;margin:0 0 8px;">Share The Smart Dollar with a friend 👇</p>
    <a href="{SUBSCRIBE_URL}" style="display:inline-block;background:#ffd700;color:#1a1a2e;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;text-decoration:none;">Subscribe Free →</a>
  </div>
</body></html>"""


def post_newsletter(issue, html):
    url = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/posts"
    payload = {
        "title":        issue["subject"],
        "subtitle":     issue["headline"],
        "content_html": html,
        "status":       "draft",   # draft = safe, works on free plan
    }
    r = requests.post(url,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {BEEHIIV_API_KEY}"},
        json=payload)
    if not r.ok:
        print(f"Beehiiv error {r.status_code}: {r.text}")
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 2. SEO BLOG POST (Blogger — free, Google-indexed)
# ══════════════════════════════════════════════════════════════════════════════
def generate_blog_post(issue):
    # Pick 2 random affiliates to feature
    aff_keys = random.sample(list(AFFILIATES.keys()), 2)
    aff_info  = "\n".join([f"- {AFFILIATES[k]['label']}: {AFFILIATES[k]['desc']} ({AFFILIATES[k]['url']})" for k in aff_keys])

    prompt = f"""Write a 600-word SEO blog post for "The Smart Dollar" blog targeting the keyword: "{issue['seo_keyword']}"

Audience: Swiss/European people interested in personal finance and AI tools.

Include naturally in the article (don't force it):
{aff_info}

Format as JSON:
{{
  "title": "SEO-optimized blog title with keyword",
  "meta_description": "155 char meta description with keyword",
  "html_body": "full blog post HTML with h2 subheadings, paragraphs, and affiliate links naturally embedded. Use <a href='URL'>anchor text</a> for links."
}}

Make it genuinely helpful, not spammy. Include specific numbers and actionable advice."""

    return json.loads(claude(prompt, max_tokens=2000))


def post_to_blogger(blog_post):
    if not BLOGGER_API_KEY or not BLOGGER_BLOG_ID:
        print("⏭️  Blogger not configured, skipping")
        return
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts?key={BLOGGER_API_KEY}"
    r = requests.post(url, json={
        "title": blog_post["title"],
        "content": f"<meta name='description' content='{blog_post['meta_description']}'>\n{blog_post['html_body']}"
    })
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 3. PINTEREST PIN (fully automated, official API)
# ══════════════════════════════════════════════════════════════════════════════
def generate_pinterest_content(issue):
    prompt = f"""Create a Pinterest pin for this finance tip:
Topic: {issue['headline']}
Tip: {issue['quick_tip']}

Return JSON:
{{
  "title": "Pinterest pin title under 100 chars",
  "description": "Pinterest description 200-500 chars, include 5 relevant hashtags like #personalfinance #SwissFinance #investing #moneytips #financialfreedom",
  "alt_text": "image alt text"
}}"""
    return json.loads(claude(prompt, max_tokens=300))


def post_to_pinterest(pin_content, issue):
    if not PINTEREST_TOKEN or not PINTEREST_BOARD_ID:
        print("⏭️  Pinterest not configured, skipping")
        return
    # Use a finance-themed image from Unsplash (free, no API key needed)
    image_url = f"https://source.unsplash.com/800x1200/?finance,money,investing&sig={datetime.now().day}"
    r = requests.post("https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {PINTEREST_TOKEN}", "Content-Type": "application/json"},
        json={
            "board_id":    PINTEREST_BOARD_ID,
            "title":       pin_content["title"],
            "description": pin_content["description"] + f"\n\n🔗 Free newsletter: {SUBSCRIBE_URL}",
            "alt_text":    pin_content["alt_text"],
            "media_source": {"source_type": "image_url", "url": image_url},
            "link":        SUBSCRIBE_URL,
        })
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 4. REDDIT COMMENT (copy-paste ready, saved to file)
# ══════════════════════════════════════════════════════════════════════════════
def generate_reddit_content(issue):
    # Pick most relevant affiliate for this issue
    all_affs = [issue.get(f"story{i}_affiliate") for i in range(1, 4)]
    primary_aff = next((a for a in all_affs if a), "etoro")
    aff = AFFILIATES[primary_aff]

    prompt = f"""Write a genuine, helpful Reddit comment about: "{issue['seo_keyword']}"

Based on this insight: {issue['story1_body']}

Rules:
- Sound like a real person, not an ad
- Be genuinely helpful first
- Mention {aff['label']} naturally at the end only if relevant
- End with: "I also write a free weekly newsletter on this stuff: {SUBSCRIBE_URL}"
- Max 150 words
- No markdown headers

Also suggest 3 specific subreddits to post this in.

Return JSON:
{{
  "comment": "the full comment text",
  "subreddits": ["subreddit1", "subreddit2", "subreddit3"],
  "suggested_post_title": "title to search for or post as"
}}"""
    return json.loads(claude(prompt, max_tokens=500))


# ══════════════════════════════════════════════════════════════════════════════
# 5. TWITTER/X THREAD
# ══════════════════════════════════════════════════════════════════════════════
def generate_twitter_thread(issue):
    aff_keys = [issue.get(f"story{i}_affiliate") for i in range(1, 4) if issue.get(f"story{i}_affiliate")]

    prompt = f"""Write a 5-tweet Twitter/X thread about: "{issue['headline']}"

Key points to cover:
1. {issue['story1_title']}: {issue['story1_body'][:100]}
2. {issue['story2_title']}: {issue['story2_body'][:100]}
3. {issue['story3_title']}: {issue['story3_body'][:100]}

Rules:
- Tweet 1: Hook that stops the scroll (no "Thread:" just start strong)
- Tweets 2-4: One insight each, specific numbers, under 280 chars each
- Tweet 5: CTA to subscribe at {SUBSCRIBE_URL}
- Add 2-3 hashtags only on tweet 5
- Naturally mention one of these if relevant: {[AFFILIATES[k]['label'] for k in aff_keys if k]}

Return JSON: {{"tweets": ["tweet1", "tweet2", "tweet3", "tweet4", "tweet5"]}}"""
    return json.loads(claude(prompt, max_tokens=600))


# ══════════════════════════════════════════════════════════════════════════════
# 6. LINKEDIN POST
# ══════════════════════════════════════════════════════════════════════════════
def generate_linkedin_post(issue):
    prompt = f"""Write a LinkedIn post about: "{issue['headline']}"

Key insight: {issue['story1_body']}

Rules:
- Professional but conversational tone
- Start with a bold first line (no "I" as first word)
- 150-200 words
- End with CTA: subscribe free at {SUBSCRIBE_URL}
- 3-5 relevant hashtags at the end
- Finance/investing angle, Swiss/European perspective

Return JSON: {{"post": "full post text"}}"""
    return json.loads(claude(prompt, max_tokens=400))


# ══════════════════════════════════════════════════════════════════════════════
# 7. SAVE DAILY MARKETING PACK (copy-paste file)
# ══════════════════════════════════════════════════════════════════════════════
def save_marketing_pack(reddit, twitter, linkedin, issue):
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""
╔══════════════════════════════════════════════════════════════╗
║         THE SMART DOLLAR — DAILY MARKETING PACK             ║
║                      {today}                         ║
╚══════════════════════════════════════════════════════════════╝

Today's topic: {issue['headline']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠 REDDIT (copy-paste, takes 2 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Post in: {" | ".join(["r/" + s for s in reddit['subreddits']])}
Search for posts about: "{reddit['suggested_post_title']}"

YOUR COMMENT:
{reddit['comment']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐦 TWITTER / X THREAD (post as a thread)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join([f"Tweet {i+1}: {t}" for i, t in enumerate(twitter['tweets'])])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 LINKEDIN POST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{linkedin['post']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PINTEREST — Posted automatically ✅
🗞️  NEWSLETTER — Sent automatically ✅
📝 SEO BLOG — Published automatically ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    with open(f"marketing_pack_{today}.txt", "w") as f:
        f.write(content)
    print(f"✅ Marketing pack saved: marketing_pack_{today}.txt")
    return content


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n🚀 THE SMART DOLLAR — Daily Automation Starting...\n")

    # 1. Generate core content
    print("📝 Generating newsletter...")
    issue = generate_newsletter()
    print(f"   ✅ Subject: {issue['subject']}")

    # 2. Send newsletter
    print("📧 Sending newsletter to Beehiiv...")
    html = build_newsletter_html(issue)
    post_newsletter(issue, html)
    print("   ✅ Newsletter sent!")

    # 3. SEO Blog post
    print("📝 Publishing SEO blog post...")
    try:
        blog = generate_blog_post(issue)
        post_to_blogger(blog)
        print(f"   ✅ Blog post: {blog['title']}")
    except Exception as e:
        print(f"   ⏭️  Blog skipped: {e}")

    # 4. Pinterest
    print("📌 Posting to Pinterest...")
    try:
        pin = generate_pinterest_content(issue)
        post_to_pinterest(pin, issue)
        print("   ✅ Pinterest pin posted!")
    except Exception as e:
        print(f"   ⏭️  Pinterest skipped: {e}")

    # 5. Generate marketing content (saved for copy-paste)
    print("📣 Generating marketing content...")
    reddit   = generate_reddit_content(issue)
    twitter  = generate_twitter_thread(issue)
    linkedin = generate_linkedin_post(issue)

    # 6. Save daily marketing pack
    save_marketing_pack(reddit, twitter, linkedin, issue)

    print("\n🎉 DONE! Everything automated for today.")
    print(f"   Newsletter: sent ✅")
    print(f"   Blog post: published ✅")
    print(f"   Pinterest: posted ✅")
    print(f"   Reddit/Twitter/LinkedIn: saved in marketing pack ✅")
    print(f"\n   💡 Optional: Check marketing_pack_*.txt for 2-min copy-paste posts")
