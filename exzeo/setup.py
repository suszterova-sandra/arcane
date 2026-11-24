#!/usr/bin/env python3
"""
Exzeo demo on the Ecommerce Platform workspace (e74a1eaa...): white-label, multi-tenant, per-carrier isolation.

    set -a; . ../.env; set +a
    python3 exzeo/setup.py

What it does (idempotent):
1. Carrier workspaces = 3 of Exzeo's real carriers (exzeo.com): Homeowners Choice, TypTap, CORE (the 3 original
   children, renamed). Data isolation: WDF wdf__client_id + WDF wdf__product_category.
2. Themes: "Exzeo" on the parent (real logo + brand colours) and one theme per carrier in the carrier's own brand
   (logo from exzeo.com, colours picked from the logo, Florida background for the AI Publisher report).
3. No users are created (org is at its user limit) - assign existing users/groups to the carrier workspaces.
4. A carrier-specific custom dashboard in CORE, next to the standard (inherited) set.

    python3 exzeo/setup.py --themes     # themes only
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "theme"))
import build_themes as bt  # noqa: E402

bt.product_images = lambda cfg: {}  # no data-product cover art in the Exzeo themes

PARENT = "e74a1eaa18f74706b94e39f91552efe7"
INTER = "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2"
# Exzeo brand (exzeo.com logo SVG): navy #1B3554, greens #3B8639 / #44A942 / #44D541
NAVY, GREEN, LIME, LEAF = "#1B3554", "#3B8639", "#44D541", "#44A942"
BLUE, ORANGE = "#2F6DB5", "#F2A33A"   # supporting chart colours
EXZ_CDN = "https://cdn.prod.website-files.com/6797a6b5c734c8a068c27fc9/"
EXZ_LOGO = EXZ_CDN + "67b64b69a480c154b99565cc_Exzeo_logo_light_bg.svg"
EXZ_LOGO_DARK = EXZ_CDN + "67b636d0d005d236c75501dd_Exzeo_logo_dark_bg.svg"
# report cover / section backgrounds (theme assets cover_bg + section_bg)
EXZ_COVER = EXZ_CDN + "67acbb3b98b9bc503f3d7f77_Exzeo%20Banner-1080-poster-00001.jpg"   # exzeo.com hero
EXZ_SECTION = EXZ_CDN + "6797a6b6c734c8a068c28097_unsplash_3fPXt37X6UQ.webp"            # exzeo.com office photo
WM = "https://upload.wikimedia.org/wikipedia/commons/thumb/"


def carrier(name, logo, primary, deep, accent, tint, line, bg, client, categories):
    return dict(name=name, logo=EXZ_CDN + logo, primary=primary, deep=deep, accent=accent, tint=tint, line=line,
                bg=bg, client=client, categories=categories)


CARRIERS = {  # workspace id -> carrier; backgrounds from Wikimedia Commons (1920px)
    "3d9adaacc9c24fc49cd7b868b468ed6f": carrier(
        "Homeowners Choice", "679cf14a07528c1451962461_HCPCI_FullLogo_Vector-p-800.png",
        "#2E2A7A", "#221C55", "#D2232A", "#F4F4FA", "#DDDCEC",
        # West Palm Beach home with palms (Flamingo Park HD) - CC BY-SA 3.0
        WM + "f/f0/West_PB_FL_Flamingo_Park_Res_HD_house01.jpg/1920px-West_PB_FL_Flamingo_Park_Res_HD_house01.jpg",
        "merchant__bigboxretailer", ["Home Goods", "Furniture", "Computers & Accessories"]),
    "efdabe226f2c4456873673af50575d3b": carrier(
        "TypTap Insurance", "679cf0fa584cf23a986b2438_TypTap-Insurance-Full-Color-tm-p-800.png",
        "#4E9A2F", "#3B3838", "#2B9FD9", "#F4F8F2", "#DDE6D8",
        # Hurricane Milton from the ISS, 2024-10-08 - NASA, public domain
        WM + "5/5a/Hurricane_Milton_from_the_ISS_2024-10-08.jpg/1920px-Hurricane_Milton_from_the_ISS_2024-10-08.jpg",
        "merchant__electronics", ["Computers & Accessories", "Audio & Video Accessories"]),
    "ff02bcf531d143bf8fb8f37c3d29fb29": carrier(
        "CORE - Condo Owners Reciprocal Exchange", "679cf0f9a9f19ee8289b948c_CORE-Horizontal-color-p-800.png",
        "#1F8FA6", "#1B3159", "#33B1C9", "#F2F7FA", "#D6E4EC",
        # Sunny Isles Beach condos - CC BY 2.0
        WM + "f/fb/St_Tropez_on_The_Bay_-_Sunny_Isles_Beach_Condos.jpg/1920px-St_Tropez_on_The_Bay_-_Sunny_Isles_Beach_Condos.jpg",
        "merchant__clothing", ["Home Goods", "Clothing", "Audio & Video Accessories"]),
}
CUSTOM_DASH = ("ff02bcf531d143bf8fb8f37c3d29fb29", "overview", "core_custom_board",
               "CORE · Custom Board", "Carrier-specific dashboard built in the CORE workspace only.")
OLD_DASH = ("ff02bcf531d143bf8fb8f37c3d29fb29", "palm_harbor_custom_board")


def themes():
    out = {"exzeo": dict(name="Exzeo", ws=PARENT, brand="Exzeo", section_bg=EXZ_SECTION, **bt.light(
        primary=GREEN, deep=NAVY, accent=LIME, ink="#0F1F33", tint="#F3F6F9", line="#DCE3EC",
        viz=[NAVY, GREEN, LIME, BLUE, LEAF, "#8DA9C4", ORANGE, "#5C677D", "#B8D8B4", "#C6CED8"],
        header=(NAVY, "#FFFFFF", LIME), logo=EXZ_LOGO, header_logo=EXZ_LOGO_DARK, bg=EXZ_COVER,
        kpi={"bg": NAVY, "border": NAVY, "title": "#D3DCE8", "value": "#FFFFFF", "secondary": "#D3DCE8",
             "good": LIME, "bad": "#FFB3AA"}))}
    for ws, c in CARRIERS.items():
        out["exzeo_" + ws.replace("exzeo_", "")[:8]] = dict(name=c["name"], ws=ws, brand=c["name"], **bt.light(
            primary=c["primary"], deep=c["deep"], accent=c["accent"], ink="#10202B", tint=c["tint"], line=c["line"],
            viz=[c["deep"], c["primary"], c["accent"], NAVY, GREEN, "#8DA9C4", ORANGE, "#5C677D", "#B8C5D6",
                 "#F1C6C9"],
            header=("#FFFFFF", c["deep"], c["primary"]), logo=c["logo"], bg=c["bg"]))
    return out


def ok(code, resp, what):
    if code not in (200, 201, 204):
        sys.exit(f"{what}: {code} {resp}")


def set_ws_setting(ws, sid, stype, ref_id, ref_type):
    body = {"data": {"id": sid, "type": "workspaceSetting",
                     "attributes": {"type": stype, "content": {"id": ref_id, "type": ref_type}}}}
    code, resp = bt.api("PUT", f"/api/v1/entities/workspaces/{ws}/workspaceSettings/{sid}", body)
    if code == 404:
        code, resp = bt.api("POST", f"/api/v1/entities/workspaces/{ws}/workspaceSettings", body)
    ok(code, resp, f"{stype} on {ws}")


def deploy_themes():
    for tid, cfg in themes().items():
        t = bt.build_theme(cfg)
        t = json.loads(json.dumps(t).replace('"Zalando Sans"', '"Inter"').replace("Zalando Sans,", "Inter,"))
        t["typography"] = {"font": INTER, "fontBold": INTER}
        if cfg.get("section_bg"):  # separate section-page background
            for img in t["assets"]["images"] + t["assets"]["backgrounds"]:
                if img["id"] == "section_bg":
                    img["url"] = cfg["section_bg"]
        (HERE / f"{tid}_theme.json").write_text(json.dumps(t, indent=2))
        bt.upsert("themes", tid, f"{cfg['name']} (Exzeo)", t)
        bt.upsert("colorPalettes", tid, f"{cfg['name']} (Exzeo)", bt.palette(cfg["viz"]))
        # same setting ids the workspaces already use, so the old theme is replaced, not duplicated
        set_ws_setting(cfg["ws"], "85b5545e-d536-4596-9cec-8e878aa82ac7", "ACTIVE_THEME", tid, "theme")
        set_ws_setting(cfg["ws"], "00746de0-0491-4d9e-b0d1-2a64296164b9", "ACTIVE_COLOR_PALETTE", tid,
                       "colorPalette")
        print(f"  theme {tid:<22} -> {cfg['ws']}  ({cfg['name']})")


def wdf_setting(ws, wdf, values):
    sid = f"{ws[:8]}_{wdf.lower()}"
    code, resp = bt.api("GET", f"/api/v1/entities/workspaces/{ws}/workspaceDataFilterSettings?origin=NATIVE"
                               f"&include=workspaceDataFilter")
    ok(code, resp, f"read WDF settings {ws}")
    existing = [x for x in resp["data"] if x["relationships"]["workspaceDataFilter"]["data"]["id"] == wdf]
    sid = existing[0]["id"] if existing else sid
    body = {"data": {"id": sid, "type": "workspaceDataFilterSetting",
                     "attributes": {"filterValues": values, "title": ""},
                     "relationships": {"workspaceDataFilter": {"data": {"id": wdf, "type": "workspaceDataFilter"}}}}}
    if existing:
        code, resp = bt.api("PUT", f"/api/v1/entities/workspaces/{ws}/workspaceDataFilterSettings/{sid}", body)
    else:
        code, resp = bt.api("POST", f"/api/v1/entities/workspaces/{ws}/workspaceDataFilterSettings", body)
    ok(code, resp, f"WDF {wdf} on {ws}")


def workspaces():
    code, resp = bt.api("PATCH", f"/api/v1/entities/workspaces/{PARENT}",
                        {"data": {"id": PARENT, "type": "workspace",
                                  "attributes": {"name": "Exzeo Carrier Analytics (template)"}}})
    ok(code, resp, "rename parent")
    for ws, c in CARRIERS.items():
        body = {"data": {"id": ws, "type": "workspace", "attributes": {"name": c["name"]},
                         "relationships": {"parent": {"data": {"id": PARENT, "type": "workspace"}}}}}
        code, resp = bt.api("PATCH", f"/api/v1/entities/workspaces/{ws}",
                            {"data": {"id": ws, "type": "workspace", "attributes": {"name": c["name"]}}})
        if code == 404:
            code, resp = bt.api("POST", "/api/v1/entities/workspaces", body)
        ok(code, resp, f"workspace {ws}")
        wdf_setting(ws, "WDF__CLIENT_ID", [c["client"]])
        wdf_setting(ws, "WDF__PRODUCT_CATEGORY", c["categories"])
        print(f"  {ws:<34} {c['name']:<40} {c['client']} / {', '.join(c['categories'])}")


def custom_dashboard():
    ws, src, did, title, desc = CUSTOM_DASH
    bt.api("DELETE", f"/api/v1/entities/workspaces/{OLD_DASH[0]}/analyticalDashboards/{OLD_DASH[1]}")
    code, resp = bt.api("GET", f"/api/v1/entities/workspaces/{PARENT}/analyticalDashboards/{src}")
    ok(code, resp, "read source dashboard")
    content = resp["data"]["attributes"]["content"]
    body = {"data": {"id": did, "type": "analyticalDashboard",
                     "attributes": {"title": title, "description": desc, "content": content,
                                    "tags": ["Custom", "CORE"]}}}
    code, resp = bt.api("PUT", f"/api/v1/entities/workspaces/{ws}/analyticalDashboards/{did}", body)
    if code == 404:
        code, resp = bt.api("POST", f"/api/v1/entities/workspaces/{ws}/analyticalDashboards", body)
    ok(code, resp, "custom dashboard")
    print(f"  dashboard '{title}' -> {ws}")


if __name__ == "__main__":
    if "--themes" in sys.argv:
        deploy_themes(); sys.exit()
    print("workspaces");  workspaces()
    print("themes");      deploy_themes()
    print("custom");      custom_dashboard()
