"""Parse the Discord value dump and attach values to value-dex cards."""
from __future__ import annotations

import re
from pathlib import Path

VALUES_PATH = Path(r"c:\Users\maxxo\Downloads\massive list of loomian vales.txt")

DEMAND_EMOJI = {
    "🟪": ("OP", "#a855f7"),
    "🟣": ("OP", "#a855f7"),
    "🟦": ("Good", "#3b82f6"),
    "🟩": ("Alright", "#22c55e"),
    "🟧": ("Decent", "#f97316"),
    "🟠": ("Decent", "#f97316"),
    "🟥": ("Bad", "#ef4444"),
    "🟫": ("Horrendous", "#92400e"),
}

FAMILIES = [
    ["Slugling", "Escargrow", "Gastroak"],
    ["Gumpod", "Ventacean"],
    ["Pyramind", "Pharoglyph"],
    ["Elephage", "Phagenaut"],
    ["Geklow", "Eleguana"],
    ["Copling", "Copperage", "Oxidrake"],
    ["Scorb", "Scoria", "Gardrone"],
    ["Goppie", "Arapaigo"],
    ["Kyeggo", "Doreggo", "Dreggodyne"],
    ["Kyogo", "Dorogo"],
    ["Twittle", "Paratweet", "Avitross"],
    ["Embit", "Rabburn", "Searknight"],
    ["Dripple", "Reptide", "Luminami"],
    ["Fevine", "Felunge", "Tahtab"],
    ["Eaglit", "Torprey", "Falkyrie"],
    ["Vambat", "Dimpire", "Vesperatu"],
    ["Snocub", "Snowl", "Himbrr"],
    ["Weevolt", "Zuelong"],
    ["Territi", "Dyeborg"],
    ["Taoshi", "Taoshinu"],
    ["Mistlebud", "Hollibunch"],
    ["Cryocub", "Barbadger"],
    ["Impkin", "Grimpire", "Imperior"],
    ["Volpup", "Halvantic"],
    ["Bunpuff", "Bunnecki"],
    ["Dractus", "Frutress", "Seedrake"],
    ["Snicle", "Slivyce", "Sylvice"],
    ["Antsee", "Florant"],
    ["Igneol", "Chrysite", "Obsidrugon"],
    ["Operator", "Tyrecks"],
    ["Sharpod", "Samarine"],
    ["Llamba", "Choochew", "Loomala"],
    ["Kleptyke", "Ragoon"],
    ["Somata", "Clionae"],
    ["Polypi", "Jellusa"],
    ["Teripod", "Teridescent"],
    ["Dokan", "Dokumori"],
    ["Terracolt", "Broncotta"],
    ["Pipsee", "Whippledriff"],
    ["Hydrini", "Deludrix"],
    ["Wispur", "Lampurge", "Charonyx"],
    ["Smoal", "Charkiln", "Billoforge"],
    ["Nymvolt", "Ohmbolt", "Plasmoth"],
    ["Pyke", "Skelic"],
    ["Dobo", "Infernix"],
    ["Zaleo", "Joltooth"],
    ["Ceratot", "Trepodon", "Colossotrops"],
    ["Nautling", "Nautillect", "Naukout"],
    ["Venile", "Verinosaur"],
    ["Yutiny", "Yutyphoon"],
    ["Swimp", "Snapr", "Garlash"],
    ["Pwuff", "Bloatox", "Barblast"],
    ["Whimpor", "Stratusoar"],
    ["Poochrol", "Hunder"],
    ["Pyder", "Swolder"],
    ["Kanki", "Kanibo"],
    ["Wiledile", "Mawamurk"],
    ["Makame", "Tsukame"],
    ["Snagull", "Snagulp", "Snagoop"],
    ["Lantot", "Lantorch"],
    ["Eyebrella", "Parasoul"],
    ["Milgoo", "Rancidor"],
    ["Lissen", "Biwarned"],
    ["Leopaw", "Chienta"],
    ["Kayute", "Kramboss"],
    ["Wassel", "Borealisk"],
    ["Snowl", "Wintrix"],
    ["Fentern", "Weaslin"],
    ["Mirami", "Mirrami"],
    ["Cafnote", "Moomoo", "Bullson"],
    ["Craytal", "Krakoco", "Volpaca"],
    ["Skilava", "Geksplode", "Eruptidon"],
    ["Phancub", "Ursoul", "Ursnac"],
    ["Crabush", "Lobol", "Clubrush"],
    ["Twilat", "Umbrat", "Luxoar", "Tiklipse"],
    ["Vari", "Cervolen", "Wendolen", "Kirolen", "Zepholen", "Venolen", "Wresolen", "Buzzolen", "Tundrolen", "Pyrolen", "Hydrolen"],
    ["Mochibi", "Mocho", "Totemochi"],
    ["Cinnaboo", "Cinnogre"],
    ["Kittone", "Lyricat"],
    ["Geklow", "Eleguana"],
    ["Veylens", "Geklow"],
]

