import anthropic
import requests
import json
import os
import base64
import random
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY    = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID     = os.environ["BEEHIIV_PUB_ID"]
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME          = os.environ.get("REPO_NAME", "")   # e.g. "arnaudg/smart-dollar-newsletter"
PINTEREST_TOKEN    = os.environ.get("PINTEREST_TOKEN", "")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")

SUBSCRIBE_URL = "https://arnauds-newsletter-47845f.beehiiv.com"

# ── ALL AFFILIATE LINKS ───────────────────────────────────────────────────────
AFFILIATES = {
    "revolut": {
        "url":   "https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",
        "label": "Revolut", "emoji": "💳",
        "desc":  "Join 70M+ users — zero-fee banking & spending abroad",
        "tags":  ["banking", "spending", "travel", "saving", "international", "fees"],
    },
    "coinbase": {
        "url":   "https://coinbase.com/join/RSRGFEP?src=ios-link",
        "label": "Coinbase", "emoji": "₿",
        "desc":  "Start investing in crypto with as little as $2",
        "tags":  ["crypto", "bitcoin", "ethereum", "digital assets", "cryptocurrency"],
    },
    "etoro": {
        "url":   "https://etoro.tw/4vZbEOP",
        "label": "eToro", "emoji": "📈",
        "desc":  "Copy top investors automatically — investing made simple",
        "tags":  ["investing", "stocks", "portfolio", "trading", "ETF", "copy trading"],
    },
    "nordvpn": {
        "url":   "https://refer-nordvpn.com/BrJJQSzaIsM",
        "label": "NordVPN", "emoji": "🔒",
        "desc":  "Protect your finances online — one tap, all devices",
        "tags":  ["security", "privacy", "VPN", "online safety", "hacking", "protection"],
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
        "tags":  ["crypto", "trading", "altcoins", "exchange", "bitcoin"],
    },
    "alpian": {
        "url":   "https://onelink.to/download-alpian",
        "code":  "PCXTNB",
        "label": "Alpian", "emoji": "🏔️",
        "desc":  "Swiss private banking app — get CHF 25 bonus with code PCXTNB",
        "tags":  ["swiss", "private banking", "wealth", "investment", "CHF"],
    },
    "wise": {
        "url":   "https://wise.com/invite/mic/f238f6e",
        "label": "Wise", "emoji": "🌍",
        "desc":  "Send money abroad with real exchange rates — no hidden fees",
        "tags":  ["international transfer", "send money", "exchange rate", "abroad"],
    },
    "getyourguide": {
        "url":   "https://www.getyourguide.com/switzerland-l125/?partner_id=NPTQI2G&utm_medium=online_publisher",
        "label": "GetYourGuide", "emoji": "🗺️",
        "desc":  "Book amazing activities and tours across Switzerland",
        "tags":  ["travel", "activities", "tours", "switzerland", "tourism", "experiences", "holidays"],
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
# 1. GENERATE NEWSLETTER CONTENT
# ══════════════════════════════════════════════════════════════════════════════
def generate_newsletter():
    today    = datetime.now().strftime("%B %d, %Y")
    aff_list = "\n".join([f'- "{k}": topics={v["tags"]}' for k, v in AFFILIATES.items()])

    prompt = f"""Write today's issue of "The Smart Dollar" newsletter for a Swiss/European audience.
Date: {today}

Available affiliate partners and their relevant topics:
{aff_list}

Return ONLY a JSON object:
{{
  "subject": "catchy email subject under 60 chars",
  "headline": "main headline",
  "intro": "2-3 sentence warm intro",
  "story1_tag": "MONEY TIP",
  "story1_title": "title",
  "story1_body": "3-4 sentences with specific numbers or percentages",
  "story1_affiliate": null or one affiliate key,
  "story2_tag": "AI SPOTLIGHT",
  "story2_title": "title about an AI tool saving money or time",
  "story2_body": "3-4 sentences",
  "story2_affiliate": null or one affiliate key,
  "story3_tag": "INVEST SMART",
  "story3_title": "investing title, Switzerland-relevant",
  "story3_body": "3-4 sentences",
  "story3_affiliate": null or one affiliate key,
  "quick_tip": "one punchy tip of the day",
  "seo_keyword": "2-4 word keyword this targets"
}}

Rules: each affiliate used max once, match to topic naturally, Swiss/European focus."""

    return json.loads(claude(prompt))


# ══════════════════════════════════════════════════════════════════════════════
# 2. BUILD NEWSLETTER HTML
# ══════════════════════════════════════════════════════════════════════════════
def build_html(issue):
    today = datetime.now().strftime("%B %d, %Y")

    def aff_block(key):
        if not key or key not in AFFILIATES:
            return ""
        a = AFFILIATES[key]
        code_html = f"<p style='margin:4px 0 6px;font-size:12px;color:#888;'>🎁 Use code: <strong>{a['code']}</strong></p>" if a.get("code") else ""
        return f"""<div style="margin-top:14px;background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:14px;">
          <p style="margin:0 0 4px;font-size:14px;color:#555;">{a['emoji']} <strong>{a['label']}</strong> — {a['desc']}</p>
          {code_html}
          <a href="{a['url']}" style="display:inline-block;background:#1a1a2e;color:#ffd700;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:700;text-decoration:none;margin-top:4px;">Try {a['label']} →</a>
        </div>"""

    # Body-only HTML — no DOCTYPE/html/head tags — works perfectly in Beehiiv editor
    return f"""<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#1a1a2e;">
  <div style="text-align:center;padding:20px 0 16px;border-bottom:3px solid #ffd700;margin-bottom:24px;">
    <p style="font-size:13px;color:#888;margin:0;">{today} · Finance & AI for Smart People</p>
  </div>
  <p style="font-size:15px;color:#555;line-height:1.8;margin-bottom:24px;">{issue['intro']}</p>
  <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:18px 20px;border-radius:0 8px 8px 0;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#16a34a;letter-spacing:2px;">{issue['story1_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0 10px;">{issue['story1_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue['story1_body']}</p>
    {aff_block(issue.get('story1_affiliate'))}
  </div>
  <div style="background:#eff6ff;border-left:4px solid #2563eb;padding:18px 20px;border-radius:0 8px 8px 0;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#2563eb;letter-spacing:2px;">{issue['story2_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0 10px;">{issue['story2_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue['story2_body']}</p>
    {aff_block(issue.get('story2_affiliate'))}
  </div>
  <div style="background:#fefce8;border-left:4px solid #ca8a04;padding:18px 20px;border-radius:0 8px 8px 0;margin-bottom:20px;">
    <span style="font-size:10px;font-weight:800;color:#ca8a04;letter-spacing:2px;">{issue['story3_tag']}</span>
    <h3 style="font-size:18px;font-weight:800;margin:8px 0 10px;">{issue['story3_title']}</h3>
    <p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue['story3_body']}</p>
    {aff_block(issue.get('story3_affiliate'))}
  </div>
  <div style="background:#1a1a2e;color:#fff;padding:18px 24px;border-radius:12px;text-align:center;margin-bottom:24px;">
    <p style="font-size:11px;opacity:0.6;margin:0 0 6px;letter-spacing:2px;">💡 TIP OF THE DAY</p>
    <p style="font-size:15px;font-weight:700;margin:0;line-height:1.5;">{issue['quick_tip']}</p>
  </div>
  <div style="text-align:center;padding:16px 0;border-top:1px solid #eee;">
    <p style="font-size:14px;color:#888;margin:0 0 10px;">Share The Smart Dollar with a friend 👇</p>
    <a href="{SUBSCRIBE_URL}" style="display:inline-block;background:#ffd700;color:#1a1a2e;padding:12px 28px;border-radius:8px;font-weight:800;font-size:14px;text-decoration:none;">Subscribe Free →</a>
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 3. SAVE NEWSLETTER TO GITHUB (replaces Beehiiv API — free plan compatible)
# ══════════════════════════════════════════════════════════════════════════════
def save_newsletter_to_github(issue, html):
    """Saves the newsletter HTML to the repo so you can copy-paste into Beehiiv."""
    if not GITHUB_TOKEN or not REPO_NAME:
        print("   ⚠️  GITHUB_TOKEN or REPO_NAME missing, saving locally only")
        today = datetime.now().strftime("%Y-%m-%d")
        with open(f"newsletter_{today}.html", "w") as f:
            f.write(html)
        return

    today    = datetime.now().strftime("%Y-%m-%d")
    filename = f"newsletters/newsletter_{today}.html"
    api_url  = f"https://api.github.com/repos/{REPO_NAME}/contents/{filename}"
    headers  = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github+json",
    }

    # Check if file exists (to get SHA for update)
    sha = None
    existing = requests.get(api_url, headers=headers)
    if existing.ok:
        sha = existing.json().get("sha")

    data = {
        "message": f"Newsletter: {issue['subject']}",
        "content": base64.b64encode(html.encode()).decode(),
        "branch":  "main",
    }
    if sha:
        data["sha"] = sha

    # Also save a plain-text instructions file alongside the HTML
    instructions = f"""
==================================================
THE SMART DOLLAR — {today}
==================================================

STEP 1 — Go to app.beehiiv.com → click "+ New Post"

STEP 2 — TITLE (paste this in the title field):
{issue['subject']}

STEP 3 — SUBTITLE (paste this in the subtitle field):
{issue['headline']}

STEP 4 — BODY (paste the HTML):
• Open the .html file in this folder
• Click "Raw" button → Select All → Copy
• In Beehiiv editor: click "/" → search "HTML block" → paste

STEP 5 — Click "Next" → "Send" → Done! 🎉
==================================================
"""
    inst_filename = f"newsletters/HOW_TO_POST_{today}.txt"
    inst_api_url  = f"https://api.github.com/repos/{REPO_NAME}/contents/{inst_filename}"

    r = requests.put(api_url, headers=headers, json=data)
    if r.ok:
        print(f"   ✅ Newsletter HTML saved: {filename}")
        # Also save instructions file
        inst_data = {"message": f"Instructions: {today}", "content": base64.b64encode(instructions.encode()).decode(), "branch": "main"}
        existing_inst = requests.get(inst_api_url, headers=headers)
        if existing_inst.ok:
            inst_data["sha"] = existing_inst.json().get("sha")
        requests.put(inst_api_url, headers=headers, json=inst_data)
        print(f"   ✅ Instructions saved!")
        print(f"   👉 GitHub → newsletters/ folder → open HOW_TO_POST_{today}.txt")
        print(f"   📋 TITLE: {issue['subject']}")
        print(f"   📋 SUBTITLE: {issue['headline']}")
    else:
        print(f"   ⚠️  GitHub save failed: {r.status_code} — {r.text[:150]}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. SEO BLOG POST → GitHub Pages
# ══════════════════════════════════════════════════════════════════════════════
def generate_and_publish_blog(issue):
    aff_keys = random.sample(list(AFFILIATES.keys()), 2)
    aff_info = "\n".join([f"- {AFFILIATES[k]['label']}: {AFFILIATES[k]['desc']} — {AFFILIATES[k]['url']}" for k in aff_keys])

    prompt = f"""Write a 500-word SEO blog post targeting: "{issue['seo_keyword']}"
Swiss/European audience. Include newsletter link: {SUBSCRIBE_URL}
Naturally include these affiliates: {aff_info}

Return JSON:
{{
  "title": "SEO title with keyword",
  "slug": "url-friendly-slug",
  "meta_description": "155 char meta description",
  "html_body": "full blog post HTML with h2s, paragraphs, affiliate links"
}}"""

    blog = json.loads(claude(prompt, max_tokens=2000))

    if not GITHUB_TOKEN or not REPO_NAME:
        print("   ⏭️  GitHub not configured, skipping blog")
        return

    today    = datetime.now().strftime("%Y-%m-%d")
    filename = f"blog/{today}-{blog['slug']}.html"
    api_url  = f"https://api.github.com/repos/{REPO_NAME}/contents/{filename}"
    headers  = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{blog['title']} | The Smart Dollar</title>
  <meta name="description" content="{blog['meta_description']}">
  <style>
    body{{font-family:Georgia,serif;max-width:700px;margin:40px auto;padding:0 20px;color:#1a1a2e;line-height:1.8;}}
    h1{{font-size:2em;font-weight:900;border-bottom:3px solid #ffd700;padding-bottom:12px;}}
    h2{{font-size:1.4em;font-weight:800;margin-top:2em;}}
    a{{color:#2563eb;}}
    .cta{{background:#1a1a2e;color:#fff;padding:20px;border-radius:10px;text-align:center;margin:2em 0;}}
    .cta a{{color:#ffd700;font-weight:700;font-size:1.1em;}}
    .date{{color:#888;font-size:0.9em;margin-bottom:2em;}}
  </style>
</head>
<body>
  <p><a href="/">← The Smart Dollar</a></p>
  <h1>{blog['title']}</h1>
  <p class="date">Published {datetime.now().strftime("%B %d, %Y")}</p>
  {blog['html_body']}
  <div class="cta">
    <p style="margin:0 0 10px;opacity:0.8;">Get daily money tips — free.</p>
    <a href="{SUBSCRIBE_URL}">Subscribe to The Smart Dollar →</a>
  </div>
</body>
</html>"""

    data = {"message": f"Blog: {blog['title']}", "content": base64.b64encode(full_html.encode()).decode(), "branch": "gh-pages"}
    r = requests.put(api_url, headers=headers, json=data)
    if r.ok:
        print(f"   ✅ Blog post published: {filename}")
    else:
        print(f"   ⚠️  Blog skipped: {r.status_code} — {r.text[:100]}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. PINTEREST
# ══════════════════════════════════════════════════════════════════════════════
def post_to_pinterest(issue):
    if not PINTEREST_TOKEN or not PINTEREST_BOARD_ID:
        print("   ⏭️  Pinterest not configured yet, skipping")
        return

    prompt = f"""Pinterest pin for finance tip:
Headline: {issue['headline']}
Tip: {issue['quick_tip']}
JSON: {{"title": "under 100 chars", "description": "200-400 chars + hashtags #PersonalFinance #SwissFinance #MoneyTips #Investing #FinancialFreedom"}}"""

    pin = json.loads(claude(prompt, max_tokens=300))
    image_url = f"https://picsum.photos/seed/{datetime.now().strftime('%Y%m%d')}/800/1200"

    r = requests.post("https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {PINTEREST_TOKEN}", "Content-Type": "application/json"},
        json={
            "board_id":     PINTEREST_BOARD_ID,
            "title":        pin["title"],
            "description":  pin["description"] + f"\n\n🔗 Free newsletter: {SUBSCRIBE_URL}",
            "media_source": {"source_type": "image_url", "url": image_url},
            "link":         SUBSCRIBE_URL,
        })
    if r.ok:
        print("   ✅ Pinterest pin posted!")
    else:
        print(f"   ⚠️  Pinterest skipped: {r.status_code} — {r.text[:100]}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. MARKETING PACK
# ══════════════════════════════════════════════════════════════════════════════
def generate_marketing_pack(issue):
    aff_keys = [issue.get(f"story{i}_affiliate") for i in range(1,4) if issue.get(f"story{i}_affiliate")]
    primary  = AFFILIATES[aff_keys[0]] if aff_keys else AFFILIATES["etoro"]

    reddit_r  = json.loads(claude(f"""Helpful Reddit comment about "{issue['seo_keyword']}".
Based on: {issue['story1_body']}
Mention {primary['label']} naturally if relevant.
End with: "I write a free newsletter on this: {SUBSCRIBE_URL}"
Max 120 words. No headers.
Suggest 3 subreddits.
JSON: {{"comment":"text","subreddits":["s1","s2","s3"],"search_query":"what to search for"}}""", 400))

    twitter_r = json.loads(claude(f"""5-tweet thread about "{issue['headline']}".
Insights: {issue['story1_body'][:150]} / {issue['story2_body'][:150]}
Tip: {issue['quick_tip']}
Last tweet: subscribe at {SUBSCRIBE_URL} + hashtags #PersonalFinance #SwissFinance #MoneyTips
JSON: {{"tweets":["t1","t2","t3","t4","t5"]}}""", 500))

    linkedin_r = json.loads(claude(f"""LinkedIn post about "{issue['headline']}".
Insight: {issue['story1_body']}
CTA: subscribe at {SUBSCRIBE_URL}
150-180 words. Don't start with "I". 4 hashtags at end.
JSON: {{"post":"text"}}""", 350))

    today   = datetime.now().strftime("%Y-%m-%d")
    content = f"""
╔══════════════════════════════════════════════════════════════╗
║         THE SMART DOLLAR — DAILY MARKETING PACK             ║
║                      {today}                         ║
╚══════════════════════════════════════════════════════════════╝

Topic: {issue['headline']}
Subscribe link: {SUBSCRIBE_URL}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗞️  BEEHIIV — Post today's newsletter (30 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to: https://github.com/{REPO_NAME}/tree/main/newsletters
2. Open today's newsletter_{today}.html file
3. Click "Raw" → Select all → Copy
4. Go to app.beehiiv.com → New Post → click "</>" HTML button
5. Paste → click back to visual editor → set subject: {issue['subject']}
6. Click Send!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠 REDDIT — 2 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Post in: {" | ".join(["r/"+s for s in reddit_r["subreddits"]])}
Search for: "{reddit_r["search_query"]}"

{reddit_r["comment"]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐦 TWITTER/X THREAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f"Tweet {i+1}:{chr(10)}{t}{chr(10)}" for i,t in enumerate(twitter_r["tweets"])])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 LINKEDIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{linkedin_r["post"]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTO-COMPLETED: Blog ✅  Pinterest ✅  Newsletter saved ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    with open(f"marketing_pack_{today}.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"   ✅ Marketing pack saved!")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n🚀 THE SMART DOLLAR — Daily Automation v3\n")

    print("📝 Generating newsletter...")
    issue = generate_newsletter()
    print(f"   ✅ Subject: {issue['subject']}")

    html = build_html(issue)

    print("💾 Saving newsletter to GitHub...")
    save_newsletter_to_github(issue, html)

    print("📝 Publishing SEO blog post...")
    try:
        generate_and_publish_blog(issue)
    except Exception as e:
        print(f"   ⚠️  Blog skipped: {e}")

    print("📌 Posting to Pinterest...")
    try:
        post_to_pinterest(issue)
    except Exception as e:
        print(f"   ⚠️  Pinterest skipped: {e}")

    print("📣 Generating marketing pack...")
    try:
        generate_marketing_pack(issue)
    except Exception as e:
        print(f"   ⚠️  Marketing pack skipped: {e}")

    print("\n🎉 ALL DONE!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Newsletter → saved to GitHub/newsletters/")
    print("✅ Blog post  → published to GitHub Pages")
    print("✅ Pinterest  → auto-posted")
    print("✅ Marketing  → download artifact in Actions")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n👉 To send newsletter: open GitHub → newsletters folder → copy HTML → paste into Beehiiv")
