#!/usr/bin/env python3
"""Render the challenger front page for news-image-20261119.

Reads stories.json from the repository root, lays out a one-page
newspaper in plain HTML/CSS with code-drawn inline SVG illustrations
(flat vector scenes, no external images, no network), and screenshots
it at exactly 1024x1024 with headless Chromium through Playwright.

Deterministic by construction: static HTML, no timestamps, no random
numbers, no JavaScript that mutates the layout. Two runs must produce
identical bytes (verified by comparing sha256).

The build FAILS with exit code 1 if anything is clipped or the page
runs taller/wider than 1024px, so a broken layout can never ship
silently. Checks:
  * page scrollHeight / scrollWidth must be <= 1024
  * every element marked class "clip" must not have scrollHeight
    above its clientHeight (no headline or fact losing a line)

Usage:
    python3 tools/render.py [--out PATH]
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
PAGE_W, PAGE_H = 1024, 1024

GUARD_JS = """() => {
  const bad = [];
  const page = document.getElementById('page');
  if (page.scrollHeight > 1024) {
    bad.push(`page too tall: scrollHeight=${page.scrollHeight} > 1024`);
  }
  if (page.scrollWidth > 1024) {
    bad.push(`page too wide: scrollWidth=${page.scrollWidth} > 1024`);
  }
  document.querySelectorAll('.clip').forEach((el, i) => {
    if (el.scrollHeight - el.clientHeight > 2) {
      bad.push(`clipped text .${el.className.split(' ')[0]} #${i}: ` +
        `"${el.textContent.trim().slice(0, 60)}..." ` +
        `scrollHeight=${el.scrollHeight} clientHeight=${el.clientHeight}`);
    }
  });
  return bad;
}"""


def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------- SVG art
# Every illustration is a flat vector scene drawn in code, composed as a
# wide 200x46 strip so it fills its cell edge to edge (heroes 310x68,
# mains 186x46) instead of letterboxing. No external images, no AI
# images, no network — the art is the code below.

def _sky(color="#bcd7ea"):
    return f'<rect width="200" height="46" fill="{color}"/>'


def art_shenzhen():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#cfe3f2")}
<rect y="36" width="200" height="10" fill="#7fae7a"/>
<g stroke="#5a4632" stroke-width="1.6"><line x1="38" y1="4" x2="38" y2="36"/><line x1="100" y1="2" x2="100" y2="36"/><line x1="162" y1="4" x2="162" y2="36"/></g>
<rect x="38" y="4" width="22" height="11" fill="#b22234"/><rect x="38" y="4" width="22" height="1.6" fill="#fff"/><rect x="38" y="8" width="22" height="1.6" fill="#fff"/><rect x="38" y="12" width="22" height="1.6" fill="#fff"/>
<rect x="100" y="2" width="22" height="11" fill="#de2910"/><circle cx="105" cy="6" r="2" fill="#ffde00"/><circle cx="112" cy="5" r="1" fill="#ffde00"/><circle cx="116" cy="9" r="1" fill="#ffde00"/>
<rect x="162" y="4" width="22" height="11" fill="#fff"/><rect x="162" y="8" width="22" height="3.6" fill="#0039a6"/><rect x="162" y="11.6" width="22" height="3.4" fill="#d52b1e"/>
<ellipse cx="100" cy="39" rx="58" ry="5" fill="#6b4f2e"/><ellipse cx="100" cy="37.5" rx="58" ry="5" fill="#a67c52"/>
<circle cx="70" cy="27" r="6" fill="#f2c89b"/><rect x="64" y="32" width="12" height="5" fill="#2e4a6b"/>
<circle cx="100" cy="24" r="6" fill="#e8b88a"/><rect x="94" y="29" width="12" height="6" fill="#7a1f1f"/>
<circle cx="130" cy="27" r="6" fill="#f2c89b"/><rect x="124" y="32" width="12" height="5" fill="#1f4d2e"/>
<rect x="90" y="35" width="20" height="3.4" fill="#fff"/><rect x="93" y="36" width="14" height="1.8" fill="#c00"/>
</svg>"""


