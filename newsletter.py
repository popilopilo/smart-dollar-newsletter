import anthropic
import requests
import json
import os
import base64
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
BEEHIIV_API_KEY    = os.environ["BEEHIIV_API_KEY"]
BEEHIIV_PUB_ID     = os.environ["BEEHIIV_PUB_ID"]
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME          = os.environ.get("REPO_NAME", "")
PINTEREST_TOKEN    = os.environ.get("PINTEREST_TOKEN", "")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")
TWITTER_API_KEY        = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET     = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN   = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET  = os.environ.get("TWITTER_ACCESS_SECRET", "")

SUBSCRIBE_URL = "https://arnauds-newsletter-47845f.beehiiv.com"

AFFILIATES = {
    "revolut":      {"url": "https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",              "label": "Revolut",      "emoji": "💳", "code": None,     "desc": "Zero-fee banking for 70M+ users",              "tags": ["banking","spending","travel","saving","international"]},
    "coinbase":     {"url": "https://coinbase.com/join/RSRGFEP?src=ios-link",                                                  "label": "Coinbase",     "emoji": "₿",  "code": None,     "desc": "Start investing in crypto from $2",            "tags": ["crypto","bitcoin","ethereum","digital assets"]},
    "etoro":        {"url": "https://etoro.tw/4vZbEOP",                                                                        "label": "eToro",        "emoji": "📈", "code": None,     "desc": "Copy top investors automatically",             "tags": ["investing","stocks","portfolio","trading","ETF"]},
    "nordvpn":      {"url": "https://refer-nordvpn.com/BrJJQSzaIsM",                                                          "label": "NordVPN",      "emoji": "🔒", "code": None,     "desc": "Protect your finances online",                 "tags": ["security","privacy","VPN","online safety"]},
    "neon":         {"url": "http://onelink.to/neon",                                                                          "label": "Neon",         "emoji": "🇨🇭", "code": "SDB98A", "desc": "Switzerland's best free bank account",         "tags": ["swiss bank","switzerland","free account","CHF"]},
    "yuh":          {"url": "https://www.yuh.com/download",                                                                    "label": "Yuh",          "emoji": "💰", "code": "uzwi60", "desc": "Pay, save and invest — one Swiss app",         "tags": ["swiss","invest","save","pay"]},
    "binance":      {"url": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00Z6UROXWP",                         "label": "Binance",      "emoji": "🟡", "code": None,     "desc": "World's largest crypto exchange",              "tags": ["crypto","trading","altcoins","exchange"]},
    "alpian":       {"url": "https://onelink.to/download-alpian",                                                              "label": "Alpian",       "emoji": "🏔️", "code": "PCXTNB", "desc": "Swiss private banking — CHF 25 bonus",         "tags": ["swiss","private banking","wealth","CHF"]},
    "wise":         {"url": "https://wise.com/invite/mic/f238f6e",                                                             "label": "Wise",         "emoji": "🌍", "code": None,     "desc": "Real exchange rates, no hidden fees",          "tags": ["international transfer","send money","exchange rate"]},
    "getyourguide": {"url": "https://www.getyourguide.com/switzerland-l125/?partner_id=NPTQI2G&utm_medium=online_publisher",  "label": "GetYourGuide", "emoji": "🗺️", "code": None,     "desc": "Book amazing Swiss activities & tours",        "tags": ["travel","activities","tours","switzerland","tourism"]},
}

TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_LONG = datetime.now().strftime("%B %d, %Y")

def ai(prompt, max_tokens=1500):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    return raw.replace("```json", "").replace("```", "").strip()

def ai_json(prompt, max_tokens=1500):
    return json.loads(ai(prompt, max_tokens))

# ══════════════════════════════════════════════════════════════════════════
# 1. GENERATE NEWSLETTER CONTENT
# ══════════════════════════════════════════════════════════════════════════
def generate_issue():
    aff_list = "\n".join([f'  "{k}": {v["tags"]}' for k, v in AFFILIATES.items()])
    r = ai_json(
        f'Write today\'s "The Smart Dollar" newsletter for Swiss/European readers.\n'
        f'Date: {TODAY_LONG}\n\n'
        f'Affiliates available:\n{aff_list}\n\n'
        'Return ONLY this JSON:\n'
        '{\n'
        '  "subject": "email subject line, max 60 chars, curiosity-driven",\n'
        '  "headline": "main headline, punchy",\n'
        '  "intro": "2-3 sentences, warm, specific to today",\n'
        '  "story1_tag": "MONEY TIP",\n'
        '  "story1_title": "title",\n'
        '  "story1_body": "3-4 sentences, specific numbers, actionable",\n'
        '  "story1_affiliate": null or affiliate key,\n'
        '  "story2_tag": "AI SPOTLIGHT",\n'
        '  "story2_title": "title",\n'
        '  "story2_body": "3-4 sentences, specific AI tool",\n'
        '  "story2_affiliate": null or affiliate key,\n'
        '  "story3_tag": "INVEST SMART",\n'
        '  "story3_title": "title",\n'
        '  "story3_body": "3-4 sentences, Switzerland-relevant",\n'
        '  "story3_affiliate": null or affiliate key,\n'
        '  "quick_tip": "one punchy tip, specific",\n'
        '  "seo_keyword": "2-4 word keyword"\n'
        '}\n\n'
        'Rules: max one use per affiliate, match naturally to topic, include real numbers.'
    )
    return r

# ══════════════════════════════════════════════════════════════════════════
# 2. BUILD NEWSLETTER HTML (body-only for Beehiiv)
# ══════════════════════════════════════════════════════════════════════════
def build_html(issue):
    def aff(key):
        if not key or key not in AFFILIATES:
            return ""
        a = AFFILIATES[key]
        code = f'<p style="margin:3px 0 6px;font-size:12px;color:#888;">Use code: <strong>{a["code"]}</strong></p>' if a.get("code") else ""
        return (
            f'<div style="margin-top:12px;background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px;">'
            f'<p style="margin:0 0 3px;font-size:13px;color:#555;">{a["emoji"]} <strong>{a["label"]}</strong> — {a["desc"]}</p>'
            f'{code}'
            f'<a href="{a["url"]}" style="display:inline-block;background:#1a1a2e;color:#ffd700;padding:7px 14px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none;margin-top:4px;">Try {a["label"]} →</a>'
            f'</div>'
        )

    return (
        f'<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#1a1a2e;">'
        f'<div style="text-align:center;padding:16px 0;border-bottom:3px solid #ffd700;margin-bottom:20px;">'
        f'<p style="font-size:12px;color:#888;margin:0;">{TODAY_LONG} · Finance &amp; AI for Smart People</p>'
        f'</div>'
        f'<p style="font-size:15px;color:#555;line-height:1.8;margin-bottom:20px;">{issue["intro"]}</p>'
        f'<div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#16a34a;letter-spacing:2px;">{issue["story1_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story1_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story1_body"]}</p>'
        f'{aff(issue.get("story1_affiliate"))}'
        f'</div>'
        f'<div style="background:#eff6ff;border-left:4px solid #2563eb;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#2563eb;letter-spacing:2px;">{issue["story2_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story2_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story2_body"]}</p>'
        f'{aff(issue.get("story2_affiliate"))}'
        f'</div>'
        f'<div style="background:#fefce8;border-left:4px solid #ca8a04;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#ca8a04;letter-spacing:2px;">{issue["story3_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story3_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story3_body"]}</p>'
        f'{aff(issue.get("story3_affiliate"))}'
        f'</div>'
        f'<div style="background:#1a1a2e;color:#fff;padding:16px 20px;border-radius:10px;text-align:center;margin-bottom:20px;">'
        f'<p style="font-size:10px;opacity:0.6;margin:0 0 5px;letter-spacing:2px;">TIP OF THE DAY</p>'
        f'<p style="font-size:14px;font-weight:700;margin:0;line-height:1.5;">{issue["quick_tip"]}</p>'
        f'</div>'
        f'<div style="text-align:center;padding:14px 0;border-top:1px solid #eee;">'
        f'<p style="font-size:13px;color:#888;margin:0 0 8px;">Share The Smart Dollar with a friend</p>'
        f'<a href="{SUBSCRIBE_URL}" style="display:inline-block;background:#ffd700;color:#1a1a2e;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;text-decoration:none;">Subscribe Free</a>'
        f'</div>'
        f'</div>'
    )

# ══════════════════════════════════════════════════════════════════════════
# 3. SAVE TO GITHUB
# ══════════════════════════════════════════════════════════════════════════
def save_to_github(content, filename, message, branch="main"):
    if not GITHUB_TOKEN or not REPO_NAME:
        return False
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{filename}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    sha = None
    ex = requests.get(api_url, headers=headers)
    if ex.ok:
        sha = ex.json().get("sha")
    data = {"message": message, "content": base64.b64encode(content.encode()).decode(), "branch": branch}
    if sha:
        data["sha"] = sha
    r = requests.put(api_url, headers=headers, json=data)
    return r.ok

# ══════════════════════════════════════════════════════════════════════════
# 4. POST TO TWITTER/X (fully automated if keys provided)
# ══════════════════════════════════════════════════════════════════════════
def post_twitter_thread(tweets):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        print("   Twitter not configured, skipping auto-post")
        return False
    try:
        import hmac, hashlib, time, uuid
        from urllib.parse import quote

        def oauth_header(method, url, params):
            oauth_params = {
                "oauth_consumer_key": TWITTER_API_KEY,
                "oauth_nonce": uuid.uuid4().hex,
                "oauth_signature_method": "HMAC-SHA1",
                "oauth_timestamp": str(int(time.time())),
                "oauth_token": TWITTER_ACCESS_TOKEN,
                "oauth_version": "1.0",
            }
            all_params = {**params, **oauth_params}
            sorted_params = "&".join([f"{quote(k, safe='')}={quote(str(v), safe='')}" for k, v in sorted(all_params.items())])
            base = f"{method}&{quote(url, safe='')}&{quote(sorted_params, safe='')}"
            key = f"{quote(TWITTER_API_SECRET, safe='')}&{quote(TWITTER_ACCESS_SECRET, safe='')}"
            sig = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
            oauth_params["oauth_signature"] = sig
            return "OAuth " + ", ".join([f'{k}="{quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items())])

        url = "https://api.twitter.com/2/tweets"
        last_id = None
        for tweet in tweets:
            body = {"text": tweet}
            if last_id:
                body["reply"] = {"in_reply_to_tweet_id": last_id}
            hdrs = {"Authorization": oauth_header("POST", url, {}), "Content-Type": "application/json"}
            r = requests.post(url, headers=hdrs, json=body)
            if r.ok:
                last_id = r.json()["data"]["id"]
            else:
                print(f"   Twitter error: {r.status_code}")
                return False
        print("   Twitter thread posted automatically!")
        return True
    except Exception as e:
        print(f"   Twitter auto-post failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════
# 5. PINTEREST (fully automated)
# ══════════════════════════════════════════════════════════════════════════
def post_to_pinterest(issue):
    if not PINTEREST_TOKEN or not PINTEREST_BOARD_ID:
        print("   Pinterest not configured, skipping")
        return
    pin = ai_json(
        f'Pinterest pin for: {issue["headline"]}\nTip: {issue["quick_tip"]}\n'
        'JSON: {"title":"under 100 chars","description":"200-400 chars + hashtags #PersonalFinance #SwissFinance #MoneyTips #Investing #FinancialFreedom #Switzerland #CHF"}',
        300
    )
    image_url = f"https://picsum.photos/seed/{TODAY}/800/1200"
    r = requests.post(
        "https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {PINTEREST_TOKEN}", "Content-Type": "application/json"},
        json={"board_id": PINTEREST_BOARD_ID, "title": pin["title"],
              "description": pin["description"] + f"\n\nFree newsletter: {SUBSCRIBE_URL}",
              "media_source": {"source_type": "image_url", "url": image_url}, "link": SUBSCRIBE_URL}
    )
    print("   Pinterest: " + ("posted!" if r.ok else f"skipped ({r.status_code})"))

# ══════════════════════════════════════════════════════════════════════════
# 6. GENERATE ALL MARKETING CONTENT
# ══════════════════════════════════════════════════════════════════════════
def generate_all_content(issue):
    aff_keys = [issue.get(f"story{i}_affiliate") for i in range(1,4) if issue.get(f"story{i}_affiliate")]
    primary  = AFFILIATES[aff_keys[0]] if aff_keys else AFFILIATES["etoro"]
    kw       = issue["seo_keyword"]
    s1       = issue["story1_body"][:200]
    s2       = issue["story2_body"][:200]

    print("   Generating meta description...")
    meta = ai(
        f'Meta description for newsletter titled: {issue["subject"]}\n'
        f'Content: {s1[:80]}\n'
        f'140-150 chars. Compelling. Keyword: {kw}. End with: Free daily newsletter.\n'
        'Return ONLY the description, no quotes.',
        120
    ).strip().strip('"')

    print("   Generating Twitter thread...")
    twitter = ai_json(
        f'5-tweet thread about: {issue["headline"]}\n'
        f'Insight 1: {s1}\nInsight 2: {s2}\nTip: {issue["quick_tip"]}\n'
        f'Tweet 1: strong hook, no "Thread:"\n'
        f'Tweets 2-4: one insight each, under 280 chars, specific numbers\n'
        f'Tweet 5: CTA + {SUBSCRIBE_URL} + hashtags #PersonalFinance #SwissFinance #CHF #MoneyTips\n'
        'JSON: {"tweets":["t1","t2","t3","t4","t5"]}',
        600
    )

    print("   Generating Reddit comment...")
    reddit = ai_json(
        f'Helpful Reddit comment about: {kw}\n'
        f'Based on: {s1}\n'
        f'Mention {primary["label"]} naturally only if very relevant.\n'
        f'End: "I cover this free in my newsletter: {SUBSCRIBE_URL}"\n'
        'Max 130 words. Sound like a real helpful person. No headers.\n'
        'Suggest 4 best subreddits (include r/eupersonalfinance and r/Switzerland).\n'
        'JSON: {"comment":"text","subreddits":["s1","s2","s3","s4"],"search":"what to search for"}',
        500
    )

    print("   Generating Instagram caption...")
    insta = ai_json(
        f'Instagram caption for: {issue["headline"]}\n'
        f'Hook: {s1[:80]}\n'
        '3 bullet points of value. End with "Link in bio to subscribe free"\n'
        'Include 20 hashtags: #SwissFinance #Switzerland #Schweiz #Investing #PersonalFinance #MoneyTips #CHF #FinanceTips #SmartMoney #Expat #SwissLife #Finanzen #Geldtipps #Sparen #Investieren #Passiveincome #FinancialFreedom #WealthBuilding #CryptoSwiss #FinanceDaily\n'
        'JSON: {"caption":"text"}',
        500
    )

    print("   Generating Quora answer...")
    quora = ai_json(
        f'Quora answer about: {kw}\n'
        f'Based on: {s1}\n'
        'Expert tone, lives in Switzerland, 180-220 words.\n'
        f'End: "I cover this in my free newsletter: {SUBSCRIBE_URL}"\n'
        'JSON: {"answer":"text","question":"exact Quora question to search for"}',
        500
    )

    print("   Generating WhatsApp/Telegram message...")
    whatsapp = ai_json(
        f'Short WhatsApp message sharing: {issue["headline"]}\n'
        f'Key fact: {s1[:80]}\n'
        f'Link: {SUBSCRIBE_URL}\n'
        '2-3 sentences max. Casual and friendly. No hashtags.\n'
        'JSON: {"message":"text"}',
        200
    )

    print("   Generating TikTok script...")
    tiktok = ai_json(
        f'60-second TikTok/Reels script about: {issue["headline"]}\n'
        f'Key insight: {s1}\n'
        'Format: Hook (5 sec) -> Problem (10 sec) -> Solution (30 sec) -> CTA (15 sec)\n'
        f'CTA: subscribe at {SUBSCRIBE_URL}\n'
        'Include on-screen text suggestions in brackets.\n'
        'JSON: {"script":"full script text","hook":"first 5 seconds only","hashtags":"20 relevant hashtags"}',
        600
    )

    print("   Generating YouTube Shorts script...")
    youtube = ai_json(
        f'YouTube Shorts script (60 sec) about: {issue["headline"]}\n'
        f'Key insight: {s1}\n'
        'Energetic, educational. Hook must grab in first 3 seconds.\n'
        f'End with: subscribe at {SUBSCRIBE_URL}\n'
        'JSON: {"title":"YouTube title with keyword","script":"full script","description":"video description with keywords"}',
        500
    )

    print("   Generating email subject line variants...")
    subjects = ai_json(
        f'5 different email subject line variants for newsletter about: {issue["headline"]}\n'
        f'Audience: Swiss/European finance readers\n'
        'Make them: curious, urgent, specific, numbered, question-based (one each)\n'
        'All under 60 chars.\n'
        'JSON: {"subjects":["s1","s2","s3","s4","s5"]}',
        300
    )

    return {
        "meta": meta,
        "twitter": twitter,
        "reddit": reddit,
        "insta": insta,
        "quora": quora,
        "whatsapp": whatsapp,
        "tiktok": tiktok,
        "youtube": youtube,
        "subjects": subjects,
    }

# ══════════════════════════════════════════════════════════════════════════
# 7. SAVE COMPLETE DAILY PACK
# ══════════════════════════════════════════════════════════════════════════
def save_daily_pack(issue, content):
    twit = content["twitter"]["tweets"]
    reddit = content["reddit"]
    insta = content["insta"]
    quora = content["quora"]
    wa = content["whatsapp"]
    tiktok = content["tiktok"]
    yt = content["youtube"]
    subjects = content["subjects"]["subjects"]
    meta = content["meta"]

    canva_title    = issue["subject"][:50]
    canva_subtitle = issue["headline"][:55]

    lines = [
        "THE SMART DOLLAR - COMPLETE DAILY PACK",
        "Date: " + TODAY,
        "================================================================",
        "",
        "AUTOMATED TODAY (nothing to do):",
        "  [AUTO] Newsletter HTML saved to GitHub/newsletters/",
        "  [AUTO] Pinterest pin posted",
        "  [AUTO] Twitter thread posted (if keys configured)",
        "",
        "================================================================",
        "STEP 1 - CANVA THUMBNAIL (2 min)",
        "================================================================",
        "Open your saved Canva template, change these 2 lines:",
        "  TITLE:    " + canva_title,
        "  SUBTITLE: " + canva_subtitle,
        "Download as PNG - you will upload it in step 2.",
        "",
        "================================================================",
        "STEP 2 - BEEHIIV NEWSLETTER (5 min)",
        "================================================================",
        "1. GitHub -> newsletters/ -> newsletter_" + TODAY + ".html -> Raw -> Select All -> Copy",
        "2. app.beehiiv.com -> click + New Post",
        "3. TITLE (paste):    " + issue["subject"],
        "4. SUBTITLE (paste): " + issue["headline"],
        "5. Click in body -> type / -> choose HTML block -> paste",
        "6. Click Next -> Audience: Email and web, All subscribers",
        "7. Click Next -> Email step: subject line auto-filled",
        "   ALTERNATIVE SUBJECT LINES (A/B test these):",
    ]
    for i, s in enumerate(subjects):
        lines.append("     " + str(i+1) + ". " + s)
    lines += [
        "8. Click Next -> Web settings:",
        "   - Advanced email capture: Popup",
        "   - Show thumbnail on top: ON",
        "   - Feature the post: ON",
        "   - Upload your Canva thumbnail",
        "9. META DESCRIPTION (paste in all 3 SEO fields - SEO, Facebook, Twitter):",
        "   " + meta,
        "10. Click Next -> Review -> SEND",
        "",
        "================================================================",
        "STEP 3 - REDDIT (2 min) - MOST POWERFUL FOR GROWTH",
        "================================================================",
        "WHERE: " + " | ".join(["r/" + s for s in reddit["subreddits"]]),
        "HOW: Go to subreddit -> search '" + reddit["search"] + "'",
        "     Find any post with comments -> click Reply -> paste this:",
        "",
        "--- COPY ---",
        reddit["comment"],
        "--- END ---",
        "",
        "TIP: Post in 2 different subreddits for double the reach.",
        "",
        "================================================================",
        "STEP 4 - TWITTER/X THREAD (2 min if not auto-posted)",
        "================================================================",
        "HOW: Post tweet 1 -> reply to it with tweet 2 -> etc.",
        "",
    ]
    for i, t in enumerate(twit):
        lines.append("--- Tweet " + str(i+1) + " ---")
        lines.append(t)
        lines.append("")
    lines += [
        "================================================================",
        "STEP 5 - INSTAGRAM (2 min)",
        "================================================================",
        "HOW: Open Instagram -> + New Post -> upload Canva thumbnail",
        "     Paste this caption:",
        "",
        "--- COPY ---",
        insta["caption"],
        "--- END ---",
        "",
        "================================================================",
        "STEP 6 - TIKTOK / REELS (3 min - film yourself reading this)",
        "================================================================",
        "HOW: Open TikTok or Instagram Reels -> film a 60-second video",
        "     You can just read this script to your phone camera:",
        "",
        "HOOK (first 5 sec, say this first):",
        tiktok["hook"],
        "",
        "FULL SCRIPT:",
        tiktok["script"],
        "",
        "HASHTAGS TO ADD:",
        tiktok["hashtags"],
        "",
        "TIP: You don't need to be perfect. Finance TikToks filmed simply",
        "     often outperform polished ones. Just talk naturally.",
        "",
        "================================================================",
        "STEP 7 - YOUTUBE SHORTS (3 min - same video as TikTok!)",
        "================================================================",
        "HOW: Upload the same video you filmed for TikTok to YouTube Shorts",
        "     Use this title and description:",
        "",
        "TITLE: " + yt["title"],
        "",
        "DESCRIPTION:",
        yt["description"],
        "",
        "TIP: Film once, post to TikTok + YouTube Shorts + Instagram Reels",
        "     = 3 platforms, 1 video, 3 minutes total.",
        "",
        "================================================================",
        "STEP 8 - QUORA (3 min - answers rank on Google!)",
        "================================================================",
        "HOW: quora.com -> search '" + quora["question"] + "'",
        "     Click on the question -> click Answer -> paste:",
        "",
        "--- COPY ---",
        quora["answer"],
        "--- END ---",
        "",
        "================================================================",
        "STEP 9 - WHATSAPP / TELEGRAM (30 sec)",
        "================================================================",
        "Send to any finance/expat/Switzerland groups you are in:",
        "",
        "--- COPY ---",
        wa["message"],
        "--- END ---",
        "",
        "================================================================",
        "YOUR AFFILIATE LINKS",
        "================================================================",
        "Revolut (banking):    https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",
        "Coinbase (crypto):    https://coinbase.com/join/RSRGFEP?src=ios-link",
        "eToro (investing):    https://etoro.tw/4vZbEOP",
        "NordVPN (security):   https://refer-nordvpn.com/BrJJQSzaIsM",
        "Neon (Swiss bank):    http://onelink.to/neon  [code: SDB98A]",
        "Yuh (Swiss invest):   https://www.yuh.com/download  [code: uzwi60]",
        "Binance (crypto):     https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00Z6UROXWP",
        "Alpian (private):     https://onelink.to/download-alpian  [code: PCXTNB]",
        "Wise (transfers):     https://wise.com/invite/mic/f238f6e",
        "GetYourGuide (travel):https://www.getyourguide.com/switzerland-l125/?partner_id=NPTQI2G&utm_medium=online_publisher",
        "",
        "SUBSCRIBE LINK: " + SUBSCRIBE_URL,
        "TARGET: 500 subscribers -> Beehiiv ad network unlocks -> passive income begins!",
        "================================================================",
        "",
        "TOTAL TIME ESTIMATE: ~15-20 min to do all steps",
        "MINIMUM (just Beehiiv + Reddit): ~7 min",
    ]

    pack = "\n".join(lines)
    filename = "DAILY_PACK_" + TODAY + ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pack)
    save_to_github(pack, "packs/" + filename, "Daily pack: " + TODAY)
    print("   Daily pack saved: " + filename)
    return pack

# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\nTHE SMART DOLLAR - v4 - " + TODAY + "\n")

    print("[1/6] Generating newsletter content...")
    issue = generate_issue()
    print("      Subject: " + issue["subject"])

    print("[2/6] Building HTML...")
    html = build_html(issue)
    ok = save_to_github(html, "newsletters/newsletter_" + TODAY + ".html", "Newsletter: " + issue["subject"])
    print("      GitHub: " + ("saved!" if ok else "local only"))

    print("[3/6] Posting to Pinterest...")
    try:
        post_to_pinterest(issue)
    except Exception as e:
        print("      Skipped: " + str(e))

    print("[4/6] Generating all marketing content...")
    content = generate_all_content(issue)

    print("[5/6] Auto-posting Twitter thread...")
    twitter_posted = post_twitter_thread(content["twitter"]["tweets"])

    print("[6/6] Saving complete daily pack...")
    save_daily_pack(issue, content)

    print("\n" + "="*50)
    print("DONE! Here is your summary for today:")
    print("="*50)
    print("TITLE:    " + issue["subject"])
    print("SUBTITLE: " + issue["headline"])
    print("")
    print("AUTO-DONE:  Pinterest, Twitter (if configured)")
    print("YOUR TASKS: Download DAILY_PACK_" + TODAY + ".txt")
    print("            from Actions -> Artifacts")
    print("            Follow steps 1-9 inside the file")
    print("="*50)
