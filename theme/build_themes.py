#!/usr/bin/env python3
"""
Build the Arcane themes and chart palettes, and optionally deploy + activate them.

    python3 theme/build_themes.py               # write JSON files only
    python3 theme/build_themes.py --deploy      # also create/update in the org and activate per workspace

Themes (one per workspace):
- arcane              -> parent "Arcane" (Arcane brand: teal #004C52, coral #FF6555, mint #8FC9A9, Zalando Sans, logo)
- arcane_<client_id>  -> each client workspace in the advertiser's own (fictional) brand, co-branded "x Arcane"
                         = the white-label set-up (same as the Primelis roll-out)
Structure comes from _template_theme.json, recoloured by role. GoodData limits a theme to 15,000 characters.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOST = os.environ.get("GD_HOST", "https://sandrasuszterova.demo.cloud.gooddata.com")
PARENT_WS = "4d4926ef508e4cba9085ca29fefcf4fd"
FONT = "https://fonts.gstatic.com/s/zalandosans/v3/FwZJ7-Asy1Em_lq_aK3hpr-RrktWHD54lnesO2lsfPbPd_ajf_E.woff2"
ARC_LOGO = "https://www.arcane.run/wp-content/themes/arcane/dist/images/logo-animated.c23bffada0219d8bbafa.webp"
# data products -> one cover image per product in every theme ({theme.assets.images.dp_<product>}), in the theme's
# own colours, so publisher reports render in the brand of the workspace that opens them
DATA_PRODUCTS = json.load(open(HERE.parent / "gooddata" / "data_products.json"))["products"]


ARC_IMG = "https://www.arcane.run/wp-content/uploads/2026/"
PRODUCT_ART = {   # Arcane's own brand visuals (arcane.run) per data product - same art in every theme
    "dp_paid_media_performance": ARC_IMG + "07/home_hero_visual.webp",
    "dp_social_creatives": ARC_IMG + "07/Tile-slider-29.webp",
    "dp_web_analytics_and_geo": ARC_IMG + "07/Group-427320730-2.webp",
    "dp_budget_and_pacing": ARC_IMG + "07/Group-427320640.webp",
    "dp_product_feed_and_shopping": ARC_IMG + "07/Group-427320637.webp",
    "dp_crm_and_offline_sales": ARC_IMG + "07/Tile-slider-26.webp",
    "dp_measurement_and_incrementality": ARC_IMG + "07/Group-427320639.webp",
    "dp_arcane_operations": ARC_IMG + "07/Group-427320638.webp",
}


def product_images(cfg):
    assert set(PRODUCT_ART) == {x["user_group"] for x in DATA_PRODUCTS.values()}
    return PRODUCT_ART


TEMPLATE_HEX = {  # role -> colour used in the template
    "page": "#0B0D10", "card": "#14171C", "panel": "#1B1F25", "line": "#252A31", "line2": "#343A43",
    "g5": "#4E5560", "g6": "#747C88", "muted": "#9BA3AE", "g8": "#C9CED6", "text": "#F2F4F7",
    "subtle": "#5B636E", "accent": "#D4F24A", "accent_hover": "#C3E635", "accent_dim": "#2A3312",
}


def solid(hex_):
    h = hex_.lstrip("#")
    return f"https://placehold.co/1920x1080/{h}/{h}/png"


def wordmark(name, fg, bg="FFFFFF"):
    return f"https://placehold.co/600x140/{bg}/{fg.lstrip('#')}/png?text={name.replace(' ', '+')}&font=montserrat"


def light(primary, deep, accent, ink, tint, line, viz, header, logo, header_logo=None, bg=None, kpi=None):
    """Light brand theme config: primary (buttons), deep (nav, KPI tiles), accent (highlights)."""
    return {
        "header": header, "primary": primary, "logo": logo, "header_logo": header_logo or logo,
        "bg": bg or solid(deep), "rule": accent.lstrip("#"), "viz": viz,
        "hex": {"page": "#FFFFFF", "card": tint, "panel": tint, "line": line, "line2": line,
                "g5": "#9A98A8", "g6": "#6E6C80", "muted": "#4F4D63", "g8": deep, "text": ink,
                "subtle": "#7E7C90", "accent": primary, "accent_hover": deep, "accent_dim": accent},
        "nav": {"bg": deep, "border": deep, "item": "#E4DDF0" if deep == "#591490" else "#E6E9EE",
                "selected": deep, "selected_bg": accent},
        "kpi_tile": kpi or {"bg": deep, "border": deep, "title": "#E9E3F3", "value": "#FFFFFF",
                            "secondary": "#E9E3F3", "good": "#8FE3C0", "bad": "#FFB3BF"},
        "doc": {"page": tint, "card": "#FFFFFF", "panel": tint},
    }


TEAL, CORAL, MINT = "#004C52", "#FF6555", "#8FC9A9"
THEMES = {
    "arcane": dict(name="Arcane", ws=PARENT_WS, brand="Arcane", **light(
        primary=CORAL, deep=TEAL, accent=MINT, ink="#0E2A2D", tint="#F3F7F7", line="#D9E4E4",
        viz=[TEAL, CORAL, MINT, "#2E8C93", "#F4A259", "#5B6C70", "#A3D9D2", "#B23A48", "#C6CACC", "#FFD6A5"],
        header=("#FFFFFF", TEAL, CORAL), logo=ARC_LOGO,
        kpi={"bg": TEAL, "border": TEAL, "title": "#CFE6E3", "value": "#FFFFFF", "secondary": "#CFE6E3",
             "good": MINT, "bad": "#FFB3AA"})),
    "arcane_secondevie": dict(name="Seconde Vie", ws="secondevie", brand="Seconde Vie", **light(
        primary="#22A06B", deep="#0F3D2E", accent="#F2C14E", ink="#0B2219", tint="#F2F8F5", line="#D6E8DF",
        viz=["#0F3D2E", "#22A06B", "#F2C14E", "#5BB98C", "#9AD3B5", "#E07A5F", "#3D5A80", "#B5C99A", "#F7DE9C",
             "#6C7A72"],
        header=("#0F3D2E", "#FFFFFF", "#F2C14E"), logo=wordmark("Seconde Vie x Arcane", "#0F3D2E"),
        header_logo=wordmark("Seconde Vie x Arcane", "#FFFFFF", "0F3D2E"))),
    "arcane_autonova": dict(name="AutoNova Automobiles", ws="autonova", brand="AutoNova", **light(
        primary="#1E5AA8", deep="#0B2545", accent="#E63946", ink="#0B1A2E", tint="#F3F6FA", line="#DCE3EE",
        viz=["#0B2545", "#1E5AA8", "#E63946", "#8DA9C4", "#F4A261", "#5C677D", "#13315C", "#B8C5D6", "#F1C6C9",
             "#2A9D8F"],
        header=("#0B2545", "#FFFFFF", "#E63946"), logo=wordmark("AutoNova x Arcane", "#0B2545"),
        header_logo=wordmark("AutoNova x Arcane", "#FFFFFF", "0B2545"))),
    "arcane_routeo": dict(name="Routéo Location", ws="routeo", brand="Routéo", **light(
        primary="#F28C28", deep="#23395B", accent="#F6D55C", ink="#16233A", tint="#FBF7F2", line="#ECE2D6",
        viz=["#23395B", "#F28C28", "#F6D55C", "#5D8BB5", "#E9B872", "#3F7D6E", "#A3B4C8", "#C2573A", "#FBE7B5",
             "#6B7280"],
        header=("#FFFFFF", "#23395B", "#F28C28"), logo=wordmark("Routeo x Arcane", "#23395B"))),
}


def doc_colors(h):
    return {"backgrounds": [{"id": "page", "color": h["page"]}, {"id": "card", "color": h["card"]},
                            {"id": "panel", "color": h["panel"]}, {"id": "accent", "color": h["accent"]}],
            "texts": [{"id": "default", "color": h["text"]}, {"id": "muted", "color": h["muted"]},
                      {"id": "subtle", "color": h["subtle"]}, {"id": "accent", "color": h["accent"]},
                      {"id": "inverse", "color": "#FFFFFF"}]}


def recolor(obj, mapping):
    s = json.dumps(obj)
    for old, new in mapping.items():
        s = s.replace(old, new).replace(old.lower(), new)
    return json.loads(s)


def build_theme(cfg):
    base = json.load(open(HERE / "_template_theme.json"))
    hexes, nav = cfg["hex"], cfg["nav"]
    t = recolor({k: v for k, v in base.items() if k not in ("assets", "images")},
                {TEMPLATE_HEX[k]: hexes[k] for k in TEMPLATE_HEX})
    t = json.loads(json.dumps(t).replace('"Inter"', '"Zalando Sans"').replace("Inter,", "Zalando Sans,"))
    t["typography"] = {"font": FONT, "fontBold": FONT}
    good, bad = "#2F9E7A", "#D1435B"
    t["palette"]["primary"] = {"base": cfg["primary"], "contrast": "#FFFFFF"}
    t["palette"]["error"]["base"], t["palette"]["success"]["base"] = bad, good
    t["kpi"]["value"] = {"positiveColor": good, "negativeColor": bad}
    t["modal"]["outsideBackgroundColor"] = "rgba(0, 0, 0, 0.45)"
    t["dashboards"]["navigation"] = {"title": {"color": "#FFFFFF"}, "backgroundColor": nav["bg"],
                                     "borderColor": nav["border"],
                                     "item": {"color": nav["item"], "hoverColor": "#FFFFFF",
                                              "selectedColor": nav["selected"],
                                              "selectedBackgroundColor": nav["selected_bg"]}}
    for w in ("widget", "kpiWidget"):
        t["dashboards"]["content"][w].update(backgroundColor="#FFFFFF", borderColor=hexes["line"])
    t["dashboards"]["content"]["backgroundColor"] = hexes["card"]
    t["dashboards"]["filterBar"]["backgroundColor"] = "#FFFFFF"
    t["chart"]["backgroundColor"] = "#FFFFFF"
    t["tooltip"] = {"color": "#FFFFFF", "backgroundColor": hexes["text"]}
    t["chart"].update(tooltipBackgroundColor=hexes["text"], tooltipBorderColor=hexes["text"],
                      tooltipLabelColor=hexes["line2"], tooltipValueColor="#FFFFFF")
    k = cfg["kpi_tile"]
    tile = t["dashboards"]["content"]["kpiWidget"]
    tile.update(backgroundColor=k["bg"], borderColor=k["border"])
    tile["title"]["color"] = k["title"]
    tile["kpi"] = {"primaryMeasureColor": k["value"], "secondaryInfoColor": k["secondary"],
                   "value": {"positiveColor": k["good"], "negativeColor": k["bad"]}}
    doc_hex = {**hexes, **cfg["doc"]}
    t["documents"]["colors"] = doc_colors(doc_hex)
    t["documents"]["page"] = {"backgroundColor": doc_hex["page"]}
    t["documents"]["visualizationPalette"] = cfg["viz"]
    img = lambda i, u, ti: {"id": i, "url": u, "title": ti, "altText": ti}
    logo = img("logo", cfg["logo"], f"{cfg['brand']} logo")
    bgs = [img("cover_bg", cfg["bg"], "Cover background"), img("section_bg", cfg["bg"], "Section background")]
    rule = img("accent_bar", f"https://placehold.co/1600x12/{cfg['rule']}/{cfg['rule']}/png", "Accent rule")
    spacer = next(a for a in base["assets"]["images"] if a["id"] == "spacer")  # inline transparent 1x1 PNG
    products = [img(pid, url, pid.replace("dp_", "").replace("_", " ").title())
                for pid, url in product_images(cfg).items()]
    t["assets"] = {"logos": [logo], "backgrounds": bgs, "images": bgs + [rule, logo, spacer] + products}
    t["images"] = {"logo": f"url({cfg['header_logo']})"}
    h = cfg["header"]
    t["header"] = {"backgroundColor": h[0], "color": h[1], "activeColor": h[2]}
    return t


def palette(viz):
    h = lambda x: {"r": int(x[1:3], 16), "g": int(x[3:5], 16), "b": int(x[5:7], 16)}
    return {"colorPalette": [{"guid": f"{i + 1:02d}", "fill": h(c)} for i, c in enumerate(viz)]}


def api(method, path, body=None):
    req = urllib.request.Request(HOST + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {os.environ['GOODDATA_API_TOKEN']}",
                                          "Content-Type": "application/vnd.gooddata.api+json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def upsert(kind, oid, name, content):
    body = {"data": {"id": oid, "type": kind[:-1], "attributes": {"name": name, "content": content}}}
    code, resp = api("PUT", f"/api/v1/entities/{kind}/{oid}", body)
    if code == 404:
        code, resp = api("POST", f"/api/v1/entities/{kind}", body)
    if code not in (200, 201):
        sys.exit(f"{kind}/{oid}: {code} {resp}")
    return code


def activate(ws, setting_type, ref):
    code, res = api("GET", f"/api/v1/entities/workspaces/{ws}/workspaceSettings?origin=NATIVE")
    existing = next((s for s in res["data"] if s["attributes"]["type"] == setting_type), None) if code == 200 else None
    sid = existing["id"] if existing else f"{setting_type.lower()}_arcane"
    body = {"data": {"id": sid, "type": "workspaceSetting", "attributes": {"type": setting_type, "content": ref}}}
    if existing:
        return api("PUT", f"/api/v1/entities/workspaces/{ws}/workspaceSettings/{sid}", body)[0]
    return api("POST", f"/api/v1/entities/workspaces/{ws}/workspaceSettings", body)[0]


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for tid, cfg in THEMES.items():
        if only and tid not in only:
            continue
        theme = build_theme(cfg)
        size = len(json.dumps(theme))
        assert size < 15000, f"{tid} is {size} chars (limit 15000)"
        (HERE / f"{tid}_theme.json").write_text(json.dumps(theme, indent=2) + "\n")
        (HERE / f"{tid}_palette.json").write_text(json.dumps(palette(cfg["viz"]), indent=2) + "\n")
        print(f"wrote {tid}_theme.json ({size} chars)")
        if "--deploy" in sys.argv:
            print("  theme", upsert("themes", tid, f"Arcane – {cfg['name']}", theme),
                  "| palette", upsert("colorPalettes", tid, f"Arcane – {cfg['name']}", palette(cfg["viz"])),
                  "| ACTIVE_THEME", activate(cfg["ws"], "ACTIVE_THEME", {"id": tid, "type": "theme"}),
                  "| ACTIVE_COLOR_PALETTE", activate(cfg["ws"], "ACTIVE_COLOR_PALETTE",
                                                     {"id": tid, "type": "colorPalette"}),
                  f"-> {cfg['ws']}")


if __name__ == "__main__":
    main()
