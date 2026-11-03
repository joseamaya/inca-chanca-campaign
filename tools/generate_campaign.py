#!/usr/bin/env python3
"""
Genera los mapas .pmp/.xml, las vistas previas, los triggers y la campaña
"La Guerra Inca-Chanca (c. 1438)".

Los mapas son procedurales, pero el relieve y la disposición de los
asentamientos se inspiran en el valle del Cusco y en la pampa de Ichupampa.
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

MOD = Path(__file__).resolve().parents[1]
PREVIEW_DIR = MOD / "art/textures/ui/session/icons/mappreview"
MAP_DIR = MOD / "maps/scenarios"
CAMPAIGN_DIR = MOD / "campaigns"

TEXTURES = [
    "new_alpine_grass_a",
    "new_alpine_grass_b",
    "new_alpine_grass_c",
    "new_alpine_grass_d",
    "alpine_grass_rocky",
    "alpine_mountainside",
    "alpine_snow_a",
    "new_alpine_grass_dirt_a",
    "alpine_dirt",
    "new_alpine_citytile",
]
TEX_INDEX = {name: i for i, name in enumerate(TEXTURES)}

# Marcadores invisibles para que la línea de tiempo sobreviva a guardar/cargar.
MARKERS = {
    "m1": [(9001, 10, 10), (9002, 30, 10), (9003, 50, 10), (9004, 70, 10), (9005, 90, 10)],
    "m2": [(9011, 10, 10), (9012, 30, 10), (9013, 50, 10), (9014, 70, 10), (9015, 90, 10)],
    "m3": [(9021, 10, 10), (9022, 30, 10), (9023, 50, 10)],
    "m4": [(9031, 10, 10), (9032, 30, 10)],
    "epilogue": [(9041, 10, 10)],
}


def smoothstep(a: float, b: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def make_heightmap(patches: int, style: str, seed: int) -> np.ndarray:
    n = patches * 16 + 1
    xs = np.linspace(0.0, 1.0, n)
    X, Z = np.meshgrid(xs, xs)
    rng = np.random.default_rng(seed)

    base = 1700.0 + 250.0 * np.sin(2.0 * np.pi * X) * np.cos(2.0 * np.pi * Z)
    edge = np.maximum(np.abs(X - 0.5), np.abs(Z - 0.5)) * 2.0
    h = base + 8200.0 * smoothstep(0.58, 1.0, edge)

    # Cordilleras laterales: no son simétricas, como el relieve andino.
    for angle, amp, fx, fz in ((0.6, 1100, 3.0, 1.2), (2.1, 850, 1.4, 3.4), (4.0, 700, 2.2, 2.0)):
        h += amp * np.sin(2 * np.pi * (fx * X + fz * Z) + angle) * smoothstep(0.45, 1.0, edge)

    if style == "cusco":
        cx, cz, r = 0.40, 0.56, 0.17
    elif style == "siege":
        cx, cz, r = 0.45, 0.55, 0.20
    elif style == "pampa":
        cx, cz, r = 0.50, 0.50, 0.23
    elif style == "chanca":
        cx, cz, r = 0.24, 0.75, 0.16
    else:  # epilogue
        cx, cz, r = 0.50, 0.50, 0.25

    # Meseta/valle central
    mask = np.exp(-(((X - cx) ** 2 + (Z - cz) ** 2) / (r * r)))
    plateau = 2300.0
    h = h * (1.0 - mask) + plateau * mask

    # Suavizado y ruido de detalle
    h += gaussian_filter(rng.normal(0.0, 110.0, (n, n)), 2.0)
    h = gaussian_filter(h, 3.0)

    # Ajuste de rango. Los valores son unidades de altura de 0 A.D. (92/m).
    h = (h - h.min()) / (h.max() - h.min())
    h = 700.0 + h * (12500.0 if style != "epilogue" else 5000.0)
    return h


def assign_tiles(h: np.ndarray, patches: int, style: str) -> np.ndarray:
    tiles = patches * 16
    hh = h[:-1, :-1]
    gy, gx = np.gradient(h)
    slope = np.hypot(gx[:-1, :-1], gy[:-1, :-1])
    n = h.shape[0]
    xs = np.linspace(0.0, 1.0, n)
    X, Z = np.meshgrid(xs, xs)
    cx, cz, r = (0.40, 0.56, 0.14) if style == "cusco" else \
                (0.45, 0.55, 0.17) if style == "siege" else \
                (0.50, 0.50, 0.12) if style == "pampa" else \
                (0.24, 0.75, 0.12) if style == "chanca" else (0.50, 0.50, 0.20)
    city = ((X[:-1, :-1] - cx) ** 2 + (Z[:-1, :-1] - cz) ** 2) < r * r

    rng = np.random.default_rng(4242)
    tile_tex = np.zeros((tiles, tiles), dtype=np.uint16)
    for z in range(tiles):
        for x in range(tiles):
            height = hh[z, x]
            s = slope[z, x]
            if city[z, x] and s < 35:
                tex = "new_alpine_citytile"
            elif height > 9600:
                tex = "alpine_snow_a"
            elif height > 7600 or s > 55:
                tex = "alpine_mountainside"
            elif s > 30:
                tex = "alpine_grass_rocky" if height < 6000 else "alpine_mountainside"
            elif height < 2200:
                tex = "new_alpine_grass_dirt_a" if rng.random() < 0.45 else "alpine_dirt"
            else:
                r = rng.random()
                if r < 0.30:
                    tex = "new_alpine_grass_a"
                elif r < 0.55:
                    tex = "new_alpine_grass_b"
                elif r < 0.75:
                    tex = "new_alpine_grass_c"
                elif r < 0.90:
                    tex = "new_alpine_grass_d"
                else:
                    tex = "alpine_grass_rocky"
            tile_tex[z, x] = TEX_INDEX[tex]
    return tile_tex


def write_pmp(path: Path, patches: int, heightmap: np.ndarray, tile_tex: np.ndarray) -> None:
    n = patches * 16 + 1
    assert heightmap.shape == (n, n)
    heights = np.clip(heightmap, 0, 65535).astype("<u2")
    body = struct.pack("<I", patches)
    body += heights.tobytes()
    body += struct.pack("<I", len(TEXTURES))
    for name in TEXTURES:
        raw = name.encode("ascii")
        body += struct.pack("<I", len(raw)) + raw
    tiles = patches * 16
    for z in range(tiles):
        for x in range(tiles):
            body += struct.pack("<4H", int(tile_tex[z, x]), 0xFFFF, 0, 0)
    data = b"PSMP" + struct.pack("<II", 7, len(body)) + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def preview_from_heightmap(heightmap: np.ndarray, path: Path, title: str = "") -> None:
    h = heightmap.astype(np.float32)
    h = (h - h.min()) / max(1.0, h.max() - h.min())
    gy, gx = np.gradient(h)
    slope = np.clip(np.hypot(gx, gy) * 2.2, 0.0, 1.0)
    # Sombreado de relieve simple para que se lean los valles y las cadenas.
    shade = np.clip(0.55 + 2.8 * (gx * 0.6 + gy * 0.8), 0.0, 1.0)
    rgb = np.zeros((*h.shape, 3), dtype=np.float32)
    # Puna: verdes amarillentos; roca: gris; nieve: blanco.
    rgb[..., 0] = 0.30 + 0.38 * h + 0.22 * slope
    rgb[..., 1] = 0.36 + 0.34 * h + 0.12 * slope
    rgb[..., 2] = 0.18 + 0.20 * h + 0.24 * slope
    rgb = rgb * (0.62 + 0.55 * shade[..., None])
    snow = smoothstep(0.82, 0.98, h)
    rgb = rgb * (1.0 - snow[..., None]) + np.array([0.92, 0.94, 0.97]) * snow[..., None]
    rgb = np.clip(rgb, 0.0, 1.0)
    im = Image.fromarray((rgb * 255).astype(np.uint8), "RGB").resize((512, 512), Image.Resampling.LANCZOS)
    if title:
        draw = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        except Exception:
            font = ImageFont.load_default()
        draw.rectangle((0, 0, 512, 44), fill=(20, 12, 8))
        draw.text((14, 8), title, fill=(235, 205, 150), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def make_campaign_image(path: Path) -> None:
    im = Image.new("RGB", (512, 512), (46, 20, 14))
    d = ImageDraw.Draw(im)
    for y in range(512):
        c = (60 + int(40 * y / 512), 22 + int(16 * y / 512), 16 + int(8 * y / 512))
        d.line((0, y, 512, y), fill=c)
    # Montañas estilizadas
    d.polygon([(0, 340), (90, 180), (170, 300), (250, 150), (340, 290), (420, 190), (512, 330), (512, 512), (0, 512)], fill=(72, 56, 40))
    d.polygon([(0, 390), (120, 260), (210, 360), (300, 240), (400, 350), (512, 270), (512, 512), (0, 512)], fill=(55, 42, 30))
    # Sol
    d.ellipse((380, 50, 470, 140), fill=(230, 180, 80))
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    d.text((24, 386), "LA GUERRA", fill=(245, 220, 170), font=font_big)
    d.text((24, 432), "INCA-CHANCA", fill=(245, 220, 170), font=font_big)
    d.text((26, 482), "c. 1438 d. C. · Yahuar Pampa", fill=(220, 190, 145), font=font_small)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


class Mission:
    def __init__(self, key: str, name: str, mapname: str, style: str, seed: int, patches: int,
                 description: str, players: list[dict], triggers: str, preview_title: str):
        self.key = key
        self.name = name
        self.mapname = mapname
        self.style = style
        self.seed = seed
        self.patches = patches
        self.description = description
        self.players = players
        self.triggers = triggers
        self.preview_title = preview_title
        self.entities: list[dict] = []
        self._uid = 10000

    def add(self, template: str, player: int, x: float, z: float, rot: float = 0.0, uid: int | None = None) -> int:
        if uid is None:
            uid = self._uid
            self._uid += 1
        self.entities.append({"uid": uid, "template": template, "player": player, "x": x, "z": z, "rot": rot})
        return uid


def player(civ: str, name: str, color: tuple[int, int, int], team: int, resources: dict) -> dict:
    return {
        "AI": "",
        "Civ": civ,
        "Color": {"r": color[0], "g": color[1], "b": color[2]},
        "Name": name,
        "Resources": resources,
        "Team": team,
    }


def scatter(m: Mission, count: int, templates: list[str], rng: np.random.Generator,
            avoid: list[tuple[float, float, float]], margin: float = 60.0) -> None:
    size = m.patches * 16 * 4
    placed = 0
    tries = 0
    while placed < count and tries < count * 40:
        tries += 1
        x = float(rng.uniform(margin, size - margin))
        z = float(rng.uniform(margin, size - margin))
        if any((x - ax) ** 2 + (z - az) ** 2 < ar * ar for ax, az, ar in avoid):
            continue
        m.add(templates[placed % len(templates)], 0, x, z, float(rng.uniform(0, 2 * math.pi)))
        placed += 1


def mission_1() -> Mission:
    m = Mission(
        "m1", "1. La amenaza chanca", "inca_chanca_01_cusco", "cusco", 1438, 16,
        "Cusco, c. 1438. Los mensajeros chancas exigen la sumisión del Curacazgo. Viracocha Inca e Inca Urco abandonan la ciudad; Cusi Yupanqui decide resistir. Reúne recursos, fortifica Cusco y rechaza las primeras incursiones.",
        [
            player("inca", "Cusco (Cusi Yupanqui)", (190, 45, 35), 1, {"food": 1800, "wood": 900, "stone": 900, "metal": 500}),
            player("chanca", "Confederación chanca", (170, 125, 35), 2, {"food": 3000, "wood": 2000, "stone": 1500, "metal": 800}),
            player("inca", "Aliados canas", (45, 85, 190), 1, {"food": 900, "wood": 600, "stone": 500, "metal": 300}),
        ],
        "inca_chanca_01_triggers.js", "1 · La amenaza chanca",
    )
    # Cusco
    m.add("structures/inca/civil_centre", 1, 400, 560, 0, 1100)
    m.add("structures/inca/temple", 1, 360, 610, 0, 1101)
    m.add("structures/inca/barracks", 1, 450, 610, 0, 1102)
    m.add("structures/inca/market", 1, 430, 650, 0, 1103)
    m.add("structures/inca/storehouse", 1, 350, 520, 0, 1104)
    m.add("structures/inca/farmstead", 1, 320, 570, 0, 1105)
    for x, z in ((370, 520), (430, 520), (340, 600), (460, 570), (390, 640), (480, 640)):
        m.add("structures/inca/house", 1, x, z, 0)
    for x, z in ((290, 610), (290, 640), (320, 640), (320, 670)):
        m.add("structures/inca/field", 1, x, z, 0)
    m.add("structures/inca/defense_tower", 1, 360, 500, 0)
    m.add("structures/inca/defense_tower", 1, 460, 520, 0)
    for x, z in ((400, 580), (415, 585), (385, 585), (405, 595), (390, 575), (420, 575)):
        m.add("units/inca/support_civilian", 1, x, z)
    for x, z in ((420, 590), (425, 595), (415, 600), (430, 585)):
        m.add("units/inca/infantry_maceman_b", 1, x, z)
    for x, z in ((380, 590), (375, 595), (385, 600)):
        m.add("units/inca/infantry_slinger_b", 1, x, z)
    for x, z in ((410, 600), (405, 605), (415, 610)):
        m.add("units/inca/infantry_spearman_b", 1, x, z)
    m.add("units/inca/hero_cusi_yupanqui", 1, 400, 520, 0, 1000)
    m.add("units/inca/hero_viracocha_inca", 1, 380, 500, 0, 1001)
    m.add("units/inca/hero_inca_urco", 1, 390, 510, 0, 1002)

    # Aldea aliada cana
    m.add("structures/inca/civil_centre", 3, 180, 820, 0, 3100)
    for x, z in ((150, 790), (210, 790), (180, 850)):
        m.add("structures/inca/house", 3, x, z, 0)
    m.add("structures/inca/defense_tower", 3, 150, 850, 0)
    for i in range(7):
        m.add("units/inca/infantry_spearman_b", 3, 180 + (i % 3) * 8, 810 + (i // 3) * 8)
    for i in range(3):
        m.add("units/inca/infantry_slinger_b", 3, 190 + i * 7, 800)

    # Campamento chanca
    m.add("structures/chanca/civil_centre", 2, 820, 200, 0, 2100)
    m.add("structures/chanca/barracks", 2, 780, 240, 0)
    for x, z in ((850, 230), (800, 270), (760, 200), (860, 180)):
        m.add("structures/chanca/house", 2, x, z, 0)
    m.add("structures/chanca/defense_tower", 2, 850, 260, 0)
    m.add("structures/chanca/farmstead", 2, 780, 160, 0)
    m.add("structures/chanca/storehouse", 2, 860, 150, 0)
    m.add("units/chanca/hero_astoy_huaraca", 2, 820, 230, 0, 2001)
    m.add("units/chanca/hero_tomay_huaraca", 2, 805, 230, 0, 2002)
    for i in range(10):
        m.add("units/chanca/infantry_maceman_b", 2, 800 + (i % 5) * 8, 185 + (i // 5) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_slinger_b", 2, 835 + (i % 3) * 8, 195 + (i // 3) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_spearman_b", 2, 780 + (i % 3) * 8, 215 + (i // 3) * 8)
    for i in range(4):
        m.add("units/chanca/infantry_axeman_b", 2, 845 + i * 6, 220)

    rng = np.random.default_rng(11)
    avoid = [(400, 560, 150), (820, 200, 110), (180, 820, 70)]
    scatter(m, 70, ["gaia/tree/pine", "gaia/tree/pine_black", "gaia/tree/fir"], rng, avoid, 90)
    scatter(m, 16, ["gaia/rock/alpine_large", "gaia/rock/alpine_small"], rng, avoid, 90)
    scatter(m, 14, ["gaia/ore/alpine_large", "gaia/ore/alpine_small"], rng, avoid, 90)
    scatter(m, 14, ["gaia/fruit/berry_01", "gaia/fruit/berry_02"], rng, avoid, 90)
    scatter(m, 10, ["gaia/fauna_deer"], rng, avoid, 100)
    return m


def mission_2() -> Mission:
    m = Mission(
        "m2", "2. El asedio de Cusco", "inca_chanca_02_siege", "siege", 1439, 16,
        "El ejército chanca rodea Cusco. La tradición recuerda la defensa de Carmenca y Chocos-Cachona. Protege el centro cívico y el santuario, resiste las oleadas y conserva con vida a Cusi Yupanqui.",
        [
            player("inca", "Cusco sitiado", (190, 45, 35), 1, {"food": 2200, "wood": 1200, "stone": 1200, "metal": 700}),
            player("chanca", "Huestes chancas", (170, 125, 35), 2, {"food": 4000, "wood": 2500, "stone": 2000, "metal": 1200}),
        ],
        "inca_chanca_02_triggers.js", "2 · El asedio de Cusco",
    )
    m.add("structures/inca/civil_centre", 1, 450, 560, 0, 1100)
    m.add("structures/inca/temple", 1, 410, 610, 0, 1101)
    m.add("structures/inca/barracks", 1, 500, 610, 0, 1102)
    m.add("structures/inca/market", 1, 500, 660, 0, 1103)
    m.add("structures/inca/storehouse", 1, 380, 520, 0, 1104)
    m.add("structures/inca/farmstead", 1, 350, 570, 0, 1105)
    for x, z in ((370, 480), (430, 480), (530, 560), (470, 660), (380, 660), (540, 620), (340, 610), (520, 500)):
        m.add("structures/inca/house", 1, x, z, 0)
    for x, z in ((290, 610), (290, 640), (320, 640), (320, 670)):
        m.add("structures/inca/field", 1, x, z, 0)
    for x, z in ((370, 480), (530, 480), (370, 620), (530, 620)):
        m.add("structures/inca/defense_tower", 1, x, z, 0)
    m.add("units/inca/hero_cusi_yupanqui", 1, 450, 540, 0, 1000)
    m.add("units/inca/hero_chanan_curi_coca", 1, 430, 540, 0, 1003)
    for i in range(12):
        m.add("units/inca/infantry_maceman_b", 1, 430 + (i % 4) * 8, 595 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_slinger_b", 1, 470 + (i % 4) * 8, 595 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_spearman_b", 1, 405 + (i % 4) * 8, 575 + (i // 4) * 8)
    for i in range(4):
        m.add("units/inca/infantry_axeman_b", 1, 490 + i * 7, 575)
    for i in range(6):
        m.add("units/inca/support_civilian", 1, 420 + (i % 3) * 8, 620 + (i // 3) * 8)

    # Campamentos chancas
    m.add("structures/chanca/civil_centre", 2, 820, 300, 0, 2100)
    m.add("structures/chanca/barracks", 2, 790, 340, 0)
    for x, z in ((850, 330), (800, 370), (760, 300), (860, 270)):
        m.add("structures/chanca/house", 2, x, z, 0)
    m.add("structures/chanca/defense_tower", 2, 850, 360, 0)
    m.add("structures/chanca/barracks", 2, 820, 780, 0)
    for x, z in ((790, 740), (850, 740), (800, 820)):
        m.add("structures/chanca/house", 2, x, z, 0)
    m.add("structures/chanca/defense_tower", 2, 790, 810, 0)
    m.add("units/chanca/hero_astoy_huaraca", 2, 820, 330, 0, 2001)
    m.add("units/chanca/hero_tomay_huaraca", 2, 805, 330, 0, 2002)
    m.add("units/chanca/hero_ancu_huallo", 2, 820, 790, 0, 2003)
    for i in range(12):
        m.add("units/chanca/infantry_maceman_b", 2, 800 + (i % 4) * 8, 290 + (i // 4) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_slinger_b", 2, 840 + (i % 3) * 8, 300 + (i // 3) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_spearman_b", 2, 780 + (i % 3) * 8, 315 + (i // 3) * 8)
    for i in range(10):
        m.add("units/chanca/infantry_maceman_b", 2, 810 + (i % 5) * 8, 760 + (i // 5) * 8)
    for i in range(5):
        m.add("units/chanca/infantry_slinger_b", 2, 800 + i * 8, 800)
    m.add("units/chanca/relic_uscovilca", 2, 820, 550, 0, 2000)
    for i in range(4):
        m.add("units/chanca/infantry_axeman_b", 2, 805 + i * 7, 540)

    rng = np.random.default_rng(22)
    avoid = [(450, 560, 180), (820, 300, 100), (820, 780, 100)]
    scatter(m, 60, ["gaia/tree/pine", "gaia/tree/pine_black", "gaia/tree/fir"], rng, avoid, 90)
    scatter(m, 14, ["gaia/rock/alpine_large", "gaia/rock/alpine_small"], rng, avoid, 90)
    scatter(m, 12, ["gaia/ore/alpine_large", "gaia/ore/alpine_small"], rng, avoid, 90)
    scatter(m, 12, ["gaia/fruit/berry_01", "gaia/fruit/berry_02"], rng, avoid, 90)
    scatter(m, 8, ["gaia/fauna_deer"], rng, avoid, 100)
    return m


def mission_3() -> Mission:
    m = Mission(
        "m3", "3. Yahuar Pampa", "inca_chanca_03_pampa", "pampa", 1440, 16,
        "La pampa de Ichupampa, luego llamada Yahuar Pampa, es el escenario de la batalla decisiva. Mantén la línea, elimina o captura a los capitanes chancas y toma la momia de Uscovilca. La tradición de los pururaucas se presenta como leyenda, no como hecho comprobado.",
        [
            player("inca", "Cusco y aliados", (190, 45, 35), 1, {"food": 2500, "wood": 1500, "stone": 1200, "metal": 900}),
            player("chanca", "Confederación chanca", (170, 125, 35), 2, {"food": 3500, "wood": 2000, "stone": 1500, "metal": 1000}),
            player("inca", "Contingente cana", (45, 85, 190), 1, {"food": 1200, "wood": 700, "stone": 500, "metal": 400}),
        ],
        "inca_chanca_03_triggers.js", "3 · Yahuar Pampa",
    )
    m.add("structures/inca/civil_centre", 1, 300, 512, 0, 1100)
    m.add("structures/inca/barracks", 1, 260, 560, 0)
    m.add("structures/inca/temple", 1, 260, 460, 0)
    for x, z in ((340, 470), (340, 550), (350, 512), (300, 580)):
        m.add("structures/inca/house", 1, x, z, 0)
    m.add("structures/inca/defense_tower", 1, 360, 512, 0)
    m.add("structures/inca/farmstead", 1, 220, 600, 0)
    m.add("units/inca/hero_cusi_yupanqui", 1, 340, 512, 0, 1000)
    m.add("units/inca/hero_chanan_curi_coca", 1, 360, 540, 0, 1003)
    for i in range(12):
        m.add("units/inca/infantry_maceman_b", 1, 390 + (i % 4) * 8, 500 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_slinger_b", 1, 430 + (i % 4) * 8, 500 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_spearman_b", 1, 380 + (i % 4) * 8, 530 + (i // 4) * 8)
    for i in range(4):
        m.add("units/inca/infantry_axeman_b", 1, 420 + i * 7, 540)
    for i in range(6):
        m.add("units/inca/support_civilian", 1, 300 + (i % 3) * 8, 540 + (i // 3) * 8)

    # Aliados canas
    m.add("structures/inca/civil_centre", 3, 300, 800, 0, 3100)
    for x, z in ((270, 770), (330, 770), (300, 830)):
        m.add("structures/inca/house", 3, x, z, 0)
    m.add("structures/inca/defense_tower", 3, 330, 800, 0)
    for i in range(10):
        m.add("units/inca/infantry_spearman_b", 3, 290 + (i % 5) * 8, 780 + (i // 5) * 8)
    for i in range(5):
        m.add("units/inca/infantry_slinger_b", 3, 300 + i * 7, 810)

    # Chancas
    m.add("structures/chanca/civil_centre", 2, 750, 512, 0, 2100)
    m.add("structures/chanca/barracks", 2, 790, 560, 0)
    m.add("structures/chanca/temple", 2, 760, 450, 0)
    for x, z in ((820, 480), (820, 550), (800, 600), (720, 580)):
        m.add("structures/chanca/house", 2, x, z, 0)
    m.add("structures/chanca/defense_tower", 2, 700, 512, 0)
    m.add("units/chanca/hero_astoy_huaraca", 2, 620, 512, 0, 2001)
    m.add("units/chanca/hero_tomay_huaraca", 2, 640, 530, 0, 2002)
    m.add("units/chanca/hero_ancu_huallo", 2, 660, 550, 0, 2003)
    for i in range(15):
        m.add("units/chanca/infantry_maceman_b", 2, 630 + (i % 5) * 8, 480 + (i // 5) * 8)
    for i in range(8):
        m.add("units/chanca/infantry_slinger_b", 2, 670 + (i % 4) * 8, 495 + (i // 4) * 8)
    for i in range(8):
        m.add("units/chanca/infantry_spearman_b", 2, 620 + (i % 4) * 8, 550 + (i // 4) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_axeman_b", 2, 680 + i * 7, 570)
    m.add("units/chanca/relic_uscovilca", 2, 740, 512, 0, 2000)
    for i in range(4):
        m.add("units/chanca/infantry_axeman_b", 2, 720 + i * 7, 500)

    rng = np.random.default_rng(33)
    avoid = [(300, 512, 120), (300, 800, 80), (750, 512, 130), (500, 512, 80)]
    scatter(m, 45, ["gaia/tree/pine", "gaia/tree/fir", "gaia/tree/bush_steppe_01"], rng, avoid, 90)
    scatter(m, 12, ["gaia/rock/alpine_large", "gaia/rock/alpine_small"], rng, avoid, 90)
    scatter(m, 10, ["gaia/ore/alpine_large", "gaia/ore/alpine_small"], rng, avoid, 90)
    scatter(m, 8, ["gaia/fruit/berry_01", "gaia/fruit/berry_02"], rng, avoid, 90)
    scatter(m, 8, ["gaia/fauna_deer"], rng, avoid, 100)
    return m


def mission_4() -> Mission:
    m = Mission(
        "m4", "4. La campaña chanca", "inca_chanca_04_andahuaylas", "chanca", 1441, 16,
        "Cusi Yupanqui lleva la guerra al territorio chanca, hacia Andahuaylas y el Apurímac. Toma la fortaleza de altura, derrota o captura a Anccu Huallo y decide el destino de los supervivientes. La incorporación de guerreros chancas al ejército inca fue una práctica documentada.",
        [
            player("inca", "Cusco (Pachacútec)", (190, 45, 35), 1, {"food": 3000, "wood": 1800, "stone": 1500, "metal": 1200}),
            player("chanca", "Fortaleza chanca", (170, 125, 35), 2, {"food": 3500, "wood": 2200, "stone": 2500, "metal": 1200}),
        ],
        "inca_chanca_04_triggers.js", "4 · La campaña chanca",
    )
    m.add("structures/inca/civil_centre", 1, 220, 760, 0, 1100)
    m.add("structures/inca/barracks", 1, 270, 720, 0)
    m.add("structures/inca/temple", 1, 170, 720, 0)
    for x, z in ((240, 680), (280, 780), (180, 800), (300, 760)):
        m.add("structures/inca/house", 1, x, z, 0)
    m.add("structures/inca/defense_tower", 1, 300, 800, 0)
    m.add("structures/inca/farmstead", 1, 160, 820, 0)
    m.add("structures/inca/storehouse", 1, 240, 820, 0)
    m.add("units/inca/hero_cusi_yupanqui", 1, 260, 760, 0, 1000)
    for i in range(12):
        m.add("units/inca/infantry_maceman_b", 1, 300 + (i % 4) * 8, 720 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_slinger_b", 1, 340 + (i % 4) * 8, 720 + (i // 4) * 8)
    for i in range(8):
        m.add("units/inca/infantry_spearman_b", 1, 300 + (i % 4) * 8, 760 + (i // 4) * 8)
    for i in range(4):
        m.add("units/inca/infantry_axeman_b", 1, 340 + i * 7, 760)
    for i in range(6):
        m.add("units/inca/support_civilian", 1, 200 + (i % 3) * 8, 760 + (i // 3) * 8)

    m.add("structures/chanca/civil_centre", 2, 780, 280, 0, 2100)
    m.add("structures/chanca/barracks", 2, 820, 330, 0)
    m.add("structures/chanca/temple", 2, 740, 220, 0)
    for x, z in ((840, 250), (860, 320), (720, 330), (760, 360)):
        m.add("structures/chanca/house", 2, x, z, 0)
    for x, z in ((720, 260), (840, 360), (700, 360), (860, 220)):
        m.add("structures/chanca/defense_tower", 2, x, z, 0)
    m.add("structures/chanca/wall_long", 2, 760, 380, 0)
    m.add("structures/chanca/wall_long", 2, 800, 380, 0)
    m.add("units/chanca/hero_ancu_huallo", 2, 780, 320, 0, 2003)
    for i in range(15):
        m.add("units/chanca/infantry_maceman_b", 2, 740 + (i % 5) * 8, 280 + (i // 5) * 8)
    for i in range(10):
        m.add("units/chanca/infantry_slinger_b", 2, 800 + (i % 5) * 8, 290 + (i // 5) * 8)
    for i in range(8):
        m.add("units/chanca/infantry_spearman_b", 2, 730 + (i % 4) * 8, 330 + (i // 4) * 8)
    for i in range(6):
        m.add("units/chanca/infantry_axeman_b", 2, 800 + i * 7, 340)
    m.add("units/chanca/relic_uscovilca", 2, 800, 250, 0, 2000)

    rng = np.random.default_rng(44)
    avoid = [(220, 760, 120), (780, 280, 130)]
    scatter(m, 55, ["gaia/tree/pine", "gaia/tree/pine_black", "gaia/tree/fir"], rng, avoid, 90)
    scatter(m, 16, ["gaia/rock/alpine_large", "gaia/rock/alpine_small"], rng, avoid, 90)
    scatter(m, 12, ["gaia/ore/alpine_large", "gaia/ore/alpine_small"], rng, avoid, 90)
    scatter(m, 12, ["gaia/fruit/berry_01", "gaia/fruit/berry_02"], rng, avoid, 90)
    scatter(m, 8, ["gaia/fauna_deer"], rng, avoid, 100)
    return m


def mission_epilogue() -> Mission:
    m = Mission(
        "epilogue", "Epílogo: Pachacútec", "inca_chanca_05_epilogo", "epilogue", 1442, 8,
        "Cusco, después de la victoria. Cusi Yupanqui asume el mando y toma el nombre de Pachacútec. La tradición recuerda la victoria como el inicio del Tawantinsuyu; las crónicas difieren en los detalles y en la fecha exacta.",
        [
            player("inca", "Cusco (Pachacútec)", (190, 45, 35), -1, {"food": 2000, "wood": 1000, "stone": 1000, "metal": 500}),
        ],
        "inca_chanca_05_triggers.js", "Epílogo · Pachacútec",
    )
    m.add("structures/inca/civil_centre", 1, 256, 256, 0, 1100)
    m.add("structures/inca/temple", 1, 210, 300, 0)
    m.add("structures/inca/market", 1, 300, 300, 0)
    for x, z in ((210, 210), (300, 210), (210, 340), (300, 340)):
        m.add("structures/inca/house", 1, x, z, 0)
    m.add("units/inca/hero_pachacutec", 1, 256, 290, 0, 1000)
    for i in range(10):
        m.add("units/inca/support_civilian", 1, 230 + (i % 5) * 8, 280 + (i // 5) * 8)
    for i in range(6):
        m.add("units/inca/infantry_maceman_b", 1, 230 + (i % 3) * 8, 320 + (i // 3) * 8)
    rng = np.random.default_rng(55)
    scatter(m, 20, ["gaia/tree/pine", "gaia/tree/fir"], rng, [(256, 256, 80)], 40)
    return m


def write_map_xml(m: Mission) -> None:
    settings = {
        "AISeed": 0,
        "AllyView": False,
        "CircularMap": False,
        "Description": m.description,
        "Keywords": ["campaign", "inca", "chanca", "historical"],
        "LockTeams": True,
        "LastManStanding": False,
        "Name": m.name,
        "PlayerData": [""] + m.players,
        "DisableTreasures": True,
        "RevealMap": False,
        "TriggerScripts": ["scripts/TriggerHelper.js", "scenarios/inca_chanca_common.js", f"scenarios/{m.triggers}"],
        "VictoryConditions": [],
    }
    settings_json = json.dumps(settings, ensure_ascii=False, indent=2)
    env = """  <Environment>
    <SkySet>cumulus</SkySet>
    <SunColor r="0.82" g="0.76" b="0.64"/>
    <SunElevation angle="0.72"/>
    <SunRotation angle="0.85"/>
    <AmbientColor r="0.42" g="0.42" b="0.38"/>
    <Fog>
      <FogFactor>0</FogFactor>
      <FogThickness>0.5</FogThickness>
      <FogColor r="0.78" g="0.80" b="0.84"/>
    </Fog>
    <Water>
      <WaterBody>
        <Type>default</Type>
        <Color r="0.12" g="0.18" b="0.22"/>
        <Tint r="0.20" g="0.28" b="0.32"/>
        <Height>-100</Height>
        <Waviness>2</Waviness>
        <Murkiness>0.6</Murkiness>
        <WindAngle>0</WindAngle>
      </WaterBody>
    </Water>
    <Postproc>
      <Brightness>0</Brightness>
      <Contrast>1.02</Contrast>
      <Saturation>1.02</Saturation>
      <Bloom>0.15</Bloom>
      <PostEffect>default</PostEffect>
    </Postproc>
  </Environment>