ALIASES = {
    "beheremoth": "Behemoroth",
    "behemoroth": "Behemoroth",
    "dorogo": "Doreggo",
    "kyogo": "Kyeggo",
    "seesdrake": "Seedrake",
    "seedrake": "Seedrake",
    "faberage": "Faberge",
    "sandwhich": "Snagull",
    "propae": "Propae",
    "lantot": "Lantot",
    "lantorch": "Lantorch",
    "weaslin": "Weaslin",
    "fentern": "Fentern",
    "mirriami": "Mirami",
    "mirami": "Mirami",
    "copperag": "Copperage",
    "copperage": "Copperage",
    "scoriax": "Gardrone",
    "gardrone": "Gardrone",
    "nautillect": "Nautillect",
    "naukout": "Naukout",
    "whippledriff": "Whippledriff",
    "charonyx": "Charonyx",
    "billoforge": "Billoforge",
    "plasmoth": "Plasmoth",
    "colossotrops": "Colossotrops",
    "verinosaur": "Verinosaur",
    "yutyphoon": "Yutyphoon",
    "snagoop": "Snagoop",
    "halvantic": "Halvantic",
    "nevermare": "Nevermare",
    "metronette": "Metronette",
    "wabalisc": "Wabalisc",
    "akhalos": "Akhalos",
    "grimyuline": "Grimyuline",
    "boonary": "Boonary",
    "cosmeleon": "Cosmeleon",
    "gobbidemic": "Gobbidemic",
    "shawchi": "Shawchi",
    "sherbot": "Sherbot",
    "obsidrugon": "Obsidrugon",
    "tyrecks": "Tyrecks",
    "samarine": "Samarine",
    "stratusoar": "Stratusoar",
    "ventacean": "Ventacean",
    "pharoglyph": "Pharoglyph",
    "pyramind": "Pyramind",
    "ikazune": "Ikazune",
    "protogon": "Protogon",
    "mutagon": "Mutagon",
    "cephalops": "Cephalops",
    "duskit": "Duskit",
    "dakuda": "Dakuda",
    "arceros": "Arceros",
    "glacadia": "Glacadia",
    "cosmiore": "Cosmiore",
    "icigool": "Icigool",
    "goppie": "Goppie",
    "arapaigo": "Arapaigo",
    "cynamoth": "Cynamoth",
    "florant": "Florant",
    "choochew": "Choochew",
    "nymaurae": "Nymaurae",
    "teridescent": "Teridescent",
    "eleguana": "Eleguana",
    "twilat": "Twilat",
    "gastroak": "Gastroak",
    "escargrow": "Escargrow",
    "slugling": "Slugling",
    "ragoon": "Ragoon",
    "mochi": "Mochibi",
    "dreggo": "Doreggo",
    "mirriami": "Mirami",
}

EGG_PATTERNS = [
    "Frilly", "Zigzag", "Striped", "Star", "Arches", "Triangle Striped", "Runic",
    "Gold", "Diamond", "Watermelon", "Wavy", "Pyramind", "2024", "2025", "Uncommon",
]


def pattern_from_title(title: str) -> str | None:
    if re.search(r"\d+\s*Star Goppie", title, re.I):
        return None
    t = title.lower()
    if "default 2025" in t or "2025 kyeggo" in t:
        return "2025"
    for p in EGG_PATTERNS:
        if p.lower() in t:
            return p
    return None