def art_gta():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="46" fill="#ff9a5c"/><rect width="200" height="24" fill="#ff6b9d"/>
<circle cx="152" cy="13" r="9" fill="#ffe08a"/>
<g fill="#1a1030"><rect x="6" y="12" width="16" height="16"/><rect x="26" y="18" width="12" height="10"/><rect x="42" y="8" width="18" height="20"/><rect x="64" y="14" width="14" height="14"/><rect x="118" y="10" width="16" height="18"/><rect x="138" y="16" width="12" height="12"/><rect x="168" y="6" width="20" height="22"/><rect x="190" y="16" width="10" height="12"/></g>
<g fill="#ffd94d"><rect x="10" y="16" width="3" height="3"/><rect x="46" y="12" width="3" height="3"/><rect x="56" y="20" width="3" height="3"/><rect x="122" y="14" width="3" height="3"/><rect x="172" y="10" width="3" height="3"/><rect x="180" y="18" width="3" height="3"/></g>
<rect y="28" width="200" height="18" fill="#2b1b4d"/><rect y="28" width="200" height="2" fill="#ffcf5c"/>
<g><path d="M72 40 L78 33 L118 33 L126 40 Z" fill="#e63b7a"/><rect x="68" y="39" width="62" height="5" rx="2" fill="#14142a"/><circle cx="80" cy="44" r="3.4" fill="#111"/><circle cx="118" cy="44" r="3.4" fill="#111"/><rect x="68" y="40" width="62" height="1.4" fill="#ffcf5c"/></g>
<g stroke="#1a5c2a" stroke-width="1.6"><line x1="192" y1="28" x2="192" y2="16"/><line x1="192" y1="18" x2="184" y2="23"/><line x1="192" y1="18" x2="199" y2="23"/></g>
</svg>"""


def art_anthropic():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#eaf3fb")}
<rect x="14" y="38" width="172" height="1.6" fill="#334155"/><rect x="14" y="6" width="1.6" height="33" fill="#334155"/>
<g fill="#c96a2e"><rect x="26" y="30" width="15" height="8"/><rect x="46" y="26" width="15" height="12"/><rect x="66" y="22" width="15" height="16"/></g>
<g fill="#d97706"><rect x="86" y="18" width="15" height="20"/><rect x="106" y="13" width="15" height="25"/><rect x="126" y="8" width="15" height="30"/></g>
<polyline points="20,32 46,28 66,24 86,19 106,15 126,10 152,4" fill="none" stroke="#b45309" stroke-width="2.4"/>
<polygon points="152,4 143,4 150,10" fill="#b45309"/>
<text x="16" y="14" font-family="sans-serif" font-size="9" font-weight="bold" fill="#334155">$81.3B IPO</text>
<rect x="148" y="28" width="46" height="14" rx="2" fill="#111827"/><text x="171" y="38" font-family="sans-serif" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">ANT $83</text>
</svg>"""


def art_icj():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#d7e5f0")}
<rect y="38" width="200" height="8" fill="#8a97a3"/>
<polygon points="100,4 30,22 170,22" fill="#5b6b7a"/><polygon points="100,9 42,20 158,20" fill="#e8eef3"/>
<circle cx="100" cy="16" r="4" fill="#9b1c1c"/>
<g fill="#f4f7fa"><rect x="36" y="22" width="7" height="16"/><rect x="54" y="22" width="7" height="16"/><rect x="72" y="22" width="7" height="16"/><rect x="121" y="22" width="7" height="16"/><rect x="139" y="22" width="7" height="16"/><rect x="157" y="22" width="7" height="16"/></g>
<rect x="30" y="38" width="140" height="3" fill="#5b6b7a"/>
<rect x="172" y="28" width="26" height="12" rx="2" fill="#111"/><text x="185" y="37" font-family="sans-serif" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">9–6</text>
</svg>"""


def art_gulf():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="46" fill="#1d2b45"/><circle cx="172" cy="9" r="7" fill="#e8e4d0"/>
<g fill="#3a4a68"><rect x="8" y="30" width="24" height="10"/><rect x="38" y="24" width="28" height="16"/><rect x="72" y="31" width="22" height="9"/></g>
<g stroke="#8fa3c8" stroke-width="1.4" fill="none"><path d="M118 40 A26 26 0 0 1 170 40"/><path d="M126 40 A18 18 0 0 1 162 40"/><path d="M134 40 A10 10 0 0 1 154 40"/></g>
<line x1="144" y1="40" x2="144" y2="24" stroke="#c8d2e0" stroke-width="2.4"/><circle cx="144" cy="22" r="3.6" fill="#c8d2e0"/>
<g fill="#ffd94d"><polygon points="56,5 57.6,9.4 62,9.4 58.4,12 59.8,16.4 56,13.8 52.2,16.4 53.6,12 50,9.4 54.4,9.4"/><polygon points="108,4 109.4,8 113.4,8 110.2,10.4 111.4,14.4 108,12 104.6,14.4 105.8,10.4 102.6,8 106.6,8"/></g>
<g stroke="#ff6b6b" stroke-width="1.8"><line x1="84" y1="8" x2="90" y2="14"/><line x1="90" y1="8" x2="84" y2="14"/></g>
<rect y="40" width="200" height="6" fill="#0f1729"/>
</svg>"""