"""
    size = m.patches * 16 * 4
    camera = f"""  <Camera>
    <Position x="{size*0.5}" y="380" z="{size*0.82}"/>
    <Rotation angle="0"/>
    <Declination angle="0.9"/>
  </Camera>
"""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Scenario version="7">', env, camera,
             '  <ScriptSettings><![CDATA[', settings_json, ']]></ScriptSettings>', '  <Entities>']
    for e in m.entities:
        lines.append(f'    <Entity uid="{e["uid"]}">')
        lines.append(f'      <Template>{e["template"]}</Template>')
        lines.append(f'      <Player>{e["player"]}</Player>')
        lines.append(f'      <Position x="{e["x"]:.2f}" z="{e["z"]:.2f}"/>')
        lines.append(f'      <Orientation y="{e["rot"]:.4f}"/>')
        lines.append('    </Entity>')
    for uid, x, z in MARKERS.get(m.key, []):
        lines.append(f'    <Entity uid="{uid}">')
        lines.append('      <Template>trigger/trigger_point_A</Template>')
        lines.append('      <Player>0</Player>')
        lines.append(f'      <Position x="{x:.2f}" z="{z:.2f}"/>')
        lines.append('      <Orientation y="0"/>')
        lines.append('    </Entity>')
    lines.append('  </Entities>')
    lines.append('  <Paths/>')
    lines.append('</Scenario>')
    (MAP_DIR / f"{m.mapname}.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


COMMON_JS = r"""
// Funciones comunes de la campaña inca-chanca.
Trigger.prototype.ICMessage = function(text)
{
	const cmpGuiInterface = Engine.QueryInterface(SYSTEM_ENTITY, IID_GuiInterface);
	cmpGuiInterface.PushNotification({
		"type": "tutorial",
		"players": [1],
		"instructions": [text]
	});
};

