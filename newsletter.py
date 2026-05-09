"""
The Smart Dollar - Master Automation Script v5
Runs daily at 9am Switzerland time via GitHub Actions
Generates: Newsletter + Video + Pinterest + Marketing Pack
"""

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
TWITTER_API_KEY       = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET    = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN  = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
PEXELS_API_KEY     = os.environ.get("PEXELS_API_KEY", "")

SUBSCRIBE_URL = "https://arnauds-newsletter-47845f.beehiiv.com"
TODAY      = datetime.now().strftime("%Y-%m-%d")
TODAY_LONG = datetime.now().strftime("%B %d, %Y")

AFFILIATES = {
    "revolut":      {"url": "https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",             "label": "Revolut",      "emoji": "💳", "code": None,     "desc": "Zero-fee banking for 70M+ users",           "tags": ["banking","spending","travel","saving","international"]},
    "coinbase":     {"url": "https://coinbase.com/join/RSRGFEP?src=ios-link",                                                 "label": "Coinbase",     "emoji": "₿",  "code": None,     "desc": "Start investing in crypto from $2",         "tags": ["crypto","bitcoin","ethereum","digital assets"]},
    "etoro":        {"url": "https://etoro.tw/4vZbEOP",                                                                       "label": "eToro",        "emoji": "📈", "code": None,     "desc": "Copy top investors automatically",          "tags": ["investing","stocks","portfolio","trading","ETF"]},
    "nordvpn":      {"url": "https://refer-nordvpn.com/BrJJQSzaIsM",                                                         "label": "NordVPN",      "emoji": "🔒", "code": None,     "desc": "Protect your finances online",              "tags": ["security","privacy","VPN","online safety"]},
    "neon":         {"url": "http://onelink.to/neon",                                                                         "label": "Neon",         "emoji": "🇨🇭", "code": "SDB98A", "desc": "Switzerland's best free bank account",      "tags": ["swiss bank","switzerland","CHF","neobank"]},
    "yuh":          {"url": "https://www.yuh.com/download",                                                                   "label": "Yuh",          "emoji": "💰", "code": "uzwi60", "desc": "Pay, save and invest — one Swiss app",      "tags": ["swiss","invest","save","pay"]},
    "binance":      {"url": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00Z6UROXWP",                        "label": "Binance",      "emoji": "🟡", "code": None,     "desc": "World's largest crypto exchange",           "tags": ["crypto","trading","altcoins","exchange"]},
    "alpian":       {"url": "https://onelink.to/download-alpian",                                                             "label": "Alpian",       "emoji": "🏔️", "code": "PCXTNB", "desc": "Swiss private banking — CHF 25 bonus",      "tags": ["swiss","private banking","wealth","CHF"]},
    "wise":         {"url": "https://wise.com/invite/mic/f238f6e",                                                            "label": "Wise",         "emoji": "🌍", "code": None,     "desc": "Real exchange rates, no hidden fees",       "tags": ["international transfer","send money","exchange rate"]},
    "getyourguide": {"url": "https://www.getyourguide.com/switzerland-l125/?partner_id=NPTQI2G&utm_medium=online_publisher", "label": "GetYourGuide", "emoji": "🗺️", "code": None,     "desc": "Amazing Swiss activities & tours",          "tags": ["travel","activities","tours","switzerland","tourism"]},
}

def ai(prompt, max_tokens=1500):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-opus-4-5", max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip().replace("```json","").replace("```","").strip()

def ai_json(prompt, max_tokens=1500):
    return json.loads(ai(prompt, max_tokens))

def save_to_github(content_bytes, filename, message, branch="main", is_binary=False):
    if not GITHUB_TOKEN or not REPO_NAME:
        return False
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{filename}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    sha = None
    ex = requests.get(api_url, headers=headers)
    if ex.ok:
        sha = ex.json().get("sha")
    if is_binary:
        encoded = base64.b64encode(content_bytes).decode()
    else:
        encoded = base64.b64encode(content_bytes.encode()).decode()
    data = {"message": message, "content": encoded, "branch": branch}
    if sha:
        data["sha"] = sha
    r = requests.put(api_url, headers=headers, json=data)
    return r.ok

# ── GENERATE NEWSLETTER ─────────────────────────────────────────────────────
def generate_issue():
    aff_list = "\n".join([f'  "{k}": {v["tags"]}' for k, v in AFFILIATES.items()])
    return ai_json(
        f'Write today\'s "The Smart Dollar" newsletter for Swiss/European readers.\n'
        f'Date: {TODAY_LONG}\n\nAffiliates:\n{aff_list}\n\n'
        'Return ONLY this JSON:\n'
        '{"subject":"max 60 chars","headline":"punchy headline",'
        '"intro":"2-3 sentence warm intro",'
        '"story1_tag":"MONEY TIP","story1_title":"title","story1_body":"3-4 sentences with numbers","story1_affiliate":null,'
        '"story2_tag":"AI SPOTLIGHT","story2_title":"title","story2_body":"3-4 sentences","story2_affiliate":null,'
        '"story3_tag":"INVEST SMART","story3_title":"title","story3_body":"3-4 sentences","story3_affiliate":null,'
        '"quick_tip":"one punchy tip","seo_keyword":"2-4 word keyword"}\n\n'
        'Rules: max one use per affiliate, match naturally, include real numbers.'
    )

def build_html(issue):
    def aff(key):
        if not key or key not in AFFILIATES:
            return ""
        a = AFFILIATES[key]
        code = f'<p style="margin:3px 0 6px;font-size:12px;color:#888;">Use code: <strong>{a["code"]}</strong></p>' if a.get("code") else ""
        return (f'<div style="margin-top:12px;background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px;">'
                f'<p style="margin:0 0 3px;font-size:13px;color:#555;">{a["emoji"]} <strong>{a["label"]}</strong> — {a["desc"]}</p>{code}'
                f'<a href="{a["url"]}" style="display:inline-block;background:#1a1a2e;color:#ffd700;padding:7px 14px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none;margin-top:4px;">Try {a["label"]} →</a></div>')

    return (
        f'<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;color:#1a1a2e;">'
        f'<div style="text-align:center;padding:16px 0;border-bottom:3px solid #ffd700;margin-bottom:20px;">'
        f'<p style="font-size:12px;color:#888;margin:0;">{TODAY_LONG} · Finance &amp; AI for Smart People</p></div>'
        f'<p style="font-size:15px;color:#555;line-height:1.8;margin-bottom:20px;">{issue["intro"]}</p>'
        f'<div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#16a34a;letter-spacing:2px;">{issue["story1_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story1_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story1_body"]}</p>'
        f'{aff(issue.get("story1_affiliate"))}</div>'
        f'<div style="background:#eff6ff;border-left:4px solid #2563eb;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#2563eb;letter-spacing:2px;">{issue["story2_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story2_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story2_body"]}</p>'
        f'{aff(issue.get("story2_affiliate"))}</div>'
        f'<div style="background:#fefce8;border-left:4px solid #ca8a04;padding:16px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;">'
        f'<span style="font-size:10px;font-weight:800;color:#ca8a04;letter-spacing:2px;">{issue["story3_tag"]}</span>'
        f'<h3 style="font-size:17px;font-weight:800;margin:6px 0 8px;">{issue["story3_title"]}</h3>'
        f'<p style="font-size:14px;color:#444;line-height:1.8;margin:0;">{issue["story3_body"]}</p>'
        f'{aff(issue.get("story3_affiliate"))}</div>'
        f'<div style="background:#1a1a2e;color:#fff;padding:16px 20px;border-radius:10px;text-align:center;margin-bottom:20px;">'
        f'<p style="font-size:10px;opacity:0.6;margin:0 0 5px;letter-spacing:2px;">TIP OF THE DAY</p>'
        f'<p style="font-size:14px;font-weight:700;margin:0;line-height:1.5;">{issue["quick_tip"]}</p></div>'
        f'<div style="text-align:center;padding:14px 0;border-top:1px solid #eee;">'
        f'<p style="font-size:13px;color:#888;margin:0 0 8px;">Share The Smart Dollar with a friend</p>'
        f'<a href="{SUBSCRIBE_URL}" style="display:inline-block;background:#ffd700;color:#1a1a2e;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;text-decoration:none;">Subscribe Free</a>'
        f'</div></div>'
    )

# ── PINTEREST ───────────────────────────────────────────────────────────────
def post_to_pinterest(issue):
    if not PINTEREST_TOKEN or not PINTEREST_BOARD_ID:
        return
    try:
        pin = ai_json(
            f'Pinterest pin for: {issue["headline"]}\nTip: {issue["quick_tip"]}\n'
            'JSON: {"title":"under 100 chars","description":"200-400 chars + hashtags #PersonalFinance #SwissFinance #MoneyTips #Investing #FinancialFreedom #Switzerland #CHF"}',
            300
        )
        image_url = f"https://picsum.photos/seed/{TODAY}/800/1200"
        r = requests.post("https://api.pinterest.com/v5/pins",
            headers={"Authorization": f"Bearer {PINTEREST_TOKEN}", "Content-Type": "application/json"},
            json={"board_id": PINTEREST_BOARD_ID, "title": pin["title"],
                  "description": pin["description"] + f"\n\nFree newsletter: {SUBSCRIBE_URL}",
                  "media_source": {"source_type": "image_url", "url": image_url}, "link": SUBSCRIBE_URL})
        print("  Pinterest: " + ("posted!" if r.ok else f"skipped ({r.status_code})"))
    except Exception as e:
        print(f"  Pinterest error: {e}")

# ── TWITTER ─────────────────────────────────────────────────────────────────
def post_twitter_thread(tweets):
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        return False
    try:
        import hmac, hashlib, time, uuid
        from urllib.parse import quote
        def oauth_header(method, url):
            op = {"oauth_consumer_key": TWITTER_API_KEY, "oauth_nonce": uuid.uuid4().hex,
                  "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": str(int(time.time())),
                  "oauth_token": TWITTER_ACCESS_TOKEN, "oauth_version": "1.0"}
            sp = "&".join([f"{quote(k,safe='')}={quote(str(v),safe='')}" for k,v in sorted(op.items())])
            base = f"{method}&{quote(url,safe='')}&{quote(sp,safe='')}"
            key = f"{quote(TWITTER_API_SECRET,safe='')}&{quote(TWITTER_ACCESS_SECRET,safe='')}"
            sig = base64.b64encode(hmac.new(key.encode(),base.encode(),hashlib.sha1).digest()).decode()
            op["oauth_signature"] = sig
            return "OAuth " + ", ".join([f'{k}="{quote(str(v),safe="")}"' for k,v in sorted(op.items())])

        url = "https://api.twitter.com/2/tweets"
        last_id = None
        for tweet in tweets:
            body = {"text": tweet}
            if last_id:
                body["reply"] = {"in_reply_to_tweet_id": last_id}
            r = requests.post(url, headers={"Authorization": oauth_header("POST", url),
                              "Content-Type": "application/json"}, json=body)
            if r.ok:
                last_id = r.json()["data"]["id"]
            else:
                return False
        print("  Twitter thread posted!")
        return True
    except Exception as e:
        print(f"  Twitter error: {e}")
        return False

# ── GENERATE MARKETING CONTENT ──────────────────────────────────────────────
def generate_marketing(issue):
    aff_keys = [issue.get(f"story{i}_affiliate") for i in range(1,4) if issue.get(f"story{i}_affiliate")]
    primary  = AFFILIATES[aff_keys[0]] if aff_keys else AFFILIATES["etoro"]
    kw = issue["seo_keyword"]
    s1 = issue["story1_body"][:200]
    s2 = issue["story2_body"][:150]

    print("  Generating meta description...")
    meta = ai(f'Meta description 140-150 chars for: {issue["subject"]}\nContent: {s1[:80]}\nKeyword: {kw}. End with: Free daily newsletter.\nReturn ONLY the text.', 120).strip().strip('"')

    print("  Generating Twitter thread...")
    twitter = ai_json(
        f'5-tweet thread about: {issue["headline"]}\nInsight 1: {s1}\nInsight 2: {s2}\nTip: {issue["quick_tip"]}\n'
        f'Tweet 5 CTA: {SUBSCRIBE_URL} + #PersonalFinance #SwissFinance #CHF #MoneyTips\n'
        'JSON: {"tweets":["t1","t2","t3","t4","t5"]}', 600)

    print("  Generating Reddit comment...")
    reddit = ai_json(
        f'Helpful Reddit comment about: {kw}\nBased on: {s1}\n'
        f'Mention {primary["label"]} only if very relevant.\nEnd: "Free newsletter: {SUBSCRIBE_URL}"\n'
        'Max 130 words. Sound like a real person. No headers.\n'
        'Best 4 subreddits including r/eupersonalfinance and r/Switzerland.\n'
        'JSON: {"comment":"text","subreddits":["s1","s2","s3","s4"],"search":"what to search"}', 500)

    print("  Generating Instagram caption...")
    insta = ai_json(
        f'Instagram caption for: {issue["headline"]}\nHook: {s1[:80]}\n'
        '3 bullet points of value. CTA: Link in bio to subscribe free\n'
        'Include 20 hashtags.\nJSON: {"caption":"text"}', 500)

    print("  Generating Quora answer...")
    quora = ai_json(
        f'Quora answer about: {kw}\nBased on: {s1}\n'
        f'Expert Swiss resident tone. 180-220 words. End: "Free newsletter: {SUBSCRIBE_URL}"\n'
        'JSON: {"answer":"text","question":"exact question to search"}', 500)

    print("  Generating WhatsApp message...")
    whatsapp = ai_json(
        f'Short WhatsApp message: {issue["headline"]}\nFact: {s1[:80]}\nLink: {SUBSCRIBE_URL}\n'
        '2-3 sentences. Casual. No hashtags.\nJSON: {"message":"text"}', 200)

    print("  Generating subject line variants...")
    subjects = ai_json(
        f'5 email subject variants for: {issue["headline"]}\n'
        'Swiss/European finance audience. All under 60 chars.\n'
        'Styles: curious, urgent, specific, numbered, question.\n'
        'JSON: {"subjects":["s1","s2","s3","s4","s5"]}', 300)

    return {"meta": meta, "twitter": twitter, "reddit": reddit,
            "insta": insta, "quora": quora, "whatsapp": whatsapp, "subjects": subjects}

# ── SAVE DAILY PACK ─────────────────────────────────────────────────────────
def save_daily_pack(issue, marketing, video_info=None):
    twit     = marketing["twitter"]["tweets"]
    reddit   = marketing["reddit"]
    insta    = marketing["insta"]
    quora    = marketing["quora"]
    wa       = marketing["whatsapp"]
    subjects = marketing["subjects"]["subjects"]
    meta     = marketing["meta"]

    video_section = ""
    if video_info and video_info.get("video_ok"):
        video_section = (
            "\n================================================================\n"
            "VIDEO READY - Download and post to TikTok + Reels + Shorts\n"
            "================================================================\n"
            "Your video has been automatically created and uploaded to GitHub!\n\n"
            "HOW TO DOWNLOAD:\n"
            "  1. GitHub Actions -> this run -> Artifacts -> download 'video'\n"
            "  OR\n"
            "  1. GitHub repo -> videos/ folder -> " + video_info.get("video_file","") + "\n"
            "  2. Click Download\n\n"
            "POST THIS VIDEO TO:\n"
            "  TikTok:          @thesmartdollar\n"
            "  Instagram Reels: @thesmartdollar\n"
            "  YouTube Shorts:  The Smart Dollar channel\n\n"
            "CAPTION FOR ALL 3 PLATFORMS:\n"
            + video_info.get("hook","") + "\n\n"
            + insta["caption"] + "\n\n"
            "HASHTAGS:\n"
            + video_info.get("tiktok_hashtags","#SwissFinance #PersonalFinance #MoneyTips") + "\n"
        )
    else:
        video_section = (
            "\n================================================================\n"
            "VIDEO - Script ready (video generation may have failed)\n"
            "================================================================\n"
            "If you want to film yourself reading this (anonymous, just show charts):\n\n"
            + (video_info.get("script","") if video_info else "") + "\n"
        )

    lines = [
        "THE SMART DOLLAR - COMPLETE DAILY PACK",
        "Date: " + TODAY,
        "================================================================",
        "",
        "AUTOMATED TODAY (zero action needed):",
        "  [AUTO] Newsletter HTML -> GitHub/newsletters/",
        "  [AUTO] Pinterest pin posted",
        "  [AUTO] Twitter thread posted (if keys set)",
        "  [AUTO] Video created -> GitHub/videos/",
        "",
        "================================================================",
        "STEP 1 - CANVA THUMBNAIL (2 min)",
        "================================================================",
        "Open your Canva template, change these 2 lines only:",
        "  TITLE:    " + issue["subject"][:50],
        "  SUBTITLE: " + issue["headline"][:55],
        "Download as PNG -> upload in Beehiiv step below",
        "",
        "================================================================",
        "STEP 2 - BEEHIIV SEND (5 min)",
        "================================================================",
        "1. GitHub -> newsletters/ -> newsletter_" + TODAY + ".html -> Raw -> Copy All",
        "2. app.beehiiv.com -> + New Post",
        "3. TITLE:    " + issue["subject"],
        "4. SUBTITLE: " + issue["headline"],
        "5. Body -> type / -> HTML block -> paste",
        "6. Next -> Audience: Email and web, All subscribers",
        "7. Email step: check subject. Alternative subject lines:",
    ]
    for i, s in enumerate(subjects):
        lines.append("   " + str(i+1) + ". " + s)
    lines += [
        "8. Web: Advanced capture = Popup, Show thumbnail = ON, Feature = ON",
        "9. META DESCRIPTION (paste in SEO + Facebook + Twitter):",
        "   " + meta,
        "10. Upload Canva thumbnail",
        "11. Next -> Review -> SEND!",
        "",
        "================================================================",
        "STEP 3 - REDDIT (2 min) - MOST POWERFUL",
        "================================================================",
        "WHERE: " + " | ".join(["r/" + s for s in reddit["subreddits"]]),
        "SEARCH FOR: " + reddit["search"],
        "Find a post -> Reply with this:",
        "",
        "--- COPY ---",
        reddit["comment"],
        "--- END ---",
        "",
        video_section,
        "================================================================",
        "STEP 4 - INSTAGRAM (2 min)",
        "================================================================",
        "Post your Canva thumbnail + this caption:",
        "",
        "--- COPY ---",
        insta["caption"],
        "--- END ---",
        "",
        "================================================================",
        "STEP 5 - QUORA (3 min) - RANKS ON GOOGLE",
        "================================================================",
        "quora.com -> search: " + quora["question"],
        "",
        "--- COPY ---",
        quora["answer"],
        "--- END ---",
        "",
        "================================================================",
        "STEP 6 - WHATSAPP/TELEGRAM (30 sec)",
        "================================================================",
        "--- COPY ---",
        wa["message"],
        "--- END ---",
        "",
        "================================================================",
        "YOUR AFFILIATE LINKS",
        "================================================================",
        "Revolut:       https://revolut.com/referral/?referral-code=arnaud1zrf!MAY1-26-AR-L1&geo-redirect",
        "Coinbase:      https://coinbase.com/join/RSRGFEP?src=ios-link",
        "eToro:         https://etoro.tw/4vZbEOP",
        "NordVPN:       https://refer-nordvpn.com/BrJJQSzaIsM",
        "Neon(SDB98A):  http://onelink.to/neon",
        "Yuh(uzwi60):   https://www.yuh.com/download",
        "Binance:       https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00Z6UROXWP",
        "Alpian(PCXTNB):https://onelink.to/download-alpian",
        "Wise:          https://wise.com/invite/mic/f238f6e",
        "GetYourGuide:  https://www.getyourguide.com/switzerland-l125/?partner_id=NPTQI2G&utm_medium=online_publisher",
        "",
        "SUBSCRIBE LINK: " + SUBSCRIBE_URL,
        "TARGET: 500 subscribers -> Beehiiv ad network -> passive income!",
        "================================================================",
        "MINIMUM DAILY TASKS: Beehiiv send + Reddit = 7 min",
        "FULL DAILY TASKS: All steps above = ~15 min",
    ]

    pack = "\n".join(lines)
    filename = "DAILY_PACK_" + TODAY + ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pack)
    save_to_github(pack, "packs/" + filename, "Pack: " + TODAY)
    print("  Daily pack saved: " + filename)

# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nTHE SMART DOLLAR v5 - " + TODAY)
    print("="*50)

    print("[1/6] Generating newsletter...")
    issue = generate_issue()
    print("  Subject: " + issue["subject"])

    print("[2/6] Saving newsletter HTML...")
    html = build_html(issue)
    ok = save_to_github(html, "newsletters/newsletter_" + TODAY + ".html", "Newsletter: " + issue["subject"])
    print("  GitHub: " + ("saved!" if ok else "failed"))

    print("[3/6] Posting to Pinterest...")
    try:
        post_to_pinterest(issue)
    except Exception as e:
        print(f"  Skipped: {e}")

    print("[4/6] Generating marketing content...")
    marketing = generate_marketing(issue)

    print("[5/6] Posting Twitter thread...")
    twitter_ok = post_twitter_thread(marketing["twitter"]["tweets"])
    if not twitter_ok:
        print("  Twitter: not configured or failed (see daily pack)")

    print("[6/6] Creating video...")
    video_info = None
    if ELEVENLABS_API_KEY and PEXELS_API_KEY:
        try:
            # Install deps and run video generator
            import subprocess
            subprocess.run("apt-get install -y ffmpeg 2>/dev/null | tail -1", shell=True)
            subprocess.run("pip install Pillow requests numpy --break-system-packages -q", shell=True)
            from video_generator import create_daily_video, install_deps
            install_deps()
            video_info = create_daily_video(issue)
        except Exception as e:
            print(f"  Video error: {e}")
            video_info = None
    else:
        print("  Video: add ELEVENLABS_API_KEY + PEXELS_API_KEY secrets to enable")

    print("[7/7] Saving daily pack...")
    save_daily_pack(issue, marketing, video_info)

    print("\n" + "="*50)
    print("ALL DONE!")
    print("TITLE:    " + issue["subject"])
    print("SUBTITLE: " + issue["headline"])
    print("Download DAILY_PACK_" + TODAY + ".txt from Actions -> Artifacts")
    if video_info and video_info.get("video_ok"):
        print("VIDEO:    Ready in Actions -> Artifacts -> video")
    print("="*50)