def art_gaza():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#e8d9b0")}
<circle cx="172" cy="10" r="8" fill="#ffdf8a"/>
<rect y="34" width="200" height="12" fill="#c9a86a"/><rect y="34" width="200" height="3" fill="#b08d4f"/>
<g><rect x="122" y="16" width="30" height="6" stroke="#3d4a2f" stroke-width="1.6" fill="none"/><line x1="152" y1="19" x2="180" y2="19" stroke="#3d4a2f" stroke-width="2.4"/><rect x="62" y="22" width="62" height="12" rx="3" fill="#5b6b42"/><rect x="74" y="15" width="28" height="8" rx="2" fill="#6b7a52"/><circle cx="76" cy="36" r="4.6" fill="#2f2a1e"/><circle cx="94" cy="36" r="4.6" fill="#2f2a1e"/><circle cx="112" cy="36" r="4.6" fill="#2f2a1e"/><rect x="66" y="33" width="54" height="6" rx="3" fill="#3d4a2f"/></g>
<rect x="8" y="34" width="30" height="10" rx="2" fill="#7a1f1f"/><text x="23" y="41.5" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#fff" text-anchor="middle">RAID</text>
</svg>"""


def art_akvan():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="46" fill="#274b63"/><rect y="36" width="200" height="10" fill="#1d5c7a"/>
<g fill="none" stroke="#e8f4f8" stroke-width="3" stroke-linecap="round"><path d="M100 23 a4 4 0 1 1 4 -4"/><path d="M100 23 a10 10 0 1 1 10 -10"/><path d="M100 23 a16 16 0 1 1 16 -16"/><path d="M100 23 a21 21 0 1 1 21 -21"/></g>
<circle cx="100" cy="23" r="3.4" fill="#ffd94d"/>
<g stroke="#9fd4e8" stroke-width="1.6"><line x1="28" y1="6" x2="25" y2="14"/><line x1="42" y1="4" x2="39" y2="12"/><line x1="158" y1="5" x2="155" y2="13"/><line x1="172" y1="8" x2="169" y2="16"/></g>
<path d="M0 36 Q50 31 100 36 T200 36 L200 46 L0 46 Z" fill="#2f7a9e"/>
<text x="8" y="44" font-family="sans-serif" font-size="9" font-weight="bold" fill="#fff">90–110 km/h</text>
</svg>"""