Trigger.prototype.ICObjective = function(text)
{
	this.ICMessage("OBJETIVO: " + text);
};

Trigger.prototype.ICWin = function(text)
{
	if (this.icEnded)
		return;
	this.icEnded = true;
	const cmpEndGameManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_EndGameManager);
	cmpEndGameManager.MarkPlayerAndAlliesAsWon(1, () => text, () => "Has sido derrotado.");
};

Trigger.prototype.ICLose = function(text)
{
	if (this.icEnded)
		return;
	this.icEnded = true;
	TriggerHelper.DefeatPlayer(1, text);
};

Trigger.prototype.ICTime = function()
{
	return TriggerHelper.GetTime();
};

// Los marcadores son trigger points invisibles colocados en el mapa.
Trigger.prototype.ICMarker = function(uid)
{
	return !!Engine.QueryInterface(uid, IID_Position);
};

Trigger.prototype.ICConsume = function(uid)
{
	if (!this.ICMarker(uid))
		return false;
	Engine.DestroyEntity(uid);
	return true;
};

// Restricciones históricas para el jugador inca en 1438.
Trigger.prototype.ICRestrictInca = function()
{
	const cmpPlayerManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_PlayerManager);
	const playerEnt = cmpPlayerManager.GetPlayerByID(1);
	const cmpPlayer = Engine.QueryInterface(playerEnt, IID_Player);
	if (!cmpPlayer)
		return;
	const disabled = [
		"units/inca/mechanical_siege_ram",
		"units/inca/champion_imperial",
		"units/inca/champion_guaranga_kamayuk",
		"units/inca/champion_apusquin_rantin",
		"units/inca/champion_apusquin _rantin",
		"units/inca/champion_pachac_kamayuk",
		"units/inca/champion_infantry_archer",
		"units/inca/champion_pikeman",
		"units/inca/hero_pachacutec",
		"units/inca/hero_sapa_inca",
		"units/inca/hero_sinchi_roca",
		"units/inca/hero_capac_yupanqui",
		"units/inca/ship_arrow",
		"units/inca/ship_fishing",
		"units/inca/ship_merchant",
		"units/inca/ship_scout",
		"units/inca/infantry_archer_merc_a",
		"units/inca/infantry_archer_merc_b",
		"units/inca/infantry_archer_merc_e",
		"units/inca/infantry_maceman_merc_a",
		"units/inca/infantry_maceman_merc_b",
		"units/inca/infantry_maceman_merc_e",
		"units/inca/infantry_maceman2_merc_a",
		"units/inca/infantry_maceman2_merc_b",
		"units/inca/infantry_maceman2_merc_e",
		"structures/inca/dock",
		"structures/inca/wonder",
		"structures/inca/military_colony"
	];
	for (const t of disabled)
		cmpPlayer.AddDisabledTemplate(t);
};