ICIGOOL_COLORS = {
    "lightblue": ["Base"],
    "wild": ["Base"],
    "2019": ["Red", "Yellow", "Green", "Indigo"],
    "2020": ["Black", "Navy", "Pink", "White"],
    "2021": ["Maroon", "Dark Green", "Orange", "Brown"],
    "2022": ["Polka Dot", "Zigzag", "Checkered", "Snowflake", "Pixel", "Floral", "Yellow Pattern", "Maroon Pattern"],
    "2023": ["Navy", "Maroon", "Orange", "Dark Green"],
    "2024": ["Star", "Plaid", "Circuit", "Honeycomb"],
    "2025": ["Red", "Yellow", "Green", "Indigo", "Black", "Navy", "Pink", "White", "Maroon", "Dark Green", "Orange", "Brown"],
}

TAG_RE = re.compile(r":[a-z0-9~_]+:", re.I)
DEMAND_RE = re.compile(r"Demand:\s*([🟪🟣🟦🟩🟧🟠🟥🟫])", re.I)
INEFF_RE = re.compile(r"Ineffective Personalit(?:y|ies)\s*:?\s*\(?([^)\n]*)", re.I)
ROW_RE = re.compile(r"^(.+?)\s*=\s*(.+)$")
FE_RE = re.compile(r"first\s*edition\s*[:=]?\s*([+\-]?\s*[\d.]+(?:\s*GR)?)", re.I)
SKIP_LINE = re.compile(
    r"^(Village Chief|APP|Role icon|-- |— |\d{2}/\d{2}/\d{4}|Values:|:[\w~]+:?\s*$)",
    re.I,
)

SECTION_MAP = [
    (re.compile(r"HALLOWEEN", re.I), "Halloween"),
    (re.compile(r"CHRISTMAS", re.I), "Christmas"),
    (re.compile(r"ANNIVERSARY", re.I), "Anniversary"),
    (re.compile(r"RAINBOW LOOM", re.I), "Rainbow"),
    (re.compile(r"VALENTINE", re.I), "Valentine's"),
    (re.compile(r"LUNAR", re.I), "Lunar New Year"),
    (re.compile(r"EASTER", re.I), "Easter"),
    (re.compile(r"PVP RESKIN", re.I), "PVP"),
    (re.compile(r"SPECIAL RESKIN", re.I), "Special"),
    (re.compile(r"METEOR", re.I), "Meteor"),
    (re.compile(r"Non event", re.I), "Non-event"),
]


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def is_title(line: str) -> bool:
    if SKIP_LINE.match(line.strip()):
        return False
    if re.search(r":(sa~1|alpha1|gamma1|event|radiant):", line, re.I):
        return True
    if re.match(r"^\d+\s*Star Goppie", line, re.I):
        return True
    return False


def strip_tags(s: str) -> str:
    return TAG_RE.sub(" ", s)


def parse_gleam(title: str) -> str:
    t = title.lower()
    radiant = ":radiant:" in t or bool(re.search(r"\bradiant\b", t))
    if ":sa~1:" in t or re.search(r"\bsa\b", t):
        gleam = "sa"
    elif ":alpha1:" in t or re.search(r"\b(alpha|gleam)\b", t):
        gleam = "alpha"
    elif ":gamma1:" in t or re.search(r"\bgamma\b", t):
        gleam = "gamma"
    elif ":event:" in t:
        gleam = "event"
    else:
        gleam = "event"
    if radiant and gleam in {"event", "sa"}:
        gleam = "radiant"
    elif radiant and gleam == "alpha":
        gleam = "radiantAlpha"
    elif radiant and gleam == "gamma":
        gleam = "radiantGamma"
    return gleam


