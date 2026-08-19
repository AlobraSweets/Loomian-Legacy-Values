"""Parse SkeleNumber sprite wiki dump into a grouped Loomian value-dex database."""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

WIKI = Path(
    r"C:\Users\maxxo\.cursor\projects\C-Users-maxxo-AppData-Local-Temp-8262e711-32f2-4126-9a5c-e26b4cc7a425\agent-tools\sprites.wiki.txt"
)
META = Path(
    r"C:\Users\maxxo\.cursor\projects\C-Users-maxxo-AppData-Local-Temp-8262e711-32f2-4126-9a5c-e26b4cc7a425\agent-tools\loomians_meta.json"
)
OUT = Path(r"C:\Users\maxxo\loomian-value-dex\data.js")

SOULBURST_PREFIXES = (
    "Flychomp",
    "Terraform",
    "Magmadire",
    "Lavafiend",
    "Incarnate",
    "Jetwing",
    "Seascourge",
    "Thunderking",
    "Atomic",
    "Tempereign",
    "Overcharged",
    "Willbound",
    "Stellarchime",
    "Frostshackled",
    "Archfiend",
)

GEMSTONES = ("Bronze", "Silver", "Gold", "Emerald", "Ruby", "Sapphire")
RAINBOW_COLORS = {"Red", "Orange", "Yellow", "Green", "Blue", "Violet", "Purple", "Rainbow"}
EGG_PATTERN_SPECIES = {"Kyeggo", "Doreggo", "Dreggodyne"}
EGG_PATTERNS = {
    "Frilly",
    "Zigzag",
    "Striped",
    "Star",
    "RedFaberge",
    "GreenFaberge",
    "BlueFaberge",
    "Arches",
    "TriangleStriped",
    "Runic",
    "Gold",
    "OrangeFaberge",
    "VioletFaberge",
    "TealFaberge",
    "Diamond",
    "Watermelon",
    "Wavy",
    "Pyramind",
    "CyanFaberge",
    "MagentaFaberge",
    "YellowFaberge",
    "2024",
    "2025",
}
ICIGOOL_NATIVE = {
    "yellow",
    "green",
    "red",
    "indigo",
    "pink",
    "black",
    "white",
    "navy",
    "darkgreen",
    "maroon",
    "brown",
    "orange",
    "PolkaDot",
    "yellowpattern",
    "Zigzag",
    "Checkered",
    "Snowflake",
    "Pixel",
    "Floral",
    "maroonpattern",
    "Star",
    "Circuit",
    "Plaid",
    "Honeycomb",
}
MOCHIBI_LINE = {"Mochibi", "Mocho", "Totemochi"}
MOCHIBI_NATIVE = {"Green", "Yellow", "Cyan", "White", "Red", "Lime", "Magenta", "Purple"}
GARGOLM_FORMS = {"Attack", "Defense", "Speed"}
COSMELEON_WEATHER = {"Rain", "Wind", "Fog", "Heat", "Thunderstorm"}
VARI_FORMS = {
    "Cervolen",
    "Wendolen",
    "Kirolen",
    "Zepholen",
    "Venolen",
    "Wresolen",
    "Buzzolen",
    "Tundrolen",
    "Pyrolen",
    "Hydrolen",
}
SWIRELLE_FLAVORS = {"Raspberry", "Blueberry", "Lemon"}
RANK_SET = {"Hyper", "Expert", "Ace"}
NUMBER_RE = re.compile(r"^\d+-\d+$")
HALLOWEEN_COLOR_WORDS = (
    "Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Violet",
    "Cyan", "Pink", "White", "Black", "Lime",
)

RESKIN_LABELS = {
    "Gemstone": "Gemstone",
    "Rainbow": "Rainbow",
    "HalloweenRainbow": "Halloween Rainbow",
    "Toy": "Toy",
    "Ornament": "Ornament",
    "Numbered": "Numbered",
    "Holiday": "Holiday",
    "Halloween": "Halloween",
    "Valentine": "Valentine's",
    "LunarNewYear": "Lunar New Year",
    "Ranked": "Ranked",
    "Hat": "Hat",
}

