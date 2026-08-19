"""Build a single self-contained value-dex HTML from data.js + the visualizer CSV."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from parse_values import attach_values

CSV = Path(r"c:\Users\maxxo\Downloads\loomian_stat_visualizer_v4_5_data (1).csv")
DEX_JS = Path(r"C:\Users\maxxo\loomian-value-dex\data.js")
OUTS = [
    Path(r"C:\Users\maxxo\loomian-value-dex\index.html"),
    Path(r"C:\Users\maxxo\Downloads\loomian-value-dex.html"),
    Path(r"C:\Users\maxxo\.cursor\projects\C-Users-maxxo-AppData-Local-Temp-8262e711-32f2-4126-9a5c-e26b4cc7a425\index.html"),
]

SOULBURST = {
    "Flychomp", "Terraform", "Magmadire", "Lavafiend", "Incarnate", "Jetwing",
    "Seascourge", "Thunderking", "Atomic", "Tempereign", "Overcharged",
    "Willbound", "Stellarchime", "Frostshackled", "Archfiend",
}
SKIP_FORMS = {"Cracked", "Unleashed"}
MOCHI = {"Mochibi", "Mocho", "Totemochi"}
# Only Ornament Scorb has a glitch Gamma (same sprites, marked icon).

MOCHI_ORDER = ["Pink", "Green", "Yellow", "Cyan", "White", "Red", "Lime", "Magenta", "Purple"]
MOCHI_HALLOWEEN_ORDER = ["Red", "Green", "Orange", "Yellow", "Lime", "Purple", "Black", "Pink", "Blue"]
COLOR_ORDER = [
    "Male", "Female", "Base", "Pink", "Red", "Orange", "Yellow", "Green", "Lime",
    "Cyan", "Blue", "Purple", "Violet", "Magenta", "Teal", "Brown", "White",
    "Black", "Bronze", "Silver", "Gold", "Ruby", "Emerald", "Sapphire",
    "Rainbow", "1", "2", "3", "4", "5", "6", "Glass",
]
VARI_LINE = {
    "Vari", "Cervolen", "Wendolen", "Kirolen", "Zepholen", "Venolen",
    "Wresolen", "Buzzolen", "Tundrolen", "Pyrolen", "Hydrolen",
}
EGG_SPECIES = {"Kyeggo", "Doreggo", "Dreggodyne"}
NO_SA_RAINBOW = {"Duskit", "Twilat"}
FABERGE_ORDER = [
    "Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Teal", "Cyan",
    "Magenta", "Rainbow",
]
COSMIORE_RAINBOW_ORDER = ["Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Rainbow"]


def parse_csv():
    rows = []
    with CSV.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            name = (r.get("name") or "").strip().strip('"')
            if not name:
                continue
            types = [t for t in (r.get("types") or "").split("/") if t]
            abs_ = r.get("abilities") or ""
            has_sa = "[SA]" in abs_
            rows.append({"name": name, "types": types, "hasSA": has_sa})
    return rows


def form_of(name: str):
    m = re.match(r"^(.+?)\s*\((.+)\)\s*$", name)
    if not m:
        return name, None
    return m.group(1), m.group(2)


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def load_dex():
    text = DEX_JS.read_text(encoding="utf-8")
    m = re.search(r"window\.DEX = (\{.*\});", text, re.S)
    if not m:
        return {"loomians": []}
    return json.loads(m.group(1))


def sort_colors(species: str, reskin: str | None, colors: list[dict]) -> list[dict]:
    by = {c["name"]: c for c in colors}
    if species in MOCHI:
        order = MOCHI_HALLOWEEN_ORDER if reskin == "Halloween Rainbow" else MOCHI_ORDER
    else:
        order = COLOR_ORDER
    out: list[dict] = []
    seen: set[str] = set()
    for name in order:
        if name in by:
            out.append(by[name])
            seen.add(name)
    for c in colors:
        if c["name"] not in seen:
            out.append(c)
    return out


def colors_from(p: dict) -> list[dict]:
    colors = []
    for v in p.get("variants") or []:
        files = v.get("files") or {}
        item = {
            "name": v.get("name") or v.get("id") or "Base",
            "files": {
                "normal": files.get("normal"),
                "alpha": files.get("alpha"),
                "gamma": files.get("gamma"),
            },
        }
        if any(item["files"].values()):
            colors.append(item)
    return sort_colors(p.get("species") or "", p.get("reskin"), colors)


def refresh_gleams(card: dict) -> None:
    colors = card.get("colors") or []
    card["hasAlpha"] = any((c.get("files") or {}).get("alpha") for c in colors)
    if card.get("gammaGlitch"):
        card["hasGamma"] = True
    else:
        card["hasGamma"] = any((c.get("files") or {}).get("gamma") for c in colors)


def sort_named(colors: list[dict], order: list[str]) -> list[dict]:
    by = {c["name"]: c for c in colors}
    out = []
    seen = set()
    for name in order:
        if name in by:
            out.append(by[name])
            seen.add(name)
    for c in colors:
        if c["name"] not in seen:
            out.append(c)
    return out


def split_cosmiore(cards: list[dict]) -> None:
    src = next((c for c in cards if c["species"] == "Cosmiore" and not c["reskin"]), None)
    if not src:
        return
    rainbow, keep = [], []
    for col in src["colors"]:
        name = col["name"]
        if name.lower() == "rainbow" or "colored" in name.lower():
            label = re.sub(r"\s*colored$", "", name, flags=re.I).strip() or name
            rainbow.append({"name": label, "files": col["files"]})
        else:
            keep.append(col)
    if not rainbow:
        return
    src["colors"] = sort_colors("Cosmiore", None, keep)
    refresh_gleams(src)
    cards.append({
        "id": "Cosmiore__Rainbow",
        "name": "Cosmiore (Rainbow)",
        "species": "Cosmiore",
        "reskin": "Rainbow",
        "types": list(src["types"]),
        "hasSA": src["hasSA"],
        "hasAlpha": False,
        "hasGamma": False,
        "gammaGlitch": False,
        "cycle": False,
        "colors": sort_named(rainbow, COSMIORE_RAINBOW_ORDER),
    })
    refresh_gleams(cards[-1])


def split_faberge(cards: list[dict]) -> None:
    by_key = {(c["species"], c["reskin"]): c for c in cards}
    for species in EGG_SPECIES:
        gathered = []
        for reskin in (None, "Rainbow"):
            card = by_key.get((species, reskin))
            if not card:
                continue
            keep, take = [], []
            for col in card["colors"]:
                if "faberge" in col["name"].lower():
                    label = re.sub(r"\s*faberge$", "", col["name"], flags=re.I).strip() or col["name"]
                    take.append({"name": label, "files": col["files"]})
                else:
                    keep.append(col)
            if take:
                card["colors"] = keep
                refresh_gleams(card)
                gathered.extend(take)
        if not gathered:
            continue
        # de-dupe by display name, prefer later (rainbow) if clash
        merged = {c["name"]: c for c in gathered}
        cards.append({
            "id": f"{species}__Faberge",
            "name": f"{species} (Faberge)",
            "species": species,
            "reskin": "Faberge",
            "types": list((by_key.get((species, None)) or by_key.get((species, "Rainbow")) or {"types": []})["types"]),
            "hasSA": bool((by_key.get((species, None)) or {}).get("hasSA")),
            "hasAlpha": False,
            "hasGamma": False,
            "gammaGlitch": False,
            "cycle": False,
            "colors": sort_named(list(merged.values()), FABERGE_ORDER),
        })
        refresh_gleams(cards[-1])


def rename_vari_base(cards: list[dict]) -> None:
    for card in cards:
        if card["species"] not in VARI_LINE:
            continue
        for col in card.get("colors") or []:
            if col["name"] == "Base":
                col["name"] = "Male"
        card["colors"] = sort_colors(card["species"], card["reskin"], card["colors"])


def card_from_dex(p: dict, csv_by_species: dict) -> dict | None:
    species = p.get("species") or ""
    reskin = p.get("reskin")
    if reskin in SOULBURST:
        return None
    if reskin in SKIP_FORMS:
        return None
    # Native Mochi colors are not a "Rainbow" event reskin.
    if species in MOCHI and reskin == "Rainbow":
        return None
    colors = colors_from(p)
    if not colors:
        return None
    csv_row = csv_by_species.get(species) or {}
    types = p.get("types") or csv_row.get("types") or []
    has_sa = bool(p.get("hasSA") if p.get("hasSA") is not None else csv_row.get("hasSA"))
    if species in NO_SA_RAINBOW and reskin == "Rainbow":
        has_sa = False
    has_alpha = any(c["files"].get("alpha") for c in colors)
    has_real_gamma = any(c["files"].get("gamma") for c in colors)
    glitch = species == "Scorb" and reskin == "Ornament" and not has_real_gamma
    # Native Mochi colors and Halloween Rainbow colors share one value; cycle sprites.
    # Unique reskins like Totemochi (Snowman) keep a single sprite set.
    cycle = species in MOCHI and reskin in {None, "Halloween Rainbow"}
    display = p.get("displayName") or (f"{species} ({reskin})" if reskin else species)
    return {
        "id": p.get("id") or f"{species}__{reskin or 'Normal'}",
        "name": display,
        "species": species,
        "reskin": reskin,
        "types": types,
        "hasSA": has_sa,
        "hasAlpha": has_alpha,
        "hasGamma": has_real_gamma or glitch,
        "gammaGlitch": glitch,
        "cycle": cycle,
        "colors": colors,
    }


def covered(species: str, form: str | None, cards: list[dict]) -> bool:
    if form in SKIP_FORMS:
        return True
    if form in SOULBURST:
        return True
    for p in cards:
        if p["species"] != species:
            continue
        if not form and not p["reskin"]:
            return True
        if form and p["reskin"] and norm(form) == norm(p["reskin"]):
            return True
        if form == "Encased" and species == "Cosmiore" and not p["reskin"]:
            return True
        if form and any(norm(c["name"]) == norm(form) for c in p.get("colors") or []):
            return True
    return False


def csv_files(species: str, form: str | None) -> dict:
    if form in ("male",):
        return {
            "normal": f"{species}-menu.png",
            "alpha": f"{species}-Alpha-menu.png",
            "gamma": f"{species}-Gamma-menu.png",
        }
    if form in ("female",):
        return {
            "normal": f"{species}-F-menu.png",
            "alpha": f"{species}-F-Alpha-menu.png",
            "gamma": f"{species}-F-Gamma-menu.png",
        }
    if not form or form in {"Base", "Encased"}:
        prefix = species if form != "Encased" else f"{species}-Encased-Green"
        return {
            "normal": f"{prefix}-menu.png" if form != "Encased" else f"{species}-Encased-Green-menu.png",
            "alpha": f"{species}-Alpha-menu.png" if form != "Encased" else f"{species}-Encased-Green-Alpha-menu.png",
            "gamma": f"{species}-Gamma-menu.png" if form != "Encased" else f"{species}-Encased-Green-Gamma-menu.png",
        }
    part = "-".join(w.capitalize() for w in form.replace("'s", "").split())
    return {
        "normal": f"{species}-{part}-menu.png",
        "alpha": f"{species}-{part}-Alpha-menu.png",
        "gamma": f"{species}-{part}-Gamma-menu.png",
    }


def build_list():
    csv_rows = parse_csv()
    csv_by_species = {}
    for r in csv_rows:
        species, form = form_of(r["name"])
        if not form:
            csv_by_species[species] = r

    out = []
    for p in (load_dex().get("loomians") or []):
        card = card_from_dex(p, csv_by_species)
        if card:
            out.append(card)

    split_cosmiore(out)
    split_faberge(out)
    rename_vari_base(out)

    for r in csv_rows:
        species, form = form_of(r["name"])
        if covered(species, form, out):
            continue
        if form in SOULBURST or form in SKIP_FORMS:
            continue
        files = csv_files(species, form)
        display = species if form == "Encased" else r["name"]
        reskin = None if form in {None, "Encased"} else form
        out.append({
            "id": f"{species}__{reskin or 'Normal'}",
            "name": display,
            "species": species,
            "reskin": reskin,
            "types": r["types"],
            "hasSA": r["hasSA"],
            "hasAlpha": True,
            "hasGamma": True,
            "gammaGlitch": False,
            "cycle": species in MOCHI and reskin in {None, "Halloween Rainbow"},
            "colors": [{"name": form or "Base", "files": files}],
        })

    seen = set()
    uniq = []
    for x in out:
        if not x.get("colors"):
            continue
        if x["id"] in seen:
            continue
        seen.add(x["id"])
        uniq.append(x)
    uniq.sort(key=lambda x: (x["species"].lower(), 0 if not x["reskin"] else 1, x["name"].lower()))
    stats = attach_values(uniq)
    print("values", stats["matched"], "/", stats["entries"], "valued", stats["valued"], "valueless", stats["valueless"], "radiant", stats["radiant"], "fe", stats["fe"])
    if stats["unmatched"]:
        print("unmatched sample", stats["unmatched"][:15])
    return uniq


HTML_HEAD = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Loomian Value Dex</title>
<style>
:root{--ink:#e5e7eb;--muted:#94a3b8;--line:#334155;--bg:#0b1220;--card-bg:#152033;--panel-bg:#152033;--input-bg:#0f172a}
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--bg);color:var(--ink)}
header{background:linear-gradient(135deg,#020617,#1e293b);color:white;padding:22px}
header h1{margin:0 0 6px;font-size:28px}
header p{margin:0;color:#94a3b8;line-height:1.45;max-width:1100px}
main{max-width:1420px;margin:0 auto;padding:16px}
.panel{background:var(--panel-bg);border:1px solid var(--line);border-radius:14px;padding:14px;display:grid;gap:10px;margin-bottom:12px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
input,select,button{font:inherit;border:1px solid #4b5563;border-radius:8px;padding:9px 10px;background:var(--input-bg);color:var(--ink)}
input{min-width:220px;flex:1}
select{min-width:145px}
button{cursor:pointer;font-weight:700;background:#111827;color:white;border-color:#111827}
button.secondary{background:var(--card-bg);color:var(--ink)}
.help{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:10px;font-size:13px;line-height:1.45;color:#cbd5e1}
.status{margin:12px 0;color:#cbd5e1;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(325px,1fr));gap:12px}
.card-shell{border-radius:16px;padding:3px}
.card{background:var(--card-bg);border-radius:14px;padding:12px;min-height:210px;display:flex;flex-direction:column}
.card-head{display:flex;align-items:flex-start;gap:8px}
.loom-sprite,.na-sprite{width:56px;height:56px;flex-shrink:0;border-radius:6px;background:#f3f4f6;object-fit:contain;image-rendering:pixelated}
.na-sprite{display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#64748b;border:1px dashed #475569;background:#0f172a}
.head-text{min-width:0;flex:1}
.head-text h3{margin:0 0 6px;font-size:17px;line-height:1.2}
.badges{display:flex;flex-wrap:wrap;gap:5px}
.badge{font-size:11px;border-radius:999px;padding:3px 7px;border:1px solid #475569;background:#1e293b;color:#e2e8f0}
.type-badge-colored{border-color:transparent;font-weight:700;color:#fff;text-shadow:0 1px 1px #0006}
.type-Light,.type-Ice,.type-Electric,.type-Air,.type-Simple{color:#111!important;text-shadow:none}
.badge.reskin{background:#312e81;border-color:#6366f1;color:#e0e7ff}
.badge.cat{background:#134e4a;border-color:#2dd4bf;color:#ccfbf1}
.color-row{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0 2px}
.color-chip{font-size:11px;border-radius:999px;padding:3px 8px;border:1px solid #475569;background:#1e293b;color:#fff;cursor:pointer;font-weight:700;line-height:1.3}
.color-chip.active{box-shadow:0 0 0 2px #7dd3fc}
.icon-row{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0 6px}
.icon-btn{background:none;border:none;padding:0;cursor:pointer;width:72px;opacity:.55;transition:transform .15s,opacity .15s,filter .15s}
.icon-btn svg{width:72px;height:82px;display:block;filter:drop-shadow(0 3px 5px rgba(0,0,0,.4))}
.icon-btn:hover{opacity:.9}
.icon-btn.active{opacity:1;transform:scale(1.07)}
.icon-btn.active svg{filter:drop-shadow(0 0 8px rgba(255,255,255,.25)) drop-shadow(0 3px 6px rgba(0,0,0,.45))}
.icon-btn.glitch svg{animation:glitch 1.4s steps(2,end) infinite}
.icon-btn.glitch.active svg{animation:glitch 0.45s steps(2,end) infinite}
@keyframes glitch{
  0%{transform:translate(0);filter:none}
  20%{transform:translate(-1px,1px);filter:hue-rotate(70deg) saturate(1.6)}
  40%{transform:translate(1px,-1px);filter:hue-rotate(-80deg)}
  60%{transform:translate(-1px,0);filter:none}
  100%{transform:translate(0);filter:none}
}
.value-slot{margin-top:auto;min-height:64px;border:1px dashed #334155;border-radius:10px;padding:10px;background:linear-gradient(180deg,#0f172a,#152033)}
.value-slot.na{display:flex;align-items:center;justify-content:center}
.na-big{font-size:22px;font-weight:800;letter-spacing:.12em;color:#64748b}
.value-slot .v-top{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.value-slot .v-label{font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:#94a3b8;font-weight:700}
.demand{font-size:10px;font-weight:800;border-radius:999px;padding:3px 8px;color:#fff;text-transform:uppercase;letter-spacing:.04em}
.fe-banner{background:linear-gradient(90deg,#b45309,#fbbf24);color:#111;font-size:11px;font-weight:800;border-radius:6px;padding:4px 8px;margin:0 0 6px}
.v-rows{display:grid;gap:4px;max-height:168px;overflow:auto}
.v-row{display:flex;justify-content:space-between;gap:8px;font-size:12px;line-height:1.3;border-bottom:1px solid #1e293b;padding:3px 0}
.v-row span{color:#cbd5e1}
.v-row b{color:#f8fafc;white-space:nowrap}
.v-note{margin-top:6px;font-size:11px;color:#94a3b8;line-height:1.35}
.v-sub{margin-top:8px;font-size:10px;font-weight:800;color:#7dd3fc;text-transform:uppercase;letter-spacing:.04em}
.chk{display:flex;align-items:center;gap:6px;font-size:13px;color:#cbd5e1}
.filters-panel{display:none}
.filters-panel.open{display:block}
footer{padding:20px;text-align:center;color:#64748b;font-size:12px}
@media(max-width:720px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
  <h1>Loomian Value Dex</h1>
  <p>Pick Secret / Alpha / Gamma / Radiant to see that form’s trade value. Missing values show N/A. Hide valueless Loomians with the filter.</p>
</header>
<main>
<section class="panel">
  <div class="help">Values are in GR (Gleam Roam). Event reskins are extra cards. Color pills swap the sprite. Use the event filter for Halloween, Christmas, Anniversary, and the rest.</div>
  <div class="row">
    <input id="search" placeholder="Search name or reskin...">
    <button type="button" id="filtersToggle" class="secondary">Filters ▾</button>
    <button type="button" id="reset" class="secondary">Reset</button>
  </div>
  <div id="filtersPanel" class="filters-panel">
    <div class="row">
      <select id="catFilter"><option value="All">All</option><option value="normal">Species only</option><option value="reskin">Reskins only</option></select>
      <select id="typeFilter"></select>
      <select id="eventFilter"></select>
      <label class="chk"><input type="checkbox" id="hideValueless"> Hide valueless</label>
    </div>
  </div>
</section>
<p id="status" class="status"></p>
<section id="grid" class="grid"></section>
</main>
<footer>Single-file page — open this HTML in Chrome or Edge. No extra files needed.</footer>
<script>
'''

HTML_TAIL = r'''
const ICONS={
  sa:`<svg viewBox="0 0 80 92"><defs><radialGradient id="saOrb" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#e9d5ff"/><stop offset="45%" stop-color="#b57edc"/><stop offset="100%" stop-color="#5b2c6f"/></radialGradient><linearGradient id="saBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#d2a6ea"/><stop offset="100%" stop-color="#7d3c98"/></linearGradient></defs><circle cx="40" cy="34" r="29" fill="#3b1f4a"/><circle cx="40" cy="34" r="27" fill="url(#saOrb)"/><circle cx="40" cy="34" r="27" fill="none" stroke="#f3e8ff" stroke-width="1.4" opacity=".55"/><ellipse cx="31" cy="23" rx="11" ry="6.5" fill="#fff" opacity=".28"/><path d="M52 14l1.8 3.7 4 .6-2.9 2.8.7 4-3.6-2-3.6 2 .7-4-2.9-2.8 4-.6z" fill="#fde68a"/><path d="M18 28l1.2 2.5 2.7.4-2 2 .5 2.7-2.4-1.3-2.4 1.3.5-2.7-2-2 2.7-.4z" fill="#fde68a" opacity=".9"/><text x="40" y="47" text-anchor="middle" font-size="30" font-weight="800" font-family="Georgia,serif" fill="#2b1736">S</text><rect x="7" y="66" width="66" height="20" rx="5" fill="url(#saBan)"/><text x="40" y="81" text-anchor="middle" font-size="11" font-weight="800" font-family="Arial" fill="#f8f0ff">SECRET</text></svg>`,
  alpha:`<svg viewBox="0 0 80 92"><defs><radialGradient id="alOrb" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#e0f7ff"/><stop offset="50%" stop-color="#7ec8e3"/><stop offset="100%" stop-color="#1d6f8a"/></radialGradient><linearGradient id="alBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#b9e7f5"/><stop offset="100%" stop-color="#3d8eaa"/></linearGradient></defs><circle cx="40" cy="34" r="29" fill="#16495c"/><circle cx="40" cy="34" r="27" fill="url(#alOrb)"/><circle cx="40" cy="34" r="27" fill="none" stroke="#f0fbff" stroke-width="1.4" opacity=".55"/><ellipse cx="31" cy="23" rx="11" ry="6.5" fill="#fff" opacity=".32"/><path d="M40 8l1.2 3.4 3.6.1-2.8 2.2 1 3.4-3-1.9-3 1.9 1-3.4-2.8-2.2 3.6-.1z" fill="#fff8dc"/><path d="M61 24l1 2.2 2.4.3-1.8 1.7.4 2.3-2-1.1-2 1.1.4-2.3-1.8-1.7 2.4-.3z" fill="#fff8dc"/><text x="40" y="47" text-anchor="middle" font-size="32" font-family="Times New Roman,serif" fill="#143844">α</text><rect x="7" y="66" width="66" height="20" rx="5" fill="url(#alBan)"/><text x="40" y="81" text-anchor="middle" font-size="11" font-weight="800" font-family="Arial" fill="#0f2f3a">ALPHA</text></svg>`,
  gamma:`<svg viewBox="0 0 80 92"><defs><radialGradient id="gaOrb" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#e8fff4"/><stop offset="50%" stop-color="#8fd9b6"/><stop offset="100%" stop-color="#1f7a55"/></radialGradient><linearGradient id="gaBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#c6f0d8"/><stop offset="100%" stop-color="#3aa874"/></linearGradient></defs><circle cx="40" cy="34" r="29" fill="#14553c"/><circle cx="40" cy="34" r="27" fill="url(#gaOrb)"/><circle cx="40" cy="34" r="27" fill="none" stroke="#f0fff7" stroke-width="1.4" opacity=".55"/><ellipse cx="31" cy="23" rx="11" ry="6.5" fill="#fff" opacity=".3"/><path d="M22 16l1.5 3.2 3.5.4-2.6 2.4.6 3.5-3-1.7-3 1.7.6-3.5-2.6-2.4 3.5-.4z" fill="#fef08a"/><path d="M58 40l1.1 2.4 2.6.3-2 1.9.5 2.6-2.2-1.3-2.2 1.3.5-2.6-2-1.9 2.6-.3z" fill="#fef08a"/><text x="40" y="47" text-anchor="middle" font-size="32" font-family="Times New Roman,serif" fill="#143d2c">γ</text><rect x="7" y="66" width="66" height="20" rx="5" fill="url(#gaBan)"/><text x="40" y="81" text-anchor="middle" font-size="11" font-weight="800" font-family="Arial" fill="#0f3324">GAMMA</text></svg>`,
  radiant:`<svg viewBox="0 0 80 92"><defs><radialGradient id="rdOrb" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#ffd2b3"/><stop offset="45%" stop-color="#ff8040"/><stop offset="100%" stop-color="#c2410c"/></radialGradient><linearGradient id="rdBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ff9a5c"/><stop offset="100%" stop-color="#ea580c"/></linearGradient></defs><circle cx="40" cy="34" r="29" fill="#7c2d12"/><circle cx="40" cy="34" r="27" fill="url(#rdOrb)"/><circle cx="40" cy="34" r="27" fill="none" stroke="#ffedd5" stroke-width="1.4" opacity=".5"/><ellipse cx="31" cy="23" rx="11" ry="6.5" fill="#fff" opacity=".25"/><text x="40" y="47" text-anchor="middle" font-size="34" font-family="Times New Roman,serif" fill="#4b3621">ρ</text><rect x="7" y="66" width="66" height="20" rx="5" fill="url(#rdBan)"/><text x="40" y="81" text-anchor="middle" font-size="10" font-weight="800" font-family="Arial" fill="#4b3621">RADIANT</text></svg>`,
  firstEdition:`<svg viewBox="0 0 80 92"><defs><radialGradient id="feOrb" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#fef3c7"/><stop offset="50%" stop-color="#fbbf24"/><stop offset="100%" stop-color="#b45309"/></radialGradient><linearGradient id="feBan" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#fcd34d"/><stop offset="100%" stop-color="#d97706"/></linearGradient></defs><circle cx="40" cy="34" r="29" fill="#78350f"/><circle cx="40" cy="34" r="27" fill="url(#feOrb)"/><circle cx="40" cy="34" r="27" fill="none" stroke="#fffbeb" stroke-width="1.4" opacity=".55"/><ellipse cx="31" cy="23" rx="11" ry="6.5" fill="#fff" opacity=".3"/><text x="40" y="44" text-anchor="middle" font-size="20" font-weight="800" font-family="Arial" fill="#4b3621">1st</text><rect x="7" y="66" width="66" height="20" rx="5" fill="url(#feBan)"/><text x="40" y="81" text-anchor="middle" font-size="9" font-weight="800" font-family="Arial" fill="#4b3621">1ST EDITION</text></svg>`
};
const TYPE_COLOR={Fire:'#e74c3c',Water:'#3498db',Plant:'#2ecc71',Light:'#f6e58d',Dark:'#3d2e28',Ice:'#7ed6df',Electric:'#f9ca24',Air:'#a5b4fc',Bug:'#8b9a3c',Earth:'#c4a04a',Toxic:'#c080e0',Metal:'#7f8c8d',Ancient:'#8b8bc8',Spirit:'#6c2eb9',Brawler:'#a0522d',Mind:'#ff69b4',Simple:'#c8c8c8'};
const CHIP_COLOR={Red:'#c0392b',Orange:'#e67e22',Yellow:'#f1c40f',Green:'#27ae60',Lime:'#a3e635',Cyan:'#22d3ee',Blue:'#2563eb',Purple:'#7c3aed',Violet:'#8b5cf6',Magenta:'#d946ef',Pink:'#ec4899',White:'#e5e7eb',Black:'#111827',Bronze:'#b45309',Silver:'#94a3b8',Gold:'#d4af37',Ruby:'#be123c',Emerald:'#059669',Sapphire:'#1d4ed8',Brown:'#8b5a2b',Teal:'#0d9488',Male:'#3b82f6',Female:'#ec4899'};
const LABELS={sa:'Secret Ability',alpha:'Alpha',gamma:'Gamma',radiant:'Radiant',firstEdition:'First Edition',event:'Normal'};
const state=new Map();
function md5cycle(x,k){var a=x[0],b=x[1],c=x[2],d=x[3];
a=ff(a,b,c,d,k[0],7,-680876936);d=ff(d,a,b,c,k[1],12,-389564586);c=ff(c,d,a,b,k[2],17,606105819);b=ff(b,c,d,a,k[3],22,-1044525330);
a=ff(a,b,c,d,k[4],7,-176418897);d=ff(d,a,b,c,k[5],12,1200080426);c=ff(c,d,a,b,k[6],17,-1473231341);b=ff(b,c,d,a,k[7],22,-45705983);
a=ff(a,b,c,d,k[8],7,1770035416);d=ff(d,a,b,c,k[9],12,-1958414417);c=ff(c,d,a,b,k[10],17,-42063);b=ff(b,c,d,a,k[11],22,-1990404162);
a=ff(a,b,c,d,k[12],7,1804603682);d=ff(d,a,b,c,k[13],12,-40341101);c=ff(c,d,a,b,k[14],17,-1502002290);b=ff(b,c,d,a,k[15],22,1236535329);
a=gg(a,b,c,d,k[1],5,-165796510);d=gg(d,a,b,c,k[6],9,-1069501632);c=gg(c,d,a,b,k[11],14,643717713);b=gg(b,c,d,a,k[0],20,-373897302);
a=gg(a,b,c,d,k[5],5,-701558691);d=gg(d,a,b,c,k[10],9,38016083);c=gg(c,d,a,b,k[15],14,-660478335);b=gg(b,c,d,a,k[4],20,-405537848);
a=gg(a,b,c,d,k[9],5,568446438);d=gg(d,a,b,c,k[14],9,-1019803690);c=gg(c,d,a,b,k[3],14,-187363961);b=gg(b,c,d,a,k[8],20,1163531501);
a=gg(a,b,c,d,k[13],5,-1444681467);d=gg(d,a,b,c,k[2],9,-51403784);c=gg(c,d,a,b,k[7],14,1735328473);b=gg(b,c,d,a,k[12],20,-1926607734);
a=hh(a,b,c,d,k[5],4,-378558);d=hh(d,a,b,c,k[8],11,-2022574463);c=hh(c,d,a,b,k[11],16,1839030562);b=hh(b,c,d,a,k[14],23,-35309556);
a=hh(a,b,c,d,k[1],4,-1530992060);d=hh(d,a,b,c,k[4],11,1272893353);c=hh(c,d,a,b,k[7],16,-155497632);b=hh(b,c,d,a,k[10],23,-1094730640);
a=hh(a,b,c,d,k[13],4,681279174);d=hh(d,a,b,c,k[0],11,-358537222);c=hh(c,d,a,b,k[3],16,-722521979);b=hh(b,c,d,a,k[6],23,76029189);
a=hh(a,b,c,d,k[9],4,-640364487);d=hh(d,a,b,c,k[12],11,-421815835);c=hh(c,d,a,b,k[15],16,530742520);b=hh(b,c,d,a,k[2],23,-995338651);
a=ii(a,b,c,d,k[0],6,-198630844);d=ii(d,a,b,c,k[7],10,1126891415);c=ii(c,d,a,b,k[14],15,-1416354905);b=ii(b,c,d,a,k[5],21,-57434055);
a=ii(a,b,c,d,k[12],6,1700485571);d=ii(d,a,b,c,k[3],10,-1894986606);c=ii(c,d,a,b,k[10],15,-1051523);b=ii(b,c,d,a,k[1],21,-2054922799);
a=ii(a,b,c,d,k[8],6,1873313359);d=ii(d,a,b,c,k[15],10,-30611744);c=ii(c,d,a,b,k[6],15,-1560198380);b=ii(b,c,d,a,k[13],21,1309151649);
a=ii(a,b,c,d,k[4],6,-145523070);d=ii(d,a,b,c,k[11],10,-1120210379);c=ii(c,d,a,b,k[2],15,718787259);b=ii(b,c,d,a,k[9],21,-343485551);
x[0]=add32(a,x[0]);x[1]=add32(b,x[1]);x[2]=add32(c,x[2]);x[3]=add32(d,x[3])}
function cmn(q,a,b,x,s,t){a=add32(add32(a,q),add32(x,t));return add32((a<<s)|(a>>>(32-s)),b)}
function ff(a,b,c,d,x,s,t){return cmn((b&c)|((~b)&d),a,b,x,s,t)}
function gg(a,b,c,d,x,s,t){return cmn((b&d)|(c&(~d)),a,b,x,s,t)}
function hh(a,b,c,d,x,s,t){return cmn(b^c^d,a,b,x,s,t)}
function ii(a,b,c,d,x,s,t){return cmn(c^(b|(~d)),a,b,x,s,t)}
function md51(s){var n=s.length,state=[1732584193,-271733879,-1732584194,271733878],i;for(i=64;i<=n;i+=64)md5cycle(state,md5blk(s.substring(i-64,i)));s=s.substring(i-64);var tail=Array(16).fill(0);for(i=0;i<s.length;i++)tail[i>>2]|=s.charCodeAt(i)<<((i%4)<<3);tail[i>>2]|=0x80<<((i%4)<<3);if(i>55){md5cycle(state,tail);tail=Array(16).fill(0)}tail[14]=n*8;md5cycle(state,tail);return state}
function md5blk(s){var md5blks=[],i;for(i=0;i<64;i+=4)md5blks[i>>2]=s.charCodeAt(i)+(s.charCodeAt(i+1)<<8)+(s.charCodeAt(i+2)<<16)+(s.charCodeAt(i+3)<<24);return md5blks}
var hex_chr='0123456789abcdef'.split('');
function rhex(n){var s='',j;for(j=0;j<4;j++)s+=hex_chr[(n>>(j*8+4))&0x0F]+hex_chr[(n>>(j*8))&0x0F];return s}
function hex(x){for(var i=0;i<x.length;i++)x[i]=rhex(x[i]);return x.join('')}
function add32(a,b){return(a+b)&0xFFFFFFFF}
function md5(s){return hex(md51(s))}
function spriteUrlFromFile(file){if(!file)return '';const h=md5(file);return 'https://static.wikia.nocookie.net/loomian-legacy/images/'+h[0]+'/'+h[0]+h[1]+'/'+encodeURIComponent(file)+'/revision/latest'}
function escapeHtml(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function typeColor(t){return TYPE_COLOR[t]||'#999'}
function typeBadge(t){const dark=['Light','Ice','Electric','Air','Simple'].includes(t);return `<span class="badge type-badge-colored type-${t}" style="background:${typeColor(t)};color:${dark?'#111':'#fff'}">${escapeHtml(t)}</span>`}
function adjustHex(hex,amt){hex=String(hex).replace('#','');if(hex.length===3)hex=hex.split('').map(c=>c+c).join('');var n=parseInt(hex,16),r=(n>>16)+amt,g=((n>>8)&255)+amt,b=(n&255)+amt;r=Math.max(0,Math.min(255,r));g=Math.max(0,Math.min(255,g));b=Math.max(0,Math.min(255,b));return '#'+((1<<24)|(r<<16)|(g<<8)|b).toString(16).slice(1)}
function cardShellStyle(types){var t=(types&&types.length)?types:['Simple'];var c1=typeColor(t[0]);if(t.length<2){var bright=adjustHex(c1,40),dark=adjustHex(c1,-35);return 'background:linear-gradient(135deg,'+bright+','+c1+','+dark+')'}return 'background:linear-gradient(135deg,'+c1+','+typeColor(t[1])+')'}
function stOf(p){if(!state.has(p.id))state.set(p.id,{gleam:p.defaultGleam||null,color:0,fe:false});return state.get(p.id)}
function gleamKey(gleam){if(!gleam||gleam==='sa'||gleam==='radiant'||gleam==='event'||gleam==='firstEdition')return 'normal';return gleam}
function cycleFiles(p,gleam){
  const key=gleamKey(gleam);
  let files=(p.colors||[]).map(c=>(c.files||{})[key]).filter(Boolean);
  if(!files.length && key==='gamma' && p.gammaGlitch){
    files=(p.colors||[]).map(c=>(c.files||{}).normal||(c.files||{}).alpha).filter(Boolean);
  }
  if(!files.length) files=(p.colors||[]).map(c=>(c.files||{}).normal).filter(Boolean);
  return files;
}
function selectedColor(p){
  const colors=p.colors||[];
  const st=stOf(p);
  let i=st.color|0;
  if(i<0||i>=colors.length)i=0;
  return colors[i]||colors[0]||{files:{}};
}
function fileFor(p,gleam){
  if(p.cycle){
    const files=cycleFiles(p,gleam);
    return files[0]||'';
  }
  const f=(selectedColor(p).files)||{};
  const key=gleamKey(gleam);
  if(key==='alpha') return f.alpha||'';
  if(key==='gamma') return f.gamma||(p.gammaGlitch?(f.normal||f.alpha||''):'');
  return f.normal||'';
}
function spriteHtml(p,gleam){
  if(p.cycle){
    const files=cycleFiles(p,gleam);
    if(!files.length) return `<div class="na-sprite">N/A</div>`;
    const url=spriteUrlFromFile(files[0]);
    return `<img class="loom-sprite" data-cycle="${escapeHtml(JSON.stringify(files))}" data-idx="0" loading="lazy" src="${escapeHtml(url)}" alt="" onerror="this.outerHTML='<div class=\\'na-sprite\\'>N/A</div>'">`;
  }
  const file=fileFor(p,gleam);
  if(!file)return `<div class="na-sprite">N/A</div>`;
  const url=spriteUrlFromFile(file);
  const fallback=(p.species||p.name)+'-menu.png';
  const fb=spriteUrlFromFile(fallback);
  return `<img class="loom-sprite" loading="lazy" src="${escapeHtml(url)}" alt="" onerror="if(!this.dataset.fb){this.dataset.fb=1;this.src='${fb}';return}this.outerHTML='<div class=\\'na-sprite\\'>N/A</div>'">`;
}
function canShow(p,kind){
  if(kind==='sa')return !!p.hasSA;
  if(kind==='alpha')return !!p.hasAlpha;
  if(kind==='gamma')return !!p.hasGamma;
  if(kind==='radiant')return !!p.hasRadiant;
  if(kind==='firstEdition')return !!p.hasFirstEdition;
  return true;
}
function iconBtn(p,kind,active){
  if(!canShow(p,kind))return '';
  const glitch=(kind==='gamma'&&p.gammaGlitch)?' glitch':'';
  return `<button type="button" class="icon-btn ${kind}${glitch}${active?' active':''}" data-id="${escapeHtml(p.id)}" data-gleam="${kind}" title="${escapeHtml(LABELS[kind])}">${ICONS[kind]}</button>`;
}
function chipStyle(name){
  if(name==='Rainbow') return 'background:linear-gradient(90deg,#e74c3c,#f1c40f,#2ecc71,#3498db,#9b59b6);border-color:transparent;color:#fff';
  const bg=CHIP_COLOR[name];
  if(!bg)return '';
  const dark=['Yellow','Lime','Cyan','White','Silver','Gold'].includes(name);
  return `background:${bg};border-color:transparent;color:${dark?'#111':'#fff'}`;
}
function pickValue(p,gleam,colorName){
  const vals=p.values||{};
  const key=gleam||'event';
  const blob=vals[key]||(!gleam?vals.event:null);
  if(!blob)return null;
  const by=blob.byColor||{};
  if(colorName&&by[colorName]) return by[colorName];
  if(blob.rows&&blob.rows.length) return blob;
  const first=Object.values(by)[0];
  return first||null;
}
function renderBlob(blob,label,feText){
  if(!blob||!(blob.rows&&blob.rows.length)&&!blob.demand&&!(blob.notes&&blob.notes.length)){
    return `<div class="value-slot na"><div class="na-big">N/A</div></div>`;
  }
  const demand=blob.demand?`<span class="demand" style="background:${blob.demandColor||'#475569'}">${escapeHtml(blob.demand)}</span>`:'';
  const fe=feText?`<div class="fe-banner">${escapeHtml(feText)}</div>`:'';
  const rows=(blob.rows||[]).map(r=>`<div class="v-row"><span>${escapeHtml(r.n)}</span><b>${escapeHtml(r.v)}</b></div>`).join('');
  const note=[blob.ineffective?('Ineffective: '+blob.ineffective):'',...(blob.notes||[])].filter(Boolean).map(escapeHtml).join('<br>');
  let extras='';
  if(blob.extras){
    for(const [k,ex] of Object.entries(blob.extras)){
      extras+=`<div class="v-sub">${escapeHtml(LABELS[k]||k)} Radiant</div>`+(ex.rows||[]).map(r=>`<div class="v-row"><span>${escapeHtml(r.n)}</span><b>${escapeHtml(r.v)}</b></div>`).join('');
    }
  }
  return `<div class="value-slot"><div class="v-top"><span class="v-label">${escapeHtml(label)}</span>${demand}</div>${fe}<div class="v-rows">${rows}${extras}</div>${note?`<div class="v-note">${note}</div>`:''}</div>`;
}
function valueSlot(p){
  const st=stOf(p);
  const gleam=st.gleam||null;
  const colorName=(selectedColor(p).name)||'';
  const blob=pickValue(p,gleam,colorName);
  const feOn=!!st.fe;
  const feText=feOn?((blob&&blob.firstEdition)||'First Edition'):'';
  const label=LABELS[gleam||'event']||'Value';
  return renderBlob(blob,label,feText);
}
function colorRow(p){
  const colors=p.colors||[];
  if(p.cycle || colors.length<2) return '';
  const st=stOf(p);
  return `<div class="color-row">${colors.map((c,i)=>`<button type="button" class="color-chip${i===st.color?' active':''}" style="${chipStyle(c.name)}" data-id="${escapeHtml(p.id)}" data-color="${i}">${escapeHtml(c.name)}</button>`).join('')}</div>`;
}
function card(p){
  const st=stOf(p);
  const gleam=st.gleam||null;
  const types=(p.types||[]).map(typeBadge).join('')||'<span class="badge">Type unknown</span>';
  const reskin=p.reskin?`<span class="badge reskin">${escapeHtml(p.reskin)}</span>`:'';
  const cat=p.category&&p.category!=='Non-event'?`<span class="badge cat">${escapeHtml(p.category)}</span>`:'';
  return `<div class="card-shell" style="${cardShellStyle(p.types)}" data-card="${escapeHtml(p.id)}">
    <article class="card">
      <div class="card-head">${spriteHtml(p,gleam)}<div class="head-text"><h3>${escapeHtml(p.name)}</h3><div class="badges">${types}${reskin}${cat}</div></div></div>
      ${colorRow(p)}
      <div class="icon-row">${iconBtn(p,'sa',gleam==='sa')}${iconBtn(p,'alpha',gleam==='alpha')}${iconBtn(p,'gamma',gleam==='gamma')}${iconBtn(p,'radiant',gleam==='radiant')}${iconBtn(p,'firstEdition',!!st.fe)}</div>
      ${valueSlot(p)}
    </article></div>`;
}
function render(){
  const q=(search.value||'').toLowerCase().trim();
  const cat=catFilter.value, type=typeFilter.value, ev=eventFilter.value;
  const hide=hideValueless.checked;
  let list=LOOMIANS.slice();
  if(q)list=list.filter(p=>(p.name+' '+(p.reskin||'')+' '+(p.category||'')+' '+(p.types||[]).join(' ')+' '+(p.colors||[]).map(c=>c.name).join(' ')).toLowerCase().includes(q));
  if(cat==='normal')list=list.filter(p=>!p.reskin);
  if(cat==='reskin')list=list.filter(p=>!!p.reskin);
  if(type!=='All')list=list.filter(p=>(p.types||[]).includes(type));
  if(ev&&ev!=='All')list=list.filter(p=>(p.category||'Non-event')===ev);
  if(hide)list=list.filter(p=>!p.valueless);
  grid.innerHTML=list.map(card).join('');
  status.textContent='Showing '+list.length+' of '+LOOMIANS.length+' Loomians';
}
function replaceCard(id){
  const p=LOOMIANS.find(x=>x.id===id);
  const shell=document.querySelector('[data-card="'+CSS.escape(id)+'"]');
  if(shell&&p)shell.outerHTML=card(p);
}
const search=document.getElementById('search');
const catFilter=document.getElementById('catFilter');
const typeFilter=document.getElementById('typeFilter');
const eventFilter=document.getElementById('eventFilter');
const hideValueless=document.getElementById('hideValueless');
const filtersToggle=document.getElementById('filtersToggle');
const filtersPanel=document.getElementById('filtersPanel');
const grid=document.getElementById('grid');
const status=document.getElementById('status');
typeFilter.innerHTML='<option value="All">All types</option>'+[...new Set(LOOMIANS.flatMap(p=>p.types||[]))].sort().map(t=>'<option value="'+t+'">'+t+'</option>').join('');
eventFilter.innerHTML='<option value="All">All events</option>'+[...new Set(LOOMIANS.map(p=>p.category||'Non-event'))].sort().map(t=>'<option value="'+t+'">'+t+'</option>').join('');
filtersToggle.onclick=()=>{filtersPanel.classList.toggle('open');filtersToggle.textContent=filtersPanel.classList.contains('open')?'Filters ▴':'Filters ▾'};
document.getElementById('reset').onclick=()=>{search.value='';catFilter.value='All';typeFilter.value='All';eventFilter.value='All';hideValueless.checked=false;render()};
grid.addEventListener('click',e=>{
  const chip=e.target.closest('.color-chip');
  if(chip){
    const id=chip.getAttribute('data-id');
    const i=+chip.getAttribute('data-color');
    const st=state.get(id)||{gleam:null,color:0,fe:false};
    st.color=i;
    state.set(id,st);
    replaceCard(id);
    return;
  }
  const btn=e.target.closest('.icon-btn');
  if(!btn)return;
  const id=btn.getAttribute('data-id');
  const kind=btn.getAttribute('data-gleam');
  const st=state.get(id)||{gleam:null,color:0,fe:false};
  if(kind==='firstEdition'){
    st.fe=!st.fe;
  }else{
    st.gleam=st.gleam===kind?null:kind;
  }
  state.set(id,st);
  replaceCard(id);
});
[search,catFilter,typeFilter,eventFilter,hideValueless].forEach(el=>el.addEventListener('input',render));
hideValueless.addEventListener('change',render);
setInterval(()=>{
  document.querySelectorAll('img.loom-sprite[data-cycle]').forEach(img=>{
    let files;
    try{files=JSON.parse(img.getAttribute('data-cycle')||'[]')}catch(err){return}
    if(!files||files.length<2)return;
    const i=((+img.dataset.idx||0)+1)%files.length;
    img.dataset.idx=i;
    img.src=spriteUrlFromFile(files[i]);
  });
}, 850);
render();
</script>
</body>
</html>
'''


def main():
    loomians = build_list()
    payload = "const LOOMIANS = " + json.dumps(loomians, ensure_ascii=False, separators=(",", ":")) + ";\n"
    html = HTML_HEAD + payload + HTML_TAIL
    for p in OUTS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding="utf-8")
        print("wrote", p, "bytes", p.stat().st_size)
    print("cards", len(loomians), "reskins", sum(1 for x in loomians if x["reskin"]))
    print("cycle", [x["name"] for x in loomians if x.get("cycle")])
    print("glitch-gamma", [x["name"] for x in loomians if x.get("gammaGlitch")])
    multi = [x["name"] for x in loomians if len(x.get("colors") or []) > 1 and not x.get("cycle")]
    print("color-select", len(multi), "sample", multi[:12])
    ceph = next((x for x in loomians if x["name"].startswith("Cephalops (Halloween")), None)
    if ceph:
        print("cephalops halloween colors", [c["name"] for c in ceph["colors"]], "gamma", ceph["hasGamma"])
    mocho = next((x for x in loomians if x["name"] == "Mocho"), None)
    if mocho:
        print("mocho cycle", mocho["cycle"], "colors", [c["name"] for c in mocho["colors"]])
    scorb = next((x for x in loomians if x["name"] == "Scorb (Ornament)"), None)
    if scorb:
        print("ornament", "glitch", scorb["gammaGlitch"], "colors", [c["name"] for c in scorb["colors"]])
    for n in ["Cosmiore", "Cosmiore (Rainbow)", "Kyeggo", "Kyeggo (Rainbow)", "Kyeggo (Faberge)",
              "Doreggo (Faberge)", "Dreggodyne (Faberge)", "Duskit (Rainbow)", "Twilat (Rainbow)",
              "Vari", "Cervolen"]:
        hit = next((x for x in loomians if x["name"] == n), None)
        if hit:
            print(n, "reskin", hit["reskin"], "sa", hit["hasSA"], "colors", [c["name"] for c in hit["colors"]])
    rainbow_wisp = "rainbowWisp" in html
    print("rainbowWisp leftover", rainbow_wisp)
    rainbow_mochi = [x["name"] for x in loomians if x["species"] in MOCHI and x.get("reskin") == "Rainbow"]
    print("mochi rainbow reskins", rainbow_mochi)


if __name__ == "__main__":
    main()