def parse_reskin(title: str, section: str) -> str | None:
    t = title.lower()
    checks = [
        ("halloween rainbow", "Halloween Rainbow"),
        ("halloween", "Halloween"),
        ("christmas", "Holiday"),
        ("santa", "Holiday"),
        ("lunar", "Lunar New Year"),
        ("valentine", "Valentine's"),
        ("anniversary", "Birthday"),
        ("rainbow faberge", "Faberge"),
        ("faberge", "Faberge"),
        ("faberage", "Faberge"),
        ("rainbow", "Rainbow"),
        ("plush", "Plush"),
        ("toy", "Toy"),
        ("surfer", "Surfer"),
        ("tennis", "Tennis Tag"),
        ("lifeguard", "Lifeguard"),
        ("easter", "Easter"),
        ("mecha", "Mecha"),
        ("cosmic", "Cosmic"),
        ("ornament", "Ornament"),
        ("glass scorb", "Ornament"),
        ("patterned scorb", "Ornament"),
        ("gemstone", "Gemstone"),
        ("bronze", "Gemstone"),
        ("silver", "Gemstone"),
        ("gold", "Gemstone"),
        ("ruby", "Gemstone"),
        ("emerald", "Gemstone"),
        ("sapphire", "Gemstone"),
        ("hat", "Hat"),
        ("fisher", "Summer"),
        ("snowman", "Snowman"),
        ("holiday", "Holiday"),
    ]
    for needle, reskin in checks:
        if needle in t:
            return reskin
    if section in {"Halloween", "Christmas", "Valentine's", "Lunar New Year", "Rainbow", "Easter", "Anniversary"}:
        return None
    return None


def gem_color(title: str) -> str | None:
    t = title.lower()
    for c in ("Bronze", "Silver", "Gold", "Ruby", "Emerald", "Sapphire"):
        if c.lower() in t:
            return c
    return None


def expand_family(names: list[str]) -> list[str]:
    out = list(names)
    nset = {norm(n) for n in names}
    for fam in FAMILIES:
        fn = [norm(x) for x in fam]
        hits = [i for i, x in enumerate(fn) if x in nset]
        if len(hits) >= 2:
            lo, hi = min(hits), max(hits)
            for sp in fam[lo : hi + 1]:
                if sp not in out:
                    out.append(sp)
        elif len(hits) == 1 and "-" in "".join(names):
            # Kyeggo-Dreggodyne style: one end matched via alias later
            pass
    # If Kyeggo and Dreggodyne both present, add Doreggo
    if {"kyeggo", "dreggodyne"} <= {norm(x) for x in out} and "Doreggo" not in out:
        out.append("Doreggo")
    if {"slugling", "gastroak"} <= {norm(x) for x in out} and "Escargrow" not in out:
        out.append("Escargrow")
    return out


def extract_names(title: str, known: dict[str, str]) -> list[str]:
    raw = strip_tags(title)
    raw = re.sub(
        r"\b(SA|Alpha|Gleam|Gamma|Radiant|Event|Normal|Patterned|Colored|Wisped|Wisp|No Wisp|"
        r"Halloween|Christmas|Santa|Lunar|Valentines?|Anniversary|Rainbow|Easter|"
        r"Bronze|Silver|Gold|Ruby|Emerald|Sapphire|Toy|Plush|Surfer|Tennis|Lifeguard|"
        r"Faberge|Faberage|Glass|Ornament|Star|Uncommon|Default|Wild caught|Wild|"
        r"First Edition|Idiosyncratic|Temper|Ray|wave|diamond|Wave|Diamond)\b",
        " ",
        raw,
        flags=re.I,
    )
    raw = re.sub(r"\([^)]*\)", " ", raw)
    raw = re.sub(r"[^A-Za-z0-9/\- ]+", " ", raw)
    parts = re.split(r"[/,]| - |–", raw)
    found = []
    for part in parts:
        tok = part.strip()
        if not tok:
            continue
        # hyphenated evo: Slugling-Gastroak
        bits = re.split(r"\s*-\s*", tok)
        for bit in bits:
            bit = bit.strip()
            if not bit:
                continue
            key = norm(bit)
            if key in known:
                found.append(known[key])
                continue
            if key in ALIASES:
                found.append(ALIASES[key])
                continue
            # last word often the species
            last = norm(bit.split()[-1]) if bit.split() else ""
            if last in known:
                found.append(known[last])
            elif last in ALIASES:
                found.append(ALIASES[last])
    # special: 4/5 Star Goppie
    if re.search(r"goppie", title, re.I) and "Goppie" not in found:
        found.append("Goppie")
    if re.search(r"\bmochi", title, re.I):
        for sp in ("Mochibi", "Mocho", "Totemochi"):
            if sp not in found:
                found.append(sp)
    if re.search(r"icigool", title, re.I) and "Icigool" not in found:
        found.append("Icigool")
    found = expand_family(list(dict.fromkeys(found)))
    eggish = {norm(n) for n in found} & {"kyeggo", "doreggo", "dreggodyne"}
    if eggish:
        found = [n for n in found if n not in {"Pyramind", "Pharoglyph"}]
    return found