PRETTY = {
    "LunarNewYear": "Lunar New Year",
    "HotChocolate": "Hot Chocolate",
    "Holiday-Fruitcake": "Fruitcake",
    "TennisTag": "Tennis Tag",
    "SpiritGuide": "Spirit Guide",
    "Jack-O'-Lantern": "Jack-O'-Lantern",
    "BurningYule": "Burning Yule",
    "RainbowFaberge": "Rainbow Faberge",
    "darkgreen": "Dark Green",
    "maroonpattern": "Maroon Pattern",
    "yellowpattern": "Yellow Pattern",
    "PolkaDot": "Polka Dot",
    "RedColored": "Red Colored",
    "OrangeColored": "Orange Colored",
    "YellowColored": "Yellow Colored",
    "GreenColored": "Green Colored",
    "BlueColored": "Blue Colored",
    "VioletColored": "Violet Colored",
}


def pretty(code: str) -> str:
    if code in PRETTY:
        return PRETTY[code]
    if code in RESKIN_LABELS:
        return RESKIN_LABELS[code]
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", code)
    s = s.replace("-", " ")
    s = s.strip()
    if s.lower() == s:
        s = s.title()
    return s


def wiki_url(filename: str) -> str:
    fn = filename.replace(" ", "_")
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    from urllib.parse import quote

    return (
        f"https://static.wikia.nocookie.net/loomian-legacy/images/{h[0]}/{h[:2]}/"
        f"{quote(fn, safe='-_.')}/revision/latest"
    )


def sprite_filename(species: str, code: str) -> str:
    if code in ("Base", ""):
        return f"{species}-menu.png"
    return f"{species}-{code}-menu.png"


def is_old(code: str, name: str) -> bool:
    n = (name or "").lower()
    if "prior to" in n:
        return True
    if re.search(r"\bv0\.\d", n):
        return True
    if code.startswith("Old") or code.startswith("Old-"):
        return True
    if "-Old" in code:
        return True
    return False


def is_soulburst_family(family: str) -> bool:
    for p in SOULBURST_PREFIXES:
        if family == p or family.startswith(p + "-") or family.startswith(p):
            return True
    return False


def parse_gleam(code: str, name: str) -> tuple[str, str]:
    """Return (family_code, gleam) where gleam is normal|alpha|gamma."""
    gleam = "normal"
    c = code
    nm = name or ""
    if c.endswith("-Gamma"):
        gleam = "gamma"
        c = c[: -len("-Gamma")]
    elif c.endswith("-Alpha"):
        gleam = "alpha"
        c = c[: -len("-Alpha")]
    elif c == "Gamma":
        return "Base", "gamma"
    elif c == "Alpha":
        return "Base", "alpha"
    elif c == "Base":
        return "Base", "normal"
    # Wiki sometimes labels Alpha in the name while reusing the non-alpha code
    if gleam == "normal":
        low = nm.lower()
        if low.endswith(" gamma") or " gamma (" in low:
            gleam = "gamma"
        elif low.endswith(" alpha") or " alpha (" in low:
            gleam = "alpha"
    return c, gleam


def parse_wiki(text: str) -> dict[str, list[tuple[str, str]]]:
    blocks = re.findall(r"\{\{User:SkeleNumber/Sprite List\|([^}]+)\}\}", text)
    by: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for b in blocks:
        params = {}
        for part in b.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()
        loom = params.get("Loomian")
        if not loom:
            continue
        for i in range(1, 7):
            e = params.get(f"e{i}")
            n = params.get(f"e{i}Name")
            if e:
                by[loom].append((e, n or e))
    return by


def species_has_gemstones(items: list[tuple[str, str]]) -> bool:
    fams = set()
    for e, n in items:
        if is_old(e, n):
            continue
        fam, _ = parse_gleam(e, n)
        fams.add(fam)
    return sum(1 for g in GEMSTONES if g in fams) >= 4