def art_florida():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="46" fill="#5b6b7a"/>
<g fill="#3d4a58"><ellipse cx="48" cy="10" rx="32" ry="8"/><ellipse cx="118" cy="8" rx="36" ry="8"/><ellipse cx="170" cy="12" rx="26" ry="7"/></g>
<g stroke="#bcd7ea" stroke-width="1.6"><line x1="30" y1="18" x2="27" y2="28"/><line x1="52" y1="19" x2="49" y2="29"/><line x1="76" y1="18" x2="73" y2="28"/><line x1="100" y1="19" x2="97" y2="29"/><line x1="124" y1="18" x2="121" y2="28"/><line x1="148" y1="19" x2="145" y2="29"/><line x1="172" y1="18" x2="169" y2="28"/></g>
<rect y="30" width="200" height="16" fill="#3f6d8e"/>
<g><rect x="12" y="20" width="30" height="12" fill="#8a5a3b"/><polygon points="9,21 27,10 45,21" fill="#5d3a24"/><rect x="23" y="25" width="8" height="7" fill="#2b1b12"/></g>
<g><path d="M120 38 L127 32 L158 32 L165 38 Z" fill="#c0392b"/><rect x="117" y="37" width="52" height="5" rx="2" fill="#7b241c"/><circle cx="128" cy="42" r="3" fill="#111"/><circle cx="158" cy="42" r="3" fill="#111"/></g>
<text x="8" y="44" font-family="sans-serif" font-size="9" font-weight="bold" fill="#fff">15.3 in / 24 h</text>
</svg>"""


def art_suneung():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#e3ecf5")}
<rect y="32" width="200" height="14" fill="#b99c7a"/>
<g><rect x="16" y="20" width="30" height="4" fill="#6b4f2e"/><rect x="72" y="20" width="30" height="4" fill="#6b4f2e"/><rect x="128" y="20" width="30" height="4" fill="#6b4f2e"/><rect x="44" y="34" width="30" height="4" fill="#6b4f2e"/><rect x="100" y="34" width="30" height="4" fill="#6b4f2e"/></g>
<g fill="#f2c89b"><circle cx="31" cy="15" r="5"/><circle cx="87" cy="15" r="5"/><circle cx="143" cy="15" r="5"/><circle cx="59" cy="29" r="5"/><circle cx="115" cy="29" r="5"/></g>
<g fill="#2e4a6b"><rect x="25" y="19" width="12" height="4"/><rect x="81" y="19" width="12" height="4"/><rect x="137" y="19" width="12" height="4"/><rect x="53" y="33" width="12" height="4"/><rect x="109" y="33" width="12" height="4"/></g>
<g fill="#fff"><rect x="25" y="17" width="12" height="3"/><rect x="81" y="17" width="12" height="3"/><rect x="137" y="17" width="12" height="3"/></g>
<circle cx="180" cy="10" r="8" fill="#fff" stroke="#334155" stroke-width="1.6"/><line x1="180" y1="10" x2="180" y2="4" stroke="#334155" stroke-width="1.6"/><line x1="180" y1="10" x2="185" y2="12" stroke="#334155" stroke-width="1.6"/>
<rect x="6" y="4" width="34" height="10" rx="2" fill="#111"/><text x="23" y="11.5" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#fff" text-anchor="middle">08:40</text>
</svg>"""


def art_colombia():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#f2e3c9")}
<rect y="34" width="200" height="12" fill="#9a8a72"/>
<rect x="16" y="4" width="168" height="7" fill="#f7d117"/><rect x="16" y="11" width="168" height="5" fill="#003087"/><rect x="16" y="16" width="168" height="4" fill="#ce1126"/>
<g fill="#2b2b2b"><circle cx="50" cy="26" r="4.6"/><circle cx="85" cy="26" r="4.6"/><circle cx="120" cy="26" r="4.6"/><circle cx="155" cy="26" r="4.6"/></g>
<g fill="#c0392b"><rect x="45" y="30" width="10" height="10"/><rect x="80" y="30" width="10" height="10"/><rect x="115" y="30" width="10" height="10"/><rect x="150" y="30" width="10" height="10"/></g>
<g fill="#fff" stroke="#334155"><rect x="64" y="22" width="24" height="12" rx="1"/><rect x="130" y="22" width="24" height="12" rx="1"/></g>
<text x="76" y="31" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#111" text-anchor="middle">NO</text>
<text x="142" y="31" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#111" text-anchor="middle">477</text>
</svg>"""


def art_jobless():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#eef2f5")}
<rect x="14" y="38" width="172" height="1.6" fill="#334155"/><rect x="14" y="6" width="1.6" height="33" fill="#334155"/>
<g fill="#64748b"><rect x="30" y="16" width="16" height="22"/><rect x="54" y="21" width="16" height="17"/><rect x="78" y="26" width="16" height="12"/><rect x="102" y="31" width="16" height="7"/></g>
<polyline points="26,13 50,18 74,24 98,30 124,35 152,40" fill="none" stroke="#b91c1c" stroke-width="2.4"/>
<polygon points="152,40 142,37 147,44" fill="#b91c1c"/>
<rect x="156" y="28" width="38" height="13" rx="2" fill="#b91c1c"/><text x="175" y="37.5" font-family="sans-serif" font-size="10" font-weight="bold" fill="#fff" text-anchor="middle">4.9%</text>
<text x="16" y="12" font-family="sans-serif" font-size="9" font-weight="bold" fill="#334155">−43,500 jobs</text>
</svg>"""