def icigool_colors_from_title(title: str) -> list[str] | None:
    if "icigool" not in title.lower():
        return None
    t = title.lower()
    colors: list[str] = []
    if "2024" in t or "star,plaid" in t.replace(" ", "") or "star/plaid" in t:
        colors = ICIGOOL_COLORS["2024"]
    elif "2019" in t:
        colors = ICIGOOL_COLORS["2019"]
    elif "2020" in t:
        colors = ICIGOOL_COLORS["2020"]
    elif "2021" in t:
        colors = ICIGOOL_COLORS["2021"]
    elif "2022" in t:
        colors = ICIGOOL_COLORS["2022"]
    elif "2023" in t:
        colors = ICIGOOL_COLORS["2023"]
    elif "2025" in t:
        colors = ICIGOOL_COLORS["2025"]
    elif "light blue" in t or "wild" in t:
        colors = ICIGOOL_COLORS["lightblue"]
    # also parse parenthetical color lists
    m = re.search(r"\(([^)]+)\)", title)
    if m and not colors:
        bits = re.split(r"[/,]", m.group(1))
        mapped = []
        for b in bits:
            b = b.strip()
            if not b:
                continue
            if re.search(r"light\s*green", b, re.I):
                mapped.append("Green")
            elif re.search(r"light\s*blue", b, re.I):
                mapped.append("Base")
            elif re.search(r"crimson", b, re.I):
                mapped.append("Maroon")
            elif re.search(r"purple", b, re.I):
                mapped.append("Indigo")
            else:
                mapped.append(b.title())
        colors = mapped
    return colors or None


def parse_body(lines: list[str]) -> dict:
    demand = None
    demand_color = None
    ineffective = ""
    rows = []
    notes = []
    first_edition = None
    for raw in lines:
        line = raw.strip()
        if not line or SKIP_LINE.match(line):
            continue
        if line.startswith(":") and "type" in line and "=" not in line:
            continue
        dm = DEMAND_RE.search(line)
        if dm:
            demand, demand_color = DEMAND_EMOJI.get(dm.group(1), (None, None))[0], DEMAND_EMOJI.get(dm.group(1), (None, None))[1]
            if demand:
                continue
        im = INEFF_RE.search(line)
        if im:
            ineffective = im.group(1).strip()
            continue
        fe = FE_RE.search(line)
        if fe:
            first_edition = re.sub(r"\s+", " ", fe.group(0)).strip()
            continue
        if "=" in line and not line.lower().startswith("demand"):
            left, right = line.split("=", 1)
            left, right = left.strip(), right.strip()
            if left and right and len(left) < 80:
                # strip trailing demand emoji from value
                right = re.sub(r"[🟪🟣🟦🟩🟧🟠🟥🟫]+", "", right).strip()
                rows.append({"n": left, "v": right})
                continue
        if re.search(r":(sa~1|alpha1|gamma1|event|radiant):", line, re.I):
            continue
        if len(line) > 8:
            notes.append(line)
    return {
        "demand": demand,
        "demandColor": demand_color,
        "ineffective": ineffective,
        "rows": rows,
        "notes": notes[:6],
        "firstEdition": first_edition,
    }


def parse_file() -> list[dict]:
    text = VALUES_PATH.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    section = "Non-event"
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        for rx, name in SECTION_MAP:
            if rx.search(stripped) and len(stripped) < 40:
                section = name
                break
        if is_title(stripped):
            title = stripped
            body = []
            i += 1
            while i < len(lines) and not is_title(lines[i].strip()):
                nxt = lines[i].strip()
                if any(rx.search(nxt) and len(nxt) < 40 for rx, _ in SECTION_MAP):
                    break
                body.append(lines[i])
                i += 1
            entries.append({"title": title, "section": section, "body": parse_body(body)})
            continue
        i += 1
    return entries


def known_species(cards: list[dict]) -> dict[str, str]:
    known = dict(ALIASES)
    for c in cards:
        known[norm(c["species"])] = c["species"]
    return known