def novadeaus_keep(family: str) -> bool:
    allowed = {
        "Base",
        "Alpha-Glacadia-Alpha-Arceros",
        "Gamma-Glacadia-Gamma-Arceros",
        "Rainbow-Glacadia-Rainbow-Arceros",
    }
    return family in allowed


def classify(species: str, family: str, gleam: str, has_gemstones: bool, name: str = "") -> tuple[str, str]:
    """Return (profile_kind, variant_name). profile_kind is 'Normal' or a reskin key."""
    if species == "Novadeaus":
        if family == "Base":
            return "Normal", "Standard"
        if family == "Alpha-Glacadia-Alpha-Arceros":
            return "Normal", "Standard"
        if family == "Gamma-Glacadia-Gamma-Arceros":
            return "Normal", "Standard"
        if family == "Rainbow-Glacadia-Rainbow-Arceros":
            return "Rainbow", "Matching"
        return None, None  # type: ignore

    if species == "Cosmiore":
        if family.startswith("Encased"):
            rest = family[len("Encased") :].lstrip("-") or "Base"
            return "Normal", pretty(rest)
        return None, None  # type: ignore

    if family in ("Base", "F"):
        if family == "F":
            return "Normal", "Female"
        m = re.search(r"\(([^)]+)\)", name or "")
        if m and not re.search(r"v0\.\d|prior to", m.group(1), re.I):
            return "Normal", m.group(1)
        if species == "Swirelle":
            return "Normal", "Strawberry"
        return "Normal", "Base"

    if family in GARGOLM_FORMS and species == "Gargolem":
        return "Normal", family

    if family.endswith("-Holiday") or family in {
        "Base-Holiday",
        "Attack-Holiday",
        "Defense-Holiday",
        "Speed-Holiday",
    }:
        form = family.replace("-Holiday", "").replace("Base", "Base")
        if form == "Base-Holiday" or family == "Base-Holiday":
            form = "Base"
        else:
            form = family.replace("-Holiday", "")
        return "Holiday", form

    if family.startswith("F-"):
        rest = family[2:]
        kind, variant = classify(species, rest, gleam, has_gemstones, name)
        if kind is None:
            return None, None  # type: ignore
        return kind, ("Female " + variant).strip()

    if family.startswith("Halloween-") and family != "Halloween":
        color = family.split("-", 1)[1]
        return "HalloweenRainbow", pretty(color)

    if family.startswith("Toy-"):
        return "Toy", pretty(family.split("-", 1)[1])

    if family.startswith("Ornament"):
        rest = family.replace("Ornament-", "").replace("Ornament", "1")
        return "Ornament", pretty(rest) if rest else "1"

    if family.endswith("-Hat") or family in {"Hat", "Red-Hat", "Orange-Hat", "Yellow-Hat", "Green-Hat", "Blue-Hat", "Violet-Hat", "Rainbow-Hat"}:
        if family == "Hat":
            return "Hat", "Base"
        color = family.replace("-Hat", "")
        return "Hat", pretty(color)

    if family == "Holiday-Fruitcake":
        return "Holiday", "Fruitcake"

    if NUMBER_RE.match(family):
        if gleam != "alpha":
            return None, None  # type: ignore
        return "Numbered", family

    if family in RANK_SET:
        return "Ranked", family

    if species in EGG_PATTERN_SPECIES and family in EGG_PATTERNS:
        return "Normal", pretty(family)

    if species == "Icigool" and family in ICIGOOL_NATIVE:
        return "Normal", pretty(family)

    if species in MOCHIBI_LINE and family in MOCHIBI_NATIVE:
        return "Normal", pretty(family)

    if species == "Cosmeleon" and family in COSMELEON_WEATHER:
        return "Normal", family

    if species == "Vari" and family in VARI_FORMS:
        return "Normal", family

    if species == "Swirelle" and family in SWIRELLE_FLAVORS:
        return "Normal", family

    if has_gemstones and family in GEMSTONES:
        return "Gemstone", family

    if family in RAINBOW_COLORS:
        native_rainbow = (species == "Icigool") or (species in MOCHIBI_LINE and family in MOCHIBI_NATIVE)
        if native_rainbow:
            return "Normal", pretty(family)
        return "Rainbow", pretty(family)

    if family == "RainbowFaberge":
        return "Rainbow", "Rainbow Faberge"

    # Generic event reskin
    return family, "Base"