Trigger.prototype.ICSpawn = function(player, template, x, z, count, angle)
{
	const out = [];
	for (let i = 0; i < count; ++i)
	{
		const ent = Engine.AddEntity(template);
		if (!ent)
			continue;
		const cmpPos = Engine.QueryInterface(ent, IID_Position);
		const cmpOwn = Engine.QueryInterface(ent, IID_Ownership);
		if (!cmpPos)
		{
			Engine.DestroyEntity(ent);
			continue;
		}
		cmpPos.JumpTo(x + (i % 4) * 4, z + Math.floor(i / 4) * 4);
		cmpPos.SetYRotation(angle || 0);
		if (cmpOwn)
			cmpOwn.SetOwner(player);
		out.push(ent);
	}
	return out;
};

Trigger.prototype.ICAttack = function(player, x, z)
{
	const ents = TriggerHelper.GetPlayerEntitiesByClass(player, "Soldier");
	if (!ents.length)
		return;
	ProcessCommand(player, {
		"type": "attack-walk",
		"entities": ents,
		"x": x,
		"z": z,
		"targetClasses": { "attack": ["Unit", "Structure"] },
		"allowCapture": true,
		"queued": false
	});
};

Trigger.prototype.ICRetreat = function(player, x, z)
{
	const ents = TriggerHelper.GetPlayerEntitiesByClass(player, "Soldier");
	if (!ents.length)
		return;
	ProcessCommand(player, {
		"type": "walk",
		"entities": ents,
		"x": x,
		"z": z,
		"queued": false
	});
};

