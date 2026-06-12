#!/usr/bin/env python3
"""Render growth-plan visual assets (SVG + PNG) from a prospect params file.

Usage: python3 scripts/render.py params/<prospect>.json

Static assets (same for every Branch-A prospect) -> svg/static/, png/static/
Parameterized assets (prospect-specific text)    -> svg/<slug>/, png/<slug>/
"""
import cairosvg, textwrap, re, json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT = "Liberation Sans, Arial, sans-serif"
NAVY = "#23265F"; IND3 = "#8B8EE8"; DARK = "#1C1E3A"; GRAY = "#4A4D68"
LGRAY = "#5A5D7A"; LINE = "#E8E9F2"
GREEN = "#3FAE68"; AMBER = "#F3B83F"; RED = "#E45B5B"; OKGREEN = "#1F9D61"
GBLUE = "#4285F4"; GYELLOW = "#FBBC04"; GRED = "#EA4335"
STAGE_COLS = ["#EF9ED6", "#C490DD", "#9D89DF", "#7C95E4", "#619DE9"]  # Gro.X logo gradient steps


def lerp_color(c1, c2, t):
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def inline_logo(name, x, y, w, h):
    raw = open(f"{ROOT}/logos/{name}.svg").read()
    m = re.search(r'<svg[^>]*viewBox="([^"]+)"[^>]*>', raw, re.S)
    vb = m.group(1)
    start = raw.index(m.group(0)) + len(m.group(0))
    inner = raw[start:raw.rindex('</svg>')]
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</svg>')