def art_indonesia():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#e6eef7")}
<rect x="12" y="4" width="26" height="14" fill="#fff"/><rect x="12" y="4" width="26" height="7" fill="#e11d2e"/>
<rect y="38" width="200" height="8" fill="#8a97a3"/>
<g stroke="#8a6d1f" stroke-width="1.6"><line x1="100" y1="10" x2="100" y2="38"/><line x1="78" y1="14" x2="122" y2="14"/><line x1="78" y1="14" x2="73" y2="23"/><line x1="78" y1="14" x2="83" y2="23"/><line x1="122" y1="14" x2="117" y2="23"/><line x1="122" y1="14" x2="127" y2="23"/></g>
<path d="M71 23 Q78 26 85 23 Z" fill="#c9a227"/><path d="M115 23 Q122 26 129 23 Z" fill="#c9a227"/>
<g transform="rotate(30 165 24)"><rect x="152" y="19" width="26" height="8" rx="2" fill="#6b4f2e"/><rect x="174" y="16" width="7" height="14" rx="2" fill="#8a6d4b"/></g>
<rect x="142" y="34" width="48" height="4" rx="2" fill="#5b4a33"/>
<rect x="46" y="26" width="24" height="11" rx="2" fill="#111"/><text x="58" y="34" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#fff" text-anchor="middle">Rp1bn</text>
</svg>"""


def art_cop31():
    return f"""<svg viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg">
{_sky("#dceef2")}
<circle cx="66" cy="23" r="19" fill="#3f7fb8"/>
<g fill="#5da85d"><ellipse cx="59" cy="18" rx="8" ry="5"/><ellipse cx="74" cy="29" rx="7" ry="4.6"/><ellipse cx="68" cy="11" rx="5" ry="3.4"/></g>
<path d="M47 23 a19 19 0 0 1 38 0" fill="none" stroke="#e8f4f8" stroke-width="1.2"/>
<g><rect x="150" y="5" width="9" height="28" rx="4" fill="#e8e8e8" stroke="#94a3b8" stroke-width="1.4"/><rect x="152" y="20" width="5" height="12" fill="#e11d2e"/><circle cx="154.5" cy="36" r="6.4" fill="#e11d2e"/><circle cx="154.5" cy="5" r="4.4" fill="#e8e8e8" stroke="#94a3b8" stroke-width="1.4"/></g>
<text x="154" y="45" font-family="sans-serif" font-size="7.5" font-weight="bold" fill="#334155" text-anchor="middle">+1.5°C</text>
<rect x="100" y="30" width="40" height="11" rx="2" fill="#0f766e"/><text x="120" y="38" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#fff" text-anchor="middle">COP31</text>
</svg>"""


ART = {
    "shenzhen": art_shenzhen, "gta": art_gta, "anthropic": art_anthropic,
    "icj": art_icj, "gulf": art_gulf, "gaza": art_gaza, "akvan": art_akvan,
    "florida": art_florida, "suneung": art_suneung, "colombia": art_colombia,
    "jobless": art_jobless, "indonesia": art_indonesia, "cop31": art_cop31,
}

# ---------------------------------------------------------------- world map
# Coarse land mask: 60 columns x 24 rows of dot cells. Each row lists
# inclusive column spans that are land. Hand-drawn approximation, good
# enough for a dotted locator map with numbered pins.
LAND_ROWS = [
    [(3, 13), (29, 31), (44, 55)],
    [(2, 14), (16, 18), (28, 33), (38, 56)],
    [(1, 15), (16, 17), (27, 34), (37, 57)],
    [(2, 13), (27, 35), (37, 58)],
    [(3, 12), (28, 34), (38, 57), (56, 57)],
    [(4, 9), (30, 36), (40, 46), (49, 53), (56, 56)],
    [(5, 8), (29, 37), (43, 46), (50, 54)],
    [(6, 9), (9, 12), (29, 38), (51, 55)],
    [(10, 13), (30, 38), (52, 56)],
    [(10, 13), (31, 37), (52, 57), (53, 58)],
    [(10, 13), (31, 36), (54, 59)],
    [(11, 13), (32, 35), (55, 58)],
    [(11, 12), (54, 57)],
    [(11, 12)],
    [(12, 12)],
    [(12, 12), (58, 58)],
    [(12, 12), (58, 58)],
    [(12, 12)],
    [(12, 12)],
    [(12, 12)],
    [(12, 12)],
    [(12, 12)],
    [(12, 12)],
    [(12, 12)],
]

# (lon, lat, dx, dy) for the 13 illustrated stories, numbered 1-13.
PINS = [
    (114, 22, 0, 0), (-80, 26, 0, 0), (-122, 37, 0, 0), (4.5, 52, 0, 0),
    (48, 29, 0, 0), (34.5, 31.4, 0, 0), (82, 17, 0, 0), (-81, 26.5, 13, 9),
    (127, 37.5, 0, 0), (-74, 4.7, 0, 0), (149, -35, 0, 0),
    (106.8, -6.2, 0, 0), (30.7, 36.9, 0, 0),
]


def map_svg():
    w, h = 312, 138
    cols, rows = 60, 24
    cw, ch = w / cols, h / rows
    dots = []
    for r, spans in enumerate(LAND_ROWS):
        for a, b in spans:
            for c in range(a, b + 1):
                dots.append(
                    f'<circle cx="{(c + 0.5) * cw:.1f}" cy="{(r + 0.5) * ch:.1f}" '
                    f'r="1.9" fill="#9aa5ad"/>'
                )
    pins = []
    for i, (lon, lat, dx, dy) in enumerate(PINS, 1):
        x = (lon + 180) / 360 * w + dx
        y = (80 - lat) / 135 * h + dy
        pins.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="#9b1c1c"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="none" stroke="#fff" stroke-width="1"/>'
            f'<text x="{x:.1f}" y="{y + 3:.1f}" font-family="sans-serif" font-size="8.5" '
            f'font-weight="bold" fill="#fff" text-anchor="middle">{i}</text>'
        )
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
        + "".join(dots) + "".join(pins) + "</svg>"
    )


# ---------------------------------------------------------------- HTML

def heroes_html(heroes):
    cells = "".join(
        f"""
      <article class="hero">
        <div class="hero-art">{ART[h['art']]()}</div>
        <div class="hero-kick">{esc(h['kicker'])} <span class="tag">{esc(h['tag'])}</span></div>
        <h2 class="clip clamp2">{h['n']}. {esc(h['headline'])}</h2>
        <p class="clip clamp4">{esc(h['body'])}</p>
      </article>"""
        for h in heroes
    )
    return f'<section class="heroes">{cells}\n    </section>'


def mains_html(mains):
    cells = "".join(
        f"""
      <article class="main">
        <div class="main-art">{ART[m['art']]()}</div>
        <div class="main-meta"><span class="region">{esc(m['region'])}</span> <span class="tag">{esc(m['tag'])}</span></div>
        <h3 class="clip clamp2">{m['n']}. {esc(m['headline'])}</h3>
        <p class="clip clamp4">{esc(m['fact'])}</p>
      </article>"""
        for m in mains
    )
    return f"""
    <div class="section-head">The day&rsquo;s main stories</div>
    <section class="mains">{cells}
    </section>"""


def briefs_html(briefs):
    cells = "".join(
        f"""
      <article class="brief clip clamp2"><b>{b['n']}. {esc(b['headline'])}</b> — {esc(b['fact'])}</article>"""
        for b in briefs
    )
    return cells


def build_html(data):
    stats = "".join(
        f'<div class="stat"><div class="stat-num">{esc(s["num"])}</div>'
        f'<div class="stat-label">{esc(s["label"])}</div></div>'
        for s in data["stats"]
    )
    regions = " &nbsp;·&nbsp; ".join(
        f"<b>{esc(r['name'])}</b> {r['n']}" for r in data["regions"]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #fff; font-family: "DejaVu Sans", sans-serif; color: #111; }}
  #page {{
    width: {PAGE_W}px; height: {PAGE_H}px; overflow: hidden;
    padding: 8px 20px 7px; background: #fdfcf6;
  }}
  .masthead {{ text-align: center; border-bottom: 3px solid #111; padding-bottom: 6px; }}
  .paper {{ font-size: 14px; font-weight: bold; letter-spacing: 5px; }}
  .date {{
    font-family: "Noto Serif", "DejaVu Serif", serif; font-weight: 800;
    font-size: 31px; line-height: 1.05; letter-spacing: 0.5px; margin-top: 1px;
  }}
  .subhead {{
    color: #9b1c1c; font-size: 12px; font-weight: bold; letter-spacing: 0.6px;
    margin-top: 3px;
  }}
  .stats {{
    display: grid; grid-template-columns: repeat(6, 1fr);
    border-bottom: 1px solid #999; padding: 5px 0 6px;
  }}
  .stat {{ text-align: center; border-left: 1px solid #ccc; padding: 0 4px; }}
  .stat:first-child {{ border-left: none; }}
  .stat-num {{ font-family: "Noto Serif", "DejaVu Serif", serif; font-weight: 800; font-size: 17px; color: #9b1c1c; }}
  .stat-label {{ font-size: 8.5px; color: #444; line-height: 1.25; }}
  .regions {{
    text-align: center; font-size: 10px; letter-spacing: 0.8px;
    padding: 4px 0 5px; border-bottom: 1px solid #999;
  }}
  .regions b {{ color: #9b1c1c; }}
  .heroes {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0 14px; padding-top: 7px; }}
  .hero-art svg {{ width: 100%; height: 68px; display: block; border: 1px solid #bbb; }}
  .hero-kick {{ color: #9b1c1c; font-size: 9.5px; font-weight: bold; letter-spacing: 1.2px; margin-top: 4px; }}
  .hero h2 {{
    font-family: "Noto Serif", "DejaVu Serif", serif; font-weight: 800;
    font-size: 16.5px; line-height: 1.18; margin: 2px 0 3px;
  }}
  .hero p {{ font-size: 10.5px; line-height: 1.4; color: #222; }}
  .tag {{
    display: inline-block; background: #e8e2d2; color: #555;
    font-size: 7.5px; font-weight: bold; letter-spacing: 0.8px;
    padding: 1px 4px; border-radius: 2px; vertical-align: 1px;
  }}
  .section-head {{
    font-size: 10.5px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;
    border-bottom: 2px solid #111; padding-bottom: 2px; margin: 7px 0 6px;
  }}
  .mains {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px 12px; }}
  .main-art svg {{ width: 100%; height: 46px; display: block; border: 1px solid #bbb; }}
  .main-meta {{ margin-top: 3px; }}
  .main .region {{ color: #9b1c1c; font-size: 8.5px; font-weight: bold; letter-spacing: 1px; }}
  .main h3 {{
    font-family: "Noto Serif", "DejaVu Serif", serif; font-weight: 800;
    font-size: 11.5px; line-height: 1.22; margin: 1px 0 2px;
  }}
  .main p {{ font-size: 9.5px; line-height: 1.35; color: #222; }}
  .lower {{ display: flex; gap: 14px; margin-top: 2px; }}
  .mapbox {{ width: 326px; flex: none; }}
  .mapbox h4, .briefbox h4 {{
    font-size: 10.5px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase;
    border-bottom: 2px solid #111; padding-bottom: 2px; margin-bottom: 4px;
  }}
  .mapbox svg {{ width: 100%; height: 118px; display: block; }}
  .mapkey {{ font-size: 8.5px; line-height: 1.4; color: #444; margin-top: 2px; }}
  .briefbox {{ flex: 1; }}
  .briefs {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2px 12px; }}
  .brief {{ font-size: 8.8px; line-height: 1.3; color: #222; }}
  .brief b {{ color: #111; }}
  .legend {{
    display: flex; justify-content: center; gap: 16px; margin-top: 4px;
    font-size: 9px; color: #444; border-top: 1px solid #999; padding-top: 3px;
  }}
  .legend .tag {{ font-size: 8px; }}
  .datecheck {{
    background: #f3ede0; border-left: 4px solid #9b1c1c;
    font-size: 9px; line-height: 1.35; color: #333; padding: 4px 8px; margin-top: 3px;
  }}
  .datecheck b {{ color: #9b1c1c; letter-spacing: 0.8px; }}
  .footer {{
    display: flex; justify-content: space-between; margin-top: 3px;
    font-size: 9.5px; color: #666; letter-spacing: 0.5px;
  }}
  .clip {{ overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; }}
  .clamp2 {{ -webkit-line-clamp: 2; }}
  .clamp3 {{ -webkit-line-clamp: 3; }}
  .clamp4 {{ -webkit-line-clamp: 4; }}
</style>
</head>
<body>
<div id="page">
  <header class="masthead">
    <div class="paper">{esc(data['paper'])}</div>
    <div class="date">{esc(data['date_label'])}</div>
    <div class="subhead">{esc(data['subhead'])}</div>
  </header>
  <section class="stats">{stats}</section>
  <div class="regions">{regions}</div>
  {heroes_html(data['heroes'])}
  {mains_html(data['mains'])}
  <div class="lower">
    <div class="mapbox">
      <h4>Where it happened</h4>
      {map_svg()}
      <div class="mapkey">Pins 1–13 mark the illustrated stories above: 1 Shenzhen · 2 Vice City · 3 San Francisco · 4 The Hague · 5 Kuwait · 6 Gaza · 7 Bay of Bengal · 8 Florida · 9 Seoul · 10 Bogotá · 11 Canberra · 12 Jakarta · 13 Antalya.</div>
    </div>
    <div class="briefbox">
      <h4>Also on Thursday 19 November</h4>
      <section class="briefs">{briefs_html(data['briefs'])}
      </section>
    </div>
  </div>
  <div class="legend"><span><b>HOW SURE ARE WE?</b></span><span><span class="tag">REPORTED</span> confirmed by a source</span><span><span class="tag">CLAIM</span> one side&rsquo;s claim</span><span><span class="tag">FORECAST</span> prediction, not yet happened</span></div>
  <div class="datecheck"><b>DATE CHECK</b> — {esc(data['datecheck'])}</div>
  <div class="footer">
    <span>{esc(data['footer'])}</span>
    <span>{esc(data['sources'])}</span>
  </div>
</div>
</body>
</html>"""