Trigger.prototype.ICAlive = function(uid)
{
	const cmpHealth = Engine.QueryInterface(uid, IID_Health);
	return !!cmpHealth && cmpHealth.GetHitpoints() > 0;
};

Trigger.prototype.ICOwner = function(uid)
{
	return TriggerHelper.GetOwner(uid);
};

Trigger.prototype.ICAliveOwned = function(uid, player)
{
	return this.ICAlive(uid) && this.ICOwner(uid) === player;
};

Trigger.prototype.ICCount = function(player, template)
{
	const cmpTemplateManager = Engine.QueryInterface(SYSTEM_ENTITY, IID_TemplateManager);
	let n = 0;
	for (const ent of TriggerHelper.GetEntitiesByPlayer(player))
	{
		if (cmpTemplateManager.GetCurrentTemplateName(ent) === template && this.ICAlive(ent))
			++n;
	}
	return n;
};

Trigger.prototype.ICAllHeroesDead = function(uids)
{
	return uids.every(uid => !this.ICAlive(uid) || TriggerHelper.GetOwner(uid) === 1);
};
"""


def trigger_1() -> str:
    return r"""
Trigger.prototype.InitMission1 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco, c. 1438. Los chancas han enviado mensajeros exigiendo la sumisión del Curacazgo. Viracocha Inca e Inca Urco abandonan la ciudad; Cusi Yupanqui decide quedarse y defenderla. Las unidades imperiales tardías, los barcos, la maravilla y los héroes de otras épocas están deshabilitados en esta campaña.");
	this.ICObjective(this.M1Objective());
};