def load_meta() -> dict:
    meta = {}
    if META.exists():
        for row in json.loads(META.read_text(encoding="utf-8")):
            name = row["name"].split(" (")[0]
            secret = any(a.get("secret") for a in row.get("abilities") or [])
            types = row.get("types") or []
            if name not in meta:
                meta[name] = {"types": types, "hasSA": secret, "secretName": next((a["name"] for a in row.get("abilities") or [] if a.get("secret")), None)}
            else:
                meta[name]["hasSA"] = meta[name]["hasSA"] or secret
    return meta


def build():
    text = WIKI.read_text(encoding="utf-8")
    by = parse_wiki(text)
    meta = load_meta()
    profiles: dict[tuple[str, str], dict] = {}

    skipped_old = skipped_sb = skipped_other = 0

    for species, items in by.items():
        has_gems = species_has_gemstones(items)
        for code, name in items:
            if is_old(code, name):
                skipped_old += 1
                continue
            family, gleam = parse_gleam(code, name)
            if family == "Halloween":
                for c in HALLOWEEN_COLOR_WORDS:
                    if re.search(rf"\b{c}\b", name or "", re.I):
                        family = f"Halloween-{c}"
                        break
            if species == "Novadeaus" and not novadeaus_keep(family if family != "Base" else "Base"):
                # parse_gleam won't rewrite novadeaus mixed codes
                if family not in {
                    "Base",
                    "Alpha-Glacadia-Alpha-Arceros",
                    "Gamma-Glacadia-Gamma-Arceros",
                    "Rainbow-Glacadia-Rainbow-Arceros",
                }:
                    skipped_other += 1
                    continue
            if is_soulburst_family(family):
                skipped_sb += 1
                continue
            kind, variant = classify(species, family, gleam, has_gems, name)
            if kind is None:
                skipped_other += 1
                continue

            key = (species, kind)
            if key not in profiles:
                m = meta.get(species, {})
                profiles[key] = {
                    "id": f"{species}__{kind}",
                    "species": species,
                    "reskin": None if kind == "Normal" else RESKIN_LABELS.get(kind, pretty(kind)),
                    "displayName": species if kind == "Normal" else f"{species} ({RESKIN_LABELS.get(kind, pretty(kind))})",
                    "types": m.get("types") or [],
                    "hasSA": bool(m.get("hasSA")),
                    "secretAbility": m.get("secretName"),
                    "category": "normal" if kind == "Normal" else "reskin",
                    "variants": {},
                }
            vkey = variant or "Base"
            var = profiles[key]["variants"].setdefault(
                vkey,
                {
                    "id": vkey,
                    "name": vkey,
                    "sprites": {"normal": None, "alpha": None, "gamma": None},
                    "files": {"normal": None, "alpha": None, "gamma": None},
                    "codes": {"normal": None, "alpha": None, "gamma": None},
                },
            )
            # Novadeaus mapping: mixed codes onto gleam slots of Standard
            if species == "Novadeaus" and kind == "Normal":
                if family == "Alpha-Glacadia-Alpha-Arceros":
                    gleam = "alpha"
                elif family == "Gamma-Glacadia-Gamma-Arceros":
                    gleam = "gamma"
            slot = gleam if gleam in ("normal", "alpha", "gamma") else "normal"
            var["sprites"][slot] = wiki_url(sprite_filename(species, code))
            var["files"][slot] = sprite_filename(species, code)
            var["codes"][slot] = code

    dex = []
    for (species, kind), prof in profiles.items():
        variants = []
        for v in prof["variants"].values():
            has = {
                "normal": bool(v["sprites"]["normal"]),
                "alpha": bool(v["sprites"]["alpha"]),
                "gamma": bool(v["sprites"]["gamma"]),
            }
            # If a variant only has gleam sprites, still allow viewing that gleam.
            # If it has no "normal" sprite but has alpha/gamma, that's OK.
            if kind == "Normal" and v["name"] == "Base" and not has["normal"]:
                # Cosmiore has no generic Base — first encased color is fine
                pass
            v["has"] = has
            v["hasRainbowWisp"] = has["gamma"]
            variants.append(v)
        # Sort variants: Base first, then alpha-numeric
        def vsort(v):
            name = v["name"]
            if name in ("Base", "Standard"):
                return (0, name)
            if name == "Female":
                return (1, name)
            return (2, name)

        variants.sort(key=vsort)
        # Drop empty variants
        variants = [v for v in variants if any(v["sprites"].values())]
        if not variants:
            continue
        prof["variants"] = variants
        # Profile-level availability: union, used for filters; buttons use the selected variant
        prof["hasAlpha"] = any(v["has"]["alpha"] for v in variants)
        prof["hasGamma"] = any(v["has"]["gamma"] for v in variants)
        prof["hasRainbowWisp"] = any(v["hasRainbowWisp"] for v in variants)
        dex.append(prof)

    dex.sort(key=lambda p: (p["species"].lower(), 0 if p["category"] == "normal" else 1, p["displayName"].lower()))

    # Stats
    n_species = len({p["species"] for p in dex})
    n_reskin = sum(1 for p in dex if p["category"] == "reskin")
    n_normal = sum(1 for p in dex if p["category"] == "normal")

    payload = {
        "version": "1.0",
        "source": "SkeleNumber Loomian Menu Sprites (wiki, through v0.4.36)",
        "note": "Trade values are empty placeholders. Fill VALUES in this file or import a data document later.",
        "natures": (
            ["Indifferent"]
            + ["Hyper", "Brawny", "Robust", "Smart", "Clever", "Nimble"]
            + ["Dull", "Frail", "Tender", "Clumsy", "Foolish", "Sluggish"]
            + ["Very Hyper", "Very Brawny", "Very Robust", "Very Smart", "Very Clever", "Very Nimble"]
            + ["Very Dull", "Very Frail", "Very Tender", "Very Clumsy", "Very Foolish", "Very Sluggish"]
        ),
        "gleamTypes": [
            {"id": "normal", "label": "Normal", "hint": "Regular ability, no gleam"},
            {"id": "sa", "label": "SA", "hint": "Secret Ability"},
            {"id": "alpha", "label": "Alpha", "hint": "Alpha Gleam · 1/4096 base (often 1/128 with boosts)"},
            {"id": "gamma", "label": "Gamma", "hint": "Gamma Gleam · 1/20480 base (often 1/640 with boosts)"},
            {"id": "rainbowWisp", "label": "Rainbow Wisp", "hint": "Gamma with rainbow wisp · extra 1/125"},
        ],
        "loomians": dex,
        "values": {},
    }

    js = (
        "/* Generated by build_data.py — do not hand-edit loomians[]; put trade values in VALUES. */\n"
        "window.DEX = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n"
        "window.VALUES = window.DEX.values;\n"
    )
    OUT.write_text(js, encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Profiles: {len(dex)}  (normal {n_normal}, reskins {n_reskin})  species {n_species}")
    print(f"Skipped old={skipped_old} soulburst={skipped_sb} other={skipped_other}")
    # Sample specials
    for s in ("Eleguana", "Ventacean", "Goppie", "Icigool", "Cosmiore", "Novadeaus", "Akhalos", "Kyeggo", "Twittle", "Dakuda", "Scorb", "Cynamoth", "Gargolem", "Mochibi"):
        rows = [p for p in dex if p["species"] == s]
        print(f"\n{s}:")
        for p in rows:
            vars_ = ", ".join(f"{v['name']}[{''.join(k[0].upper() for k,ok in v['has'].items() if ok)}]" for v in p["variants"])
            print(f"  {p['displayName']:40s}  {len(p['variants'])} vars  {vars_[:160]}")


if __name__ == "__main__":
    build()