def logo_seo(x, y):
    return (f'<g transform="translate({x},{y})" font-family="{FONT}" font-size="58" font-weight="bold">'
            f'<text x="0" y="52" fill="{GBLUE}">S</text><text x="40" y="52" fill="{GYELLOW}">E</text>'
            f'<text x="78" y="52" fill="{GRED}">O</text></g>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


def check_path(cx, cy, scale=1.0, color="white", width=4):
    s = scale
    return (f'<path d="M {cx-8*s} {cy} L {cx-2*s} {cy+6*s} L {cx+9*s} {cy-7*s}" fill="none" '
            f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- static: chain
def chain_diagram(out):
    W, H = 1800, 240
    pw, ph, gap = 245, 92, 55
    n = 6; total = n*pw + (n-1)*gap; x0 = (W-total)/2; cy = H/2
    labels = ["Searches", "Clicks", "Lands", "Qualifies", "Books", "Shows up"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    for i, lab in enumerate(labels):
        x = x0 + i*(pw+gap); col = lerp_color(NAVY, IND3, i/(n-1))
        s.append(f'<rect x="{x}" y="{cy-ph/2}" width="{pw}" height="{ph}" rx="46" fill="{col}"/>')
        s.append(f'<text x="{x+pw/2}" y="{cy+11}" font-family="{FONT}" font-size="31" font-weight="bold" fill="white" text-anchor="middle">{lab}</text>')
        if i < n-1:
            ax = x + pw + gap/2
            s.append(f'<path d="M {ax-9} {cy-16} L {ax+11} {cy} L {ax-9} {cy+16}" fill="none" stroke="#B9BBE3" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append('</svg>')
    open(out, "w").write("".join(s))


# ---------------------------------------------------------------- static: heatmap
def heatmap(out, vals=None):
    W, H = 1920, 960
    mx, my = 40, 70
    lab_w = 400; cw = 205; hh = 100; rh = 136
    cols = ["Cold\noutreach", "Social\ncontent", "SEO", "LinkedIn\nads", "Meta\nads", "Google\nAds", "ChatGPT\nads"]
    rows = [["Reaches buyers", "in-window"], ["Works for niche,", "specific buyers"], ["Time to first", "pipeline"],
            ["Predictable", "&amp; scalable"], ["Effort required", "from you"]]
    vals = vals or [["R","R","G","R","R","G","G"], ["Y","Y","G","Y","R","G","G"], ["Y","R","R","Y","Y","G","G"],
            ["Y","R","Y","Y","Y","G","Y"], ["R","R","R","Y","Y","G","G"]]
    mat_w = lab_w + 7*cw; mat_h = hh + 5*rh
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    s.append(f'<defs><clipPath id="rc"><rect x="{mx}" y="{my}" width="{mat_w}" height="{mat_h}" rx="20"/></clipPath></defs>')
    s.append('<g clip-path="url(#rc)">')
    s.append(f'<rect x="{mx}" y="{my}" width="{mat_w}" height="{hh}" fill="{NAVY}"/>')
    for j, c in enumerate(cols):
        x = mx + lab_w + j*cw + cw/2; lines = c.split("\n")
        if len(lines) == 1:
            s.append(f'<text x="{x}" y="{my+hh/2+10}" font-family="{FONT}" font-size="28" font-weight="bold" fill="white" text-anchor="middle">{lines[0]}</text>')
        else:
            s.append(f'<text x="{x}" y="{my+hh/2-6}" font-family="{FONT}" font-size="28" font-weight="bold" fill="white" text-anchor="middle">{lines[0]}</text>')
            s.append(f'<text x="{x}" y="{my+hh/2+28}" font-family="{FONT}" font-size="28" font-weight="bold" fill="white" text-anchor="middle">{lines[1]}</text>')
    for i in range(5):
        y = my + hh + i*rh
        l1, l2 = rows[i]
        s.append(f'<text x="{mx+lab_w-22}" y="{y+rh/2-8}" font-family="{FONT}" font-size="27" font-weight="bold" fill="{DARK}" text-anchor="end">{l1}</text>')
        s.append(f'<text x="{mx+lab_w-22}" y="{y+rh/2+26}" font-family="{FONT}" font-size="27" font-weight="bold" fill="{DARK}" text-anchor="end">{l2}</text>')
        for j in range(7):
            v = vals[i][j]
            x = mx + lab_w + j*cw
            col = GREEN if v == "G" else AMBER if v == "Y" else RED
            s.append(f'<rect x="{x+2}" y="{y+2}" width="{cw-4}" height="{rh-4}" fill="{col}"/>')
            cx, cyy = x + cw/2, y + rh/2
            if v == "G":
                s.append(f'<path d="M {cx-16} {cyy} L {cx-4} {cyy+12} L {cx+17} {cyy-12}" fill="none" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
            elif v == "Y":
                s.append(f'<line x1="{cx-14}" y1="{cyy}" x2="{cx+14}" y2="{cyy}" stroke="white" stroke-width="7" stroke-linecap="round"/>')
            else:
                s.append(f'<path d="M {cx-12} {cyy-12} L {cx+12} {cyy+12} M {cx+12} {cyy-12} L {cx-12} {cyy+12}" stroke="white" stroke-width="7" stroke-linecap="round"/>')
    s.append('</g>')
    gx = mx + lab_w + 5*cw
    s.append(f'<rect x="{gx}" y="{my}" width="{cw}" height="{mat_h}" rx="14" fill="none" stroke="{NAVY}" stroke-width="6"/>')
    bw = 170
    s.append(f'<rect x="{gx+cw/2-bw/2}" y="{my-48}" width="{bw}" height="40" rx="20" fill="{NAVY}"/>')
    s.append(f'<text x="{gx+cw/2}" y="{my-20}" font-family="{FONT}" font-size="22" font-weight="bold" fill="white" text-anchor="middle" letter-spacing="1">BEST FIT</text>')
    ly = my + mat_h + 58; lx = mx + 10
    for col, lab in [(GREEN, "Strong fit"), (AMBER, "Partial / conditional"), (RED, "Poor fit")]:
        s.append(f'<rect x="{lx}" y="{ly-26}" width="36" height="36" rx="9" fill="{col}"/>')
        s.append(f'<text x="{lx+52}" y="{ly}" font-family="{FONT}" font-size="26" fill="{LGRAY}">{lab}</text>')
        lx += 52 + len(lab)*13.5 + 70
    s.append('</svg>')
    open(out, "w").write("".join(s))


# ---------------------------------------------------------------- static: funnel
def funnel(out):
    import math
    W, H = 1920, 800
    x0 = 60; colw = 360; n = 5; gap = 14
    xb = [x0 + i*colw for i in range(n+1)]
    stages = [("1,000", "Clicks", None, 1000), ("40", "Leads", "4% of clicks", 40),
              ("30", "Qualified", "75% of leads", 30), ("20", "Showed calls", "67% book &amp; show", 20),
              ("5", "New clients", "25% close rate", 5)]
    cy = 520; k = 135
    hs = [math.log10(v)*k for _, _, _, v in stages]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    for i in range(1, n):
        s.append(f'<line x1="{xb[i]}" y1="70" x2="{xb[i]}" y2="745" stroke="#ECEDF5" stroke-width="2.5"/>')
    for i in range(n):
        xl = xb[i] + (gap/2 if i > 0 else 0)
        xr = xb[i+1] - (gap/2 if i < n-1 else 0)
        hl = hs[i]; hr = hs[i+1] if i < n-1 else hs[i]
        s.append(f'<polygon points="{xl},{cy-hl/2} {xr},{cy-hr/2} {xr},{cy+hr/2} {xl},{cy+hl/2}" fill="{STAGE_COLS[i]}"/>')
    for i, (disp, lab, rate, _) in enumerate(stages):
        x = xb[i] + (8 if i == 0 else 26)
        numcol = OKGREEN if i == n-1 else NAVY
        s.append(f'<text x="{x}" y="125" font-family="{FONT}" font-size="52" font-weight="bold" fill="{numcol}">{disp}</text>')
        s.append(f'<text x="{x}" y="170" font-family="{FONT}" font-size="29" font-weight="bold" fill="{DARK}">{lab}</text>')
        if rate:
            s.append(f'<text x="{x}" y="206" font-family="{FONT}" font-size="24" fill="{LGRAY}">{rate}</text>')
    s.append('</svg>')
    open(out, "w").write("".join(s))


# ---------------------------------------------------------------- per-prospect: channel cards
def channel_cards(out, params):
    W = 1920
    cw, ch, gap = 925, 585, 35
    H = 20 + 2*ch + gap + 25
    positions = [(13, 20), (13+cw+gap, 20), (13, 20+ch+gap), (13+cw+gap, 20+ch+gap)]
    card1_body = params.get("card1_body") or ("Interrupt people who aren't looking. They also need big audiences to work - "
                  "the delivery algorithms want roughly 200,000+ targetable decision-makers to learn who converts. "
                  f"“{params['card1_example']}” is a tiny fraction of that. The algorithm never gets enough signal.")
    cards = [
        {"title": "Meta &amp; LinkedIn ads", "logo": "metali", "body": card1_body},
        {"title": "SEO", "logo": "seo",
         "body": params.get("seo_body") or ("The right idea: show up at the moment of search. But it takes 12+ months to rank, "
                  f"and the first page of “{params['seo_example_term']}” results is already spoken for.")},
        {"title": "ChatGPT ads", "logo": "gpt", "pill": ("SECONDARY FIT", NAVY),
         "body": "Work on the same capture logic as Google, on a brand-new auction. Worth a position early - we treat it as the second priority."},
        {"title": "Google Ads", "logo": "gads", "pill": ("PRIMARY FIT", OKGREEN), "ring": OKGREEN,
         "body": params.get("card4_body") or "The only channel that scores green on the requirement that matters most: it shows your firm to a buyer at the moment they type the need."},
    ]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    for card, (px, py) in zip(cards, positions):
        ring = card.get("ring")
        s.append(f'<rect x="{px}" y="{py}" width="{cw}" height="{ch}" rx="22" fill="white" stroke="{ring if ring else "#E2E3EE"}" stroke-width="{5 if ring else 2.5}"/>')
        lx, ly = px + 44, py + 42
        if card["logo"] == "metali":
            s.append(inline_logo("meta", lx, ly+4, 90, 60))
            s.append(inline_logo("linkedin", lx+118, ly+2, 62, 62))
        elif card["logo"] == "seo":
            s.append(logo_seo(lx, ly))
        elif card["logo"] == "gpt":
            s.append(inline_logo("openai", lx, ly+2, 62, 62))
        elif card["logo"] == "gads":
            s.append(inline_logo("google-ads", lx, ly+2, 64, 64))
        if card.get("pill"):
            plabel, pcol = card["pill"]; pw_ = 50 + len(plabel)*14
            s.append(f'<rect x="{px+cw-pw_-36}" y="{py+40}" width="{pw_}" height="50" rx="25" fill="{pcol}"/>')
            s.append(f'<text x="{px+cw-pw_/2-36}" y="{py+74}" font-family="{FONT}" font-size="24" font-weight="bold" fill="white" text-anchor="middle" letter-spacing="1">{plabel}</text>')
        s.append(f'<text x="{px+44}" y="{py+186}" font-family="{FONT}" font-size="38" font-weight="bold" fill="{NAVY}">{card["title"]}</text>')
        for i, ln in enumerate(textwrap.wrap(card["body"], width=47)):
            ln = ln.replace("&", "&amp;").replace("&amp;amp;", "&amp;").replace("<", "&lt;")
            s.append(f'<text x="{px+44}" y="{py+244+i*45}" font-family="{FONT}" font-size="32" fill="{GRAY}">{ln}</text>')
    s.append('</svg>')
    open(out, "w").write("".join(s))


# ---------------------------------------------------------------- per-prospect: search-matched pages
def search_matched_pages(out, params):
    W2, H2 = 1920, 980
    rows = params["search_rows"]  # list of [query, page_headline, page_subline]
    d = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}"><rect width="{W2}" height="{H2}" fill="white"/>']
    ycs = [180, 490, 800]
    for (q, head, sub), yc in zip(rows, ycs):
        d.append(f'<rect x="60" y="{yc-46}" width="820" height="92" rx="46" fill="white" stroke="#DADCE0" stroke-width="3"/>')
        d.append(f'<circle cx="122" cy="{yc-4}" r="16" fill="none" stroke="#5F6368" stroke-width="5"/>')
        d.append(f'<line x1="134" y1="{yc+8}" x2="146" y2="{yc+20}" stroke="#5F6368" stroke-width="5" stroke-linecap="round"/>')
        d.append(f'<text x="172" y="{yc+10}" font-family="{FONT}" font-size="28" fill="{DARK}">{esc(q)}</text>')
        d.append(f'<line x1="905" y1="{yc}" x2="1020" y2="{yc}" stroke="#9DA0C3" stroke-width="6" stroke-linecap="round"/>')
        d.append(f'<path d="M 1008 {yc-14} L 1032 {yc} L 1008 {yc+14}" fill="none" stroke="#9DA0C3" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
        cx0, cy0 = 1060, yc - 110
        d.append(f'<rect x="{cx0}" y="{cy0}" width="800" height="220" rx="16" fill="white" stroke="#E2E3EE" stroke-width="3"/>')
        d.append(f'<path d="M {cx0} {cy0+40} L {cx0} {cy0+16} A 16 16 0 0 1 {cx0+16} {cy0} L {cx0+784} {cy0} A 16 16 0 0 1 {cx0+800} {cy0+16} L {cx0+800} {cy0+40} Z" fill="#F1F2F8"/>')
        for di, dc in enumerate(["#E45B5B", "#F3B83F", "#3FAE68"]):
            d.append(f'<circle cx="{cx0+30+di*26}" cy="{cy0+20}" r="6" fill="{dc}"/>')
        d.append(f'<text x="{cx0+34}" y="{cy0+98}" font-family="{FONT}" font-size="34" font-weight="bold" fill="{NAVY}">{esc(head)}</text>')
        d.append(f'<text x="{cx0+34}" y="{cy0+142}" font-family="{FONT}" font-size="25" fill="{GRAY}">{esc(sub)}</text>')
        bw_ = 300
        d.append(f'<rect x="{cx0+34}" y="{cy0+164}" width="{bw_}" height="40" rx="20" fill="{OKGREEN}"/>')
        d.append(check_path(cx0+62, cy0+184, 1.1, "white", 4.5))
        d.append(f'<text x="{cx0+86}" y="{cy0+192}" font-family="{FONT}" font-size="22" font-weight="bold" fill="white">Built for this search</text>')
    d.append('</svg>')
    open(out, "w").write("".join(d))


# ---------------------------------------------------------------- per-prospect: comparison scenario
def comparison_scenario(out, sc):
    import math
    W, H = 1920, 1070
    pw = 880
    stages = sc["stages"]
    last = stages[-1]
    panels = [
        {"x": 60, "label": sc["typical_label"], "head": "#6B6E8C", "vkey": "t", "nkey": "t_note",
         "bars": ["#9B9DDB", "#7B7DC9", "#5C5FB0", "#3D4097"], "badges": False,
         "top_val": str(last["t"]), "top_note": "", "top_col": DARK},
        {"x": 980, "label": sc["system_label"], "head": NAVY, "vkey": "s", "nkey": "s_note",
         "bars": ["#7BCBA4", "#4FB983", "#2FA76C", "#1F9D61"], "badges": True,
         "top_val": str(last["s"]), "top_note": (sc.get("multiplier_badge", "") + " vs typical").strip(), "top_col": OKGREEN},
    ]
    maxv = max(max(st["t"], st["s"]) for st in stages)
    k = 400 / math.log10(maxv)
    bar_h, bar_gap = 118, 30
    fy0 = 392
    panel_h = fy0 + len(stages)*(bar_h+bar_gap) - bar_gap + 40 - 60
    d = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>']
    for p in panels:
        x = p["x"]
        d.append(f'<rect x="{x}" y="60" width="{pw}" height="{panel_h}" rx="22" fill="white" stroke="#E2E3EE" stroke-width="3"/>')
        d.append(f'<rect x="{x+24}" y="84" width="{pw-48}" height="74" rx="14" fill="{p["head"]}"/>')
        d.append(f'<text x="{x+pw/2}" y="{84+48}" font-family="{FONT}" font-size="30" font-weight="bold" fill="white" text-anchor="middle">{esc(p["label"])}</text>')
        cw_ = (pw - 88 - 22) / 2
        cards = [("MONTHLY BUDGET", sc["budget"], "", DARK), ("CONSULTATIONS / MONTH", p["top_val"], p["top_note"], p["top_col"])]
        for ci, (clab, cval, cnote, ccol) in enumerate(cards):
            cx0 = x + 44 + ci*(cw_+22)
            d.append(f'<rect x="{cx0}" y="186" width="{cw_}" height="124" rx="16" fill="#FAFAFD" stroke="#E2E3EE" stroke-width="2"/>')
            d.append(f'<text x="{cx0+cw_/2}" y="226" font-family="{FONT}" font-size="20" font-weight="bold" fill="{LGRAY}" text-anchor="middle" letter-spacing="1">{clab}</text>')
            d.append(f'<text x="{cx0+cw_/2}" y="274" font-family="{FONT}" font-size="44" font-weight="bold" fill="{ccol}" text-anchor="middle">{esc(cval)}</text>')
            if cnote:
                d.append(f'<text x="{cx0+cw_/2}" y="302" font-family="{FONT}" font-size="19" font-weight="bold" fill="{OKGREEN}" text-anchor="middle">{esc(cnote)}</text>')
        cxm = x + pw/2
        widths = [math.log10(st[p["vkey"]]) * k for st in stages]
        for i, st in enumerate(stages):
            y = fy0 + i*(bar_h+bar_gap)
            wt = widths[i]
            wb = widths[i+1] if i < len(stages)-1 else widths[i]*0.86
            col = p["bars"][i]
            d.append(f'<polygon points="{cxm-wt/2},{y} {cxm+wt/2},{y} {cxm+wb/2},{y+bar_h} {cxm-wb/2},{y+bar_h}" fill="{col}"/>')
            d.append(f'<text x="{x+44}" y="{y+bar_h/2+10}" font-family="{FONT}" font-size="28" font-weight="bold" fill="{DARK}">{esc(st["label"])}</text>')
            d.append(f'<text x="{cxm}" y="{y+bar_h/2+16}" font-family="{FONT}" font-size="44" font-weight="bold" fill="white" text-anchor="middle">{st[p["vkey"]]}</text>')
            if p["badges"]:
                d.append(f'<text x="{x+pw-44}" y="{y+bar_h/2-16}" font-family="{FONT}" font-size="26" font-weight="bold" fill="{DARK}" text-anchor="end">{esc(st[p["nkey"]])}</text>')
                if st.get("badge"):
                    blen = len(st["badge"])*14 + 36
                    bx = x + pw - 44 - blen
                    d.append(f'<rect x="{bx}" y="{y+bar_h/2+2}" width="{blen}" height="46" rx="23" fill="{OKGREEN}"/>')
                    d.append(f'<text x="{bx+blen/2}" y="{y+bar_h/2+33}" font-family="{FONT}" font-size="23" font-weight="bold" fill="white" text-anchor="middle">{esc(st["badge"])}</text>')
            else:
                d.append(f'<text x="{x+pw-44}" y="{y+bar_h/2+10}" font-family="{FONT}" font-size="26" font-weight="bold" fill="{DARK}" text-anchor="end">{esc(st[p["nkey"]])}</text>')
    d.append('</svg>')
    open(out, "w").write("".join(d))


# ---------------------------------------------------------------- main
def main():
    params = json.load(open(sys.argv[1]))
    slug = params["slug"]
    svg_static = f"{ROOT}/svg/static"; svg_p = f"{ROOT}/svg/{slug}"
    png_static = f"{ROOT}/png/static"; png_p = f"{ROOT}/png/{slug}"
    for d in (svg_static, svg_p, png_static, png_p):
        os.makedirs(d, exist_ok=True)

    chain_diagram(f"{svg_static}/chain-diagram.svg")
    heatmap(f"{svg_static}/channel-fit-heatmap.svg")
    funnel(f"{svg_static}/funnel-scenario.svg")
    channel_cards(f"{svg_p}/channel-cards.svg", params)
    search_matched_pages(f"{svg_p}/search-matched-pages.svg", params)
    if params.get("heatmap_vals"):
        heatmap(f"{svg_p}/channel-fit-heatmap.svg", vals=params["heatmap_vals"])
    if params.get("scenario"):
        comparison_scenario(f"{svg_p}/comparison-scenario.svg", params["scenario"])

    for svg_dir, png_dir in ((svg_static, png_static), (svg_p, png_p)):
        for f in sorted(os.listdir(svg_dir)):
            if not f.endswith(".svg"):
                continue
            src = f"{svg_dir}/{f}"
            m = re.search(r'viewBox="0 0 (\d+)', open(src).read())
            w = int(float(m.group(1))) * 2 if m else 3840
            dst = f"{png_dir}/{f[:-4]}.png"
            cairosvg.svg2png(url=src, write_to=dst, output_width=w)
            print("rendered", dst)


if __name__ == "__main__":
    main()