Trigger.prototype.ResumeMission1 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M1Objective());
};

Trigger.prototype.M1Objective = function()
{
	if (!this.ICMarker(9004))
		return "Resiste el asalto final.";
	if (!this.ICMarker(9003))
		return "Resiste la segunda oleada.";
	if (!this.ICMarker(9002))
		return "Resiste la primera oleada.";
	return "Reúne recursos, fortifica Cusco y resiste las incursiones chancas.";
};

Trigger.prototype.Mission1Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha caído. La defensa de Cusco se desmorona.");
		return;
	}
	if (!this.ICAliveOwned(1100, 1))
	{
		this.ICLose("El centro cívico de Cusco ha caído o ha sido destruido.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9001) && t >= 8000)
	{
		this.ICConsume(9001);
		if (this.ICAlive(1001))
			Engine.DestroyEntity(1001);
		if (this.ICAlive(1002))
			Engine.DestroyEntity(1002);
		this.ICMessage("Viracocha Inca e Inca Urco han huido. Cusi Yupanqui queda al mando de la defensa. Las crónicas difieren sobre estos hechos.");
	}
	if (this.ICMarker(9002) && t >= 60000)
	{
		this.ICConsume(9002);
		this.ICMessage("Primera incursión chanca: una columna avanza desde el norte.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 820, 260, 8, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 840, 280, 4, 0);
		this.ICAttack(2, 400, 560);
	}
	if (this.ICMarker(9003) && t >= 150000)
	{
		this.ICConsume(9003);
		this.ICMessage("Segunda oleada: los chancas presionan por el este. Los aliados canas se suman a la defensa.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 760, 240, 10, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 760, 280, 5, 0);
		this.ICAttack(2, 400, 560);
		this.ICAttack(3, 820, 250);
	}
	if (this.ICMarker(9004) && t >= 240000)
	{
		this.ICConsume(9004);
		this.ICMessage("Tercera oleada: el grueso de la hueste chanca ataca Cusco.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 860, 300, 12, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 860, 340, 6, 0);
		this.ICSpawn(2, "units/chanca/infantry_spearman_b", 820, 320, 6, 0);
		this.ICAttack(2, 400, 560);
	}
	if (this.ICMarker(9005) && t >= 360000)
	{
		this.ICConsume(9005);
		if (this.ICAliveOwned(1100, 1) && this.ICAliveOwned(1000, 1))
		{
			this.ICMessage("Cusco resiste. La victoria en Yahuar Pampa aún está por venir.");
			this.ICWin("Has defendido Cusco y rechazado las incursiones chancas.");
		}
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission1", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission1", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission1Tick", { "enabled": true, "interval": 1000 });
}
"""


def trigger_2() -> str:
    return r"""
Trigger.prototype.InitMission2 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco está rodeado. La tradición recuerda la defensa de Carmenca y Chocos-Cachona. Protege el centro cívico y el santuario, y conserva con vida a Cusi Yupanqui.");
	this.ICObjective(this.M2Objective());
};

Trigger.prototype.ResumeMission2 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M2Objective());
};

Trigger.prototype.M2Objective = function()
{
	if (!this.ICMarker(9014))
		return "Resiste la oleada final.";
	if (!this.ICMarker(9013))
		return "Resiste la tercera oleada.";
	if (!this.ICMarker(9012))
		return "Resiste la segunda oleada.";
	if (!this.ICMarker(9011))
		return "Resiste la primera oleada.";
	return "Resiste las oleadas chancas y protege el centro cívico y el santuario durante 7 minutos.";
};

Trigger.prototype.Mission2Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha caído durante el asedio.");
		return;
	}
	if (!this.ICAliveOwned(1100, 1))
	{
		this.ICLose("El centro cívico de Cusco ha caído.");
		return;
	}
	if (!this.ICAliveOwned(1101, 1))
	{
		this.ICLose("El santuario de Cusco ha ca\u00eddo o ha sido destruido.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9011) && t >= 45000)
	{
		this.ICConsume(9011);
		this.ICMessage("Los chancas atacan el flanco norte.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 700, 300, 10, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 720, 330, 5, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9012) && t >= 120000)
	{
		this.ICConsume(9012);
		this.ICMessage("Segunda oleada: ataque coordinado por el sur. Astoy Huaraca dirige a los veteranos.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 700, 780, 12, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9013) && t >= 210000)
	{
		this.ICConsume(9013);
		this.ICMessage("Tercera oleada: Tomay Huaraca presiona el este. La ciudad resiste.");
		this.ICSpawn(2, "units/chanca/infantry_spearman_b", 760, 550, 8, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 760, 580, 6, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9014) && t >= 300000)
	{
		this.ICConsume(9014);
		this.ICMessage("Oleada final: Anccu Huallo lanza el asalto decisivo.");
		this.ICSpawn(2, "units/chanca/infantry_maceman_b", 760, 800, 14, 0);
		this.ICSpawn(2, "units/chanca/infantry_slinger_b", 780, 820, 7, 0);
		this.ICSpawn(2, "units/chanca/infantry_axeman_b", 740, 820, 6, 0);
		this.ICAttack(2, 450, 560);
	}
	if (this.ICMarker(9015) && t >= 420000)
	{
		this.ICConsume(9015);
		if (this.ICAliveOwned(1100, 1) && this.ICAliveOwned(1101, 1) && this.ICAliveOwned(1000, 1))
		{
			this.ICMessage("El asedio ha sido rechazado. Cusco sigue en pie.");
			this.ICWin("Has resistido el asedio chanca y salvado Cusco.");
		}
	}
};

Trigger.prototype.M2OnOwnershipChanged = function(msg)
{
	if (msg.entity === 2100 && msg.to === 1)
	{
		this.ICMessage("Has tomado el centro cívico chanca. El asedio se quiebra.");
		this.ICWin("Has contraatacado y roto el asedio chanca.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission2", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission2", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnOwnershipChanged", "M2OnOwnershipChanged", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission2Tick", { "enabled": true, "interval": 1000 });
}
"""


def trigger_3() -> str:
    return r"""
Trigger.prototype.InitMission3 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Yahuar Pampa, la pampa de sangre. Las crónicas exageran las cifras, pero coinciden en que la batalla decidió el futuro del Cusco. La leyenda de los pururaucas se contará como tradición, no como hecho comprobado.");
	this.ICObjective(this.M3Objective());
};

Trigger.prototype.ResumeMission3 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M3Objective());
};

Trigger.prototype.M3Objective = function()
{
	if (TriggerHelper.GetOwner(2000) === 1)
		return "La momia de Uscovilca está en tu poder. Elimina o captura a los capitanes chancas.";
	return "Mantén la línea, elimina o captura a los capitanes chancas y toma la momia de Uscovilca.";
};

Trigger.prototype.Mission3Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha caído en Yahuar Pampa.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9021) && t >= 30000)
	{
		this.ICConsume(9021);
		this.ICMessage("Las dos huestes avanzan. Cusi Yupanqui arenga a sus hombres.");
		this.ICAttack(2, 420, 512);
		this.ICAttack(1, 700, 512);
		this.ICAttack(3, 700, 512);
	}
	if (this.ICMarker(9022) && t >= 180000)
	{
		this.ICConsume(9022);
		this.ICMessage("Según la tradición, las piedras del campo (pururaucas) se levantaron para luchar junto a los incas. Es una leyenda recogida por las crónicas, no un hecho comprobado. Un contingente de reserva se suma al combate.");
		this.ICSpawn(1, "units/inca/infantry_spearman_b", 420, 512, 8, 0);
		this.ICAttack(1, 740, 512);
	}
	if (this.ICAllHeroesDead([2001, 2002, 2003]))
	{
		this.ICMessage("Los capitanes chancas han caído. La confederación se desmorona.");
		this.ICWin("Has ganado en Yahuar Pampa y abierto el camino al Tawantinsuyu.");
		return;
	}
	if (this.ICMarker(9023) && t >= 360000)
	{
		this.ICConsume(9023);
		this.ICMessage("La batalla continúa. Elimina o captura a los capitanes chancas para romper la confederación.");
	}
};

Trigger.prototype.M3OnOwnershipChanged = function(msg)
{
	if (msg.entity === 2000 && msg.to === 1)
	{
		this.ICMessage("Has capturado la momia de Uscovilca. La moral chanca se quiebra; según Sarmiento de Gamboa, era llevada como reliquia.");
		this.ICRetreat(2, 820, 512);
		this.ICAttack(1, 740, 512);
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission3", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission3", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnOwnershipChanged", "M3OnOwnershipChanged", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission3Tick", { "enabled": true, "interval": 1000 });
}
"""


def trigger_4() -> str:
    return r"""
Trigger.prototype.InitMission4 = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("La guerra se traslada al país chanca, hacia Andahuaylas y el Apurímac. Toma la fortaleza de altura y derrota o captura a Anccu Huallo.");
	this.ICObjective(this.M4Objective());
};

Trigger.prototype.ResumeMission4 = function()
{
	this.ICRestrictInca();
	this.ICObjective(this.M4Objective());
};

Trigger.prototype.M4Objective = function()
{
	return "Avanza hacia la fortaleza chanca y toma su centro cívico. Anccu Huallo debe ser derrotado o capturado.";
};

Trigger.prototype.Mission4Tick = function()
{
	if (this.icEnded)
		return;
	if (!this.ICAliveOwned(1000, 1))
	{
		this.ICLose("Cusi Yupanqui ha caído en territorio chanca.");
		return;
	}
	const t = this.ICTime();
	if (this.ICMarker(9031) && t >= 30000)
	{
		this.ICConsume(9031);
		this.ICMessage("El ejército inca avanza por el valle. La fortaleza chanca domina el paso.");
		this.ICAttack(1, 780, 280);
		this.ICAttack(2, 300, 760);
	}
	const centreTaken = !this.ICAlive(2100) || TriggerHelper.GetOwner(2100) === 1;
	const anccuDown = !this.ICAlive(2003) || TriggerHelper.GetOwner(2003) === 1;
	if (centreTaken && anccuDown)
	{
		this.ICMessage("La fortaleza ha caído. Los supervivientes chancas se incorporan al ejército inca, como ocurrió tras la victoria.");
		this.ICWin("Has conquistado el país chanca y consolidado el poder de Cusco.");
		return;
	}
	if (this.ICMarker(9032) && t >= 300000)
	{
		this.ICConsume(9032);
		this.ICMessage("La fortaleza sigue en pie. Toma el centro cívico y derrota o captura a Anccu Huallo.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitMission4", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeMission4", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "Mission4Tick", { "enabled": true, "interval": 1000 });
}
"""


def trigger_epilogue() -> str:
    return r"""
Trigger.prototype.InitEpilogue = function()
{
	this.icEnded = false;
	this.ICRestrictInca();
	this.ICMessage("Cusco, después de la victoria. Cusi Yupanqui asume el mando y toma el nombre de Pachacútec. La tradición lo recuerda como el iniciador del Tawantinsuyu; las crónicas no coinciden en todos los detalles.");
	this.ICObjective("Presencia la asunción de Pachacútec.");
};

Trigger.prototype.ResumeEpilogue = function()
{
	this.ICRestrictInca();
	this.ICObjective("Presencia la asunción de Pachacútec.");
};

Trigger.prototype.EpilogueTick = function()
{
	if (this.icEnded)
		return;
	if (this.ICMarker(9041) && this.ICTime() >= 18000)
	{
		this.ICConsume(9041);
		this.ICWin("Cusi Yupanqui se convierte en Pachacútec. Comienza la expansión del Tawantinsuyu.");
	}
};

{
	const cmpTrigger = Engine.QueryInterface(SYSTEM_ENTITY, IID_Trigger);
	cmpTrigger.RegisterTrigger("OnInitGame", "InitEpilogue", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnDeserialized", "ResumeEpilogue", { "enabled": true });
	cmpTrigger.RegisterTrigger("OnInterval", "EpilogueTick", { "enabled": true, "interval": 1000 });
}
"""


def escape_js_unicode(text: str) -> str:
    r"""Convierte caracteres no ASCII a escapes \uXXXX para que el motor los lea siempre bien."""
    out = []
    for ch in text:
        code = ord(ch)
        if code < 128:
            out.append(ch)
        elif code <= 0xFFFF:
            out.append("\\u%04x" % code)
        else:
            code -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF)))
    return "".join(out)


def write_triggers() -> None:
    (MAP_DIR / "inca_chanca_common.js").write_text(escape_js_unicode(COMMON_JS), encoding="utf-8")
    for name, text in (
        ("inca_chanca_01_triggers.js", trigger_1()),
        ("inca_chanca_02_triggers.js", trigger_2()),
        ("inca_chanca_03_triggers.js", trigger_3()),
        ("inca_chanca_04_triggers.js", trigger_4()),
        ("inca_chanca_05_triggers.js", trigger_epilogue()),
    ):
        (MAP_DIR / name).write_text(escape_js_unicode(text), encoding="utf-8")


def write_campaign(missions: list[Mission]) -> None:
    levels = {}
    order = []
    for m in missions:
        levels[m.key] = {
            "Name": m.name,
            "Map": f"scenarios/{m.mapname}.xml",
            "MapType": "scenario",
            "Description": m.description,
            "Preview": f"session/icons/mappreview/{m.mapname}.png",
        }
        order.append(m.key)
    for i in range(1, len(order)):
        levels[order[i]]["Requires"] = order[i - 1]
    campaign = {
        "Name": "La Guerra Inca-Chanca (c. 1438)",
        "Description": "Campaña histórica sobre el conflicto entre el Curacazgo del Cusco y la confederación chanca. Cuatro misiones y un epílogo, con notas sobre las fuentes y las incertidumbres.",
        "Image": "session/icons/mappreview/inca_chanca_campaign.png",
        "Levels": levels,
        "Order": order,
        "ShowUnavailable": False,
    }
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)
    (CAMPAIGN_DIR / "inca_chanca.json").write_text(
        json.dumps(campaign, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8")


def main() -> None:
    missions = [mission_1(), mission_2(), mission_3(), mission_4(), mission_epilogue()]
    for m in missions:
        hm = make_heightmap(m.patches, m.style, m.seed)
        tiles = assign_tiles(hm, m.patches, m.style)
        write_pmp(MAP_DIR / f"{m.mapname}.pmp", m.patches, hm, tiles)
        write_map_xml(m)
        preview_from_heightmap(hm, PREVIEW_DIR / f"{m.mapname}.png", m.preview_title)
    write_triggers()
    write_campaign(missions)
    make_campaign_image(PREVIEW_DIR / "inca_chanca_campaign.png")
    print("Campaña generada en", MOD)


if __name__ == "__main__":
    main()