def card_reskin_aliases(reskin: str | None) -> set[str]:
    if not reskin:
        return {""}
    n = norm(reskin)
    out = {n}
    if n == "halloweensrainbow":
        out.add("halloween")
    if n == "halloween":
        out.add("halloweensrainbow")
    if n in {"holiday", "gingerbread", "elf", "festive", "snowman", "hotchocolate"}:
        out.update({"holiday", "christmas", "santa"})
    if n == "birthday":
        out.add("anniversary")
    if n == "valentines":
        out.add("valentine")
    if n == "lunarnewyear":
        out.add("lunar")
    if n == "tennistag":
        out.add("tennis")
    return out


def prefer_card(cands: list[dict], reskin_hint: str | None, title: str) -> dict | None:
    if not cands:
        return None
    if reskin_hint:
        hn = norm(reskin_hint)
        exact = [c for c in cands if norm(c.get("reskin")) == hn]
        if exact:
            cands = exact
        else:
            aliased = [c for c in cands if hn in card_reskin_aliases(c.get("reskin"))]
            if aliased:
                cands = aliased
    t = title.lower()
    if "halloween" in t:
        rain = [c for c in cands if c.get("reskin") == "Halloween Rainbow"]
        plain = [c for c in cands if c.get("reskin") == "Halloween"]
        if rain and not plain:
            cands = rain
        elif plain:
            cands = plain
    if "rainbow" in t and "halloween" not in t:
        rain = [c for c in cands if c.get("reskin") == "Rainbow"]
        if rain:
            cands = rain
    if "faberge" in t or "faberage" in t:
        fab = [c for c in cands if c.get("reskin") == "Faberge"]
        if fab:
            cands = fab
    if re.search(r"\d+\s*star|numbered|bob", t) or (re.search(r"radiant", t) and re.search(r"goppie", t)):
        num = [c for c in cands if c.get("reskin") == "Numbered"]
        if num:
            cands = num
    if "snowman" in t or ("christmas" in t and any(c["species"] == "Totemochi" for c in cands)):
        snow = [c for c in cands if c.get("reskin") == "Snowman"]
        if snow:
            cands = snow
    # prefer matching reskin over base species if title is an event
    if reskin_hint:
        skinned = [c for c in cands if c.get("reskin")]
        if skinned:
            cands = skinned
    else:
        base = [c for c in cands if not c.get("reskin")]
        if base and "halloween" not in t and "christmas" not in t and "lunar" not in t and "rainbow" not in t:
            cands = base
    return cands[0]