def render(out_path):
    data = json.loads((REPO / "stories.json").read_text(encoding="utf-8"))
    n = len(data["heroes"]) + len(data["mains"]) + len(data["briefs"])
    print(f"stories: {n} ({len(data['heroes'])} heroes + "
          f"{len(data['mains'])} mains + {len(data['briefs'])} briefs)")
    html = build_html(data)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(html)
        tmp_path = tmp.name
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                args=["--no-sandbox", "--disable-dev-shm-usage",
                      "--force-color-profile=srgb"]
            )
            page = browser.new_page(
                viewport={"width": PAGE_W, "height": PAGE_H},
                device_scale_factor=1,
            )
            page.goto(Path(tmp_path).as_uri())
            page.wait_for_load_state("load")
            failures = page.evaluate(GUARD_JS)
            if failures:
                print("LAYOUT GUARD FAILED:", file=sys.stderr)
                for f in failures:
                    print(f"  - {f}", file=sys.stderr)
                browser.close()
                return 1
            out_path.parent.mkdir(parents=True, exist_ok=True)
            page.locator("#page").screenshot(path=str(out_path))
            browser.close()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    with Image.open(out_path) as img:
        if img.format != "PNG" or img.size != (PAGE_W, PAGE_H):
            print(f"BAD PNG: format={img.format} size={img.size}", file=sys.stderr)
            return 1
    if out_path.stat().st_size > 1048576:
        print(f"PNG TOO BIG: {out_path.stat().st_size} bytes > 1 MiB", file=sys.stderr)
        return 1
    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"wrote {out_path}  {out_path.stat().st_size} bytes  sha256={digest}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=REPO / "assets" / "entry.png")
    args = parser.parse_args()
    return render(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