def attach_values(cards: list[dict]) -> dict:
    known = known_species(cards)
    entries = parse_file()
    by_id = {c["id"]: c for c in cards}
    for c in cards:
        c.setdefault("values", {})
        c.setdefault("category", "Non-event")
        c.setdefault("hasRadiant", False)
        c.setdefault("hasFirstEdition", False)
        c.setdefault("valueless", True)
        c.setdefault("defaultGleam", None)

    unmatched = []
    matched = 0
    for e in entries:
        title = e["title"]
        names = extract_names(title, known)
        gleam = parse_gleam(title)
        reskin = parse_reskin(title, e["section"])
        colors = icigool_colors_from_title(title)
        gcol = gem_color(title)
        pattern = pattern_from_title(title)
        if "faber" in title.lower():
            m = re.search(r"\(([^)]+)\)", title)
            if m:
                colors = [b.strip().title() for b in re.split(r"[/,]", m.group(1)) if b.strip()]
        body = e["body"]
        if not names:
            unmatched.append(title)
            continue
        blob = {
            "demand": body["demand"],
            "demandColor": body["demandColor"],
            "ineffective": body["ineffective"],
            "rows": body["rows"],
            "notes": body["notes"],
            "firstEdition": body["firstEdition"],
            "title": re.sub(r"\s+", " ", strip_tags(title)).strip(),
        }
        hit_any = False
        for sp in names:
            cands = [c for c in cards if c["species"] == sp]
            card = prefer_card(cands, reskin, title)
            if not card:
                continue
            hit_any = True
            key = gleam
            slot = card["values"].get(key) or {}
            targets = list(colors or [])
            if gcol:
                targets.append(gcol)
            if pattern:
                targets.append(pattern)
            if targets:
                by = dict(slot.get("byColor") or {})
                for col in targets:
                    by[col] = blob
                slot["byColor"] = by
                if "Base" in targets or not slot.get("rows"):
                    if not slot.get("rows"):
                        slot = {**blob, "byColor": by}
                card["values"][key] = slot
            else:
                existing = slot
                if existing.get("rows") and len(existing.get("rows") or []) >= len(blob["rows"]):
                    if blob["firstEdition"] and not existing.get("firstEdition"):
                        existing["firstEdition"] = blob["firstEdition"]
                else:
                    blob2 = dict(blob)
                    if existing.get("byColor"):
                        blob2["byColor"] = existing["byColor"]
                    card["values"][key] = blob2
            if e["section"] and e["section"] != "Non-event":
                if e["section"].split()[0].lower() in title.lower() or (reskin and card.get("reskin") and norm(reskin) == norm(card.get("reskin"))):
                    card["category"] = e["section"]
            elif reskin:
                card["category"] = reskin if reskin not in {"Holiday"} else "Christmas"
            if blob["firstEdition"] or (card["values"].get(key) or {}).get("firstEdition"):
                card["hasFirstEdition"] = True
            if key.startswith("radiant"):
                card["hasRadiant"] = True
        if hit_any:
            matched += 1
        else:
            unmatched.append(title)

    # Radiant availability by rule, even without a parsed radiant block
    for c in cards:
        if c["species"] in {"Goppie", "Arapaigo"} and c.get("reskin") == "Numbered":
            c["hasRadiant"] = True
            if not c.get("category") or c["category"] == "Non-event":
                c["category"] = "Bob's Pond"
        if c.get("reskin") == "Lunar New Year":
            c["hasRadiant"] = True
            c["category"] = "Lunar New Year"
        if c["species"] in {"Kyeggo", "Doreggo", "Dreggodyne"}:
            c["hasRadiant"] = True
            if c.get("reskin") == "Faberge" and c.get("category") == "Non-event":
                c["category"] = "Easter"
        # Christmas holiday cards
        if c.get("reskin") in {"Holiday", "Gingerbread", "Elf", "Festive", "Snowman", "Hot Chocolate"}:
            if c.get("category") in {None, "Non-event"}:
                c["category"] = "Christmas"
        if c.get("reskin") in {"Halloween", "Halloween Rainbow"}:
            if c.get("category") in {None, "Non-event"}:
                c["category"] = "Halloween"
        if c.get("reskin") == "Rainbow":
            if c.get("category") in {None, "Non-event"}:
                c["category"] = "Rainbow"
        if c.get("reskin") == "Valentine's":
            c["category"] = "Valentine's"
        if c.get("reskin") == "Birthday":
            c["category"] = "Anniversary"
        if not c.get("reskin"):
            if c["species"] == "Icigool":
                c["category"] = "Icigool"
            else:
                c["category"] = "Non-event"

        vals = c.get("values") or {}
        def valued(b):
            if not b:
                return False
            if b.get("rows") or b.get("demand"):
                return True
            return any(valued(x) for x in (b.get("byColor") or {}).values())
        has_sa = valued(vals.get("sa"))
        has_al = valued(vals.get("alpha"))
        has_ga = valued(vals.get("gamma"))
        has_ev = valued(vals.get("event"))
        has_rad = valued(vals.get("radiant"))
        c["valueless"] = not (has_sa or has_al or has_ga or has_ev or has_rad)
        if not has_sa and not has_al and has_ga:
            c["defaultGleam"] = "gamma"
        elif has_ev and not has_sa and not has_al and not has_ga:
            c["defaultGleam"] = "event"
        # Copy radiantAlpha/Gamma into radiant extras
        rad = vals.get("radiant") or {}
        extras = {}
        if vals.get("radiantAlpha"):
            extras["alpha"] = vals["radiantAlpha"]
        if vals.get("radiantGamma"):
            extras["gamma"] = vals["radiantGamma"]
        if extras:
            if not rad:
                rad = extras.get("gamma") or extras.get("alpha") or {}
            rad = dict(rad)
            rad["extras"] = extras
            c["values"]["radiant"] = rad

    return {
        "matched": matched,
        "unmatched": unmatched,
        "entries": len(entries),
        "valued": sum(1 for c in cards if not c["valueless"]),
        "valueless": sum(1 for c in cards if c["valueless"]),
        "radiant": sum(1 for c in cards if c.get("hasRadiant")),
        "fe": sum(1 for c in cards if c.get("hasFirstEdition")),
    }
