#!/usr/bin/env python3
"""
Genera la civilización chanca del mod inca-chanca a partir del mod Inca 0.28.

El arte se deriva del mod Incas 0 A.D. (CC-BY-SA 3.0) y se atribuye en CREDITS.md.
Este script es idempotente: se puede volver a ejecutar tras actualizar el mod Inca.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

MOD = Path(__file__).resolve().parents[1]
INCA = MOD.parent / "incas0ad"

UNITS = [
    "support_civilian",
    "support_civilian_house",
    "support_healer_a",
    "support_healer_b",
    "support_healer_e",
    "support_trader",
    "infantry_chaski",
    "infantry_maceman_a",
    "infantry_maceman_b",
    "infantry_maceman_e",
    "infantry_axeman_a",
    "infantry_axeman_b",
    "infantry_axeman_e",
    "infantry_spearman_a",
    "infantry_spearman_b",
    "infantry_spearman_e",
    "infantry_slinger_a",
    "infantry_slinger_b",
    "infantry_slinger_e",
    "infantry_javelineer_a",
    "infantry_javelineer_b",
    "infantry_javelineer_e",
]

STRUCTURES = [
    "civil_centre",
    "house",
    "barracks",
    "farmstead",
    "field",
    "storehouse",
    "market",
    "temple",
    "forge",
    "corral",
    "defense_tower",
    "sentry_tower",
    "outpost",
    "fortress",
    "wall_gate",
    "wall_long",
    "wall_medium",
    "wall_short",
    "wall_tower",
    "wallset_stone",
    "kancha",
    "military_colony",
]

CHANCA_BUILDER = """<Builder>
    <Entities datatype="tokens" replace="">
      structures/chanca/civil_centre
      structures/chanca/house
      structures/chanca/storehouse
      structures/chanca/farmstead
      structures/chanca/field
      structures/chanca/barracks
      structures/chanca/forge
      structures/chanca/temple
      structures/chanca/market
      structures/chanca/outpost
      structures/chanca/sentry_tower
      structures/chanca/defense_tower
      structures/chanca/fortress
      structures/chanca/military_colony
      structures/chanca/kancha
      structures/chanca/wallset_stone
      structures/wallset_palisade
    </Entities>
  </Builder>"""

UNIT_NAMES = {
    "support_civilian": ("Campesinos chancas", "Chanka runa"),
    "support_civilian_house": ("Campesinos chancas", "Chanka runa"),
    "support_healer": ("Curandero chanca", "Hampiq"),
    "support_trader": ("Comerciante chanca", "Qhatuq"),
    "infantry_chaski": ("Corredor chanca", "Chaski"),
    "infantry_maceman": ("Guerrero chanca con macana", "Chanka macana"),
    "infantry_axeman": ("Guerrero chanca con hacha", "Chanka champi"),
    "infantry_spearman": ("Lancero chanca", "Chanka chuqui"),
    "infantry_slinger": ("Hondero chanca", "Chanka huaraca"),
    "infantry_javelineer": ("Jabalínero chanca", "Chanka antañauichi"),
    "champion_infantry": ("Guerrero de élite chanca", "Chanka awqa"),
}

UNIT_ICONS = {
    "support_civilian": "units/chanca_female.png",
    "support_civilian_house": "units/chanca_female.png",
    "support_healer": "units/chanca_support_healer.png",
    "support_trader": "units/chanca_trader.png",
    "infantry_chaski": "units/chanca_chaski.png",
    "infantry_maceman": "units/chanca_maceman.png",
    "infantry_axeman": "units/chanca_axeman.png",
    "infantry_spearman": "units/chanca_spearman.png",
    "infantry_slinger": "units/chanca_slinger.png",
    "infantry_javelineer": "units/chanca_javelinist.png",
    "champion_infantry": "units/chanca_champ_1.png",
}

STRUCTURE_NAMES = {
    "civil_centre": ("Centro cívico chanca", "Marka wasi"),
    "house": ("Casa chanca", "Wasi"),
    "barracks": ("Cuartel chanca", "Awqa wasi"),
    "farmstead": ("Granja chanca", "Chakra wasi"),
    "field": ("Campo de cultivo", "Chakra"),
    "storehouse": ("Almacén chanca", "Qollqa"),
    "market": ("Mercado chanca", "Qhatu"),
    "temple": ("Santuario chanca", "Waka"),
    "forge": ("Herrería chanca", "Rumiwasi"),
    "corral": ("Corral chanca", "Kancha"),
    "defense_tower": ("Torre defensiva chanca", "Pukara"),
    "sentry_tower": ("Atalaya chanca", "Pukara"),
    "outpost": ("Puesto avanzado chanca", "Pukara"),
    "fortress": ("Fortaleza chanca", "Pukara"),
    "wall_gate": ("Puerta de muralla chanca", "Qincha"),
    "wall_long": ("Muralla chanca", "Qincha"),
    "wall_medium": ("Muralla chanca", "Qincha"),
    "wall_short": ("Muralla chanca", "Qincha"),
    "wall_tower": ("Torre de muralla chanca", "Pukara"),
    "wallset_stone": ("Muralla de piedra chanca", "Qincha"),
    "kancha": ("Kancha chanca", "Kancha"),
    "military_colony": ("Colonia militar chanca", "Marka"),
}

TINT_UNIT = (0.62, 0.20, 0.12)
TINT_STRUCT = (0.42, 0.34, 0.26)
TINT_ICON = (0.72, 0.18, 0.10)


def find_public_zip() -> Path | None:
    env = os.environ.get("PYROGENESIS_PUBLIC_ZIP") or os.environ.get("0AD_PUBLIC_ZIP")
    if env and Path(env).is_file():
        return Path(env)
    candidates = [
        Path("/snap/0ad/current/binaries/data/mods/public/public.zip"),
        Path("/snap/0ad/748/binaries/data/mods/public/public.zip"),
        Path("/usr/share/0ad/data/mods/public/public.zip"),
        Path("/usr/local/share/0ad/data/mods/public/public.zip"),
        Path.home()/"snap/0ad/current/binaries/data/mods/public/public.zip",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    for root in (Path("/snap/0ad"), Path.home()/"snap/0ad"):
        for candidate in root.glob("*/binaries/data/mods/public/public.zip"):
            return candidate
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_tag(text: str, tag: str, value: str) -> str:
    if re.search(rf"<{tag}>.*?</{tag}>", text, flags=re.S):
        return re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}>{value}</{tag}>", text, count=1, flags=re.S)
    return text


def replace_or_insert_identity(text: str, tag: str, value: str) -> str:
    if re.search(rf"<{tag}>.*?</{tag}>", text, flags=re.S):
        return replace_tag(text, tag, value)
    # insert after <Identity>
    return text.replace("<Identity>", f"<Identity>\n    <{tag}>{value}</{tag}>", 1)


def transform_unit_template(text: str, base: str) -> str:
    text = text.replace("units/inca/", "units/chanca/")
    text = text.replace("units/inca_", "units/chanca_")
    text = text.replace("units/incas/", "units/chancas/")
    text = text.replace("structures/inca/", "structures/chanca/")
    text = text.replace("<Civ>inca</Civ>", "<Civ>chanca</Civ>")
    text = text.replace("<Lang>quechua</Lang>", "<Lang>quechua</Lang>")
    # La campaña no llega a fase ciudad; el jabalinero queda disponible en fase villa.
    text = text.replace("<Techs datatype=\"tokens\">phase_city</Techs>", "<Techs datatype=\"tokens\">phase_town</Techs>")
    if base in UNIT_NAMES:
        generic, specific = UNIT_NAMES[base]
        text = replace_or_insert_identity(text, "GenericName", generic)
        text = replace_or_insert_identity(text, "SpecificName", specific)
        text = replace_or_insert_identity(text, "Icon", UNIT_ICONS[base])
    return text


def transform_structure_template(text: str, base: str) -> str:
    text = text.replace("structures/inca/", "structures/chanca/")
    text = text.replace("structures/incas/", "structures/chancas/")
    text = text.replace("units/inca/", "units/chanca/")
    text = text.replace("units/incas/", "units/chancas/")
    text = text.replace("<Civ>inca</Civ>", "<Civ>chanca</Civ>")
    text = text.replace("Train incas citizen-soldiers. Research improvements for Inca units.",
                        "Entrena infantería ciudadana chanca. Investiga mejoras para las unidades chancas.")
    text = text.replace("Special house for the Inca civilization, used for training civilians and basic military units.",
                        "Casa comunal chanca, usada para entrenar civiles y unidades militares básicas.")
    text = text.replace("Military colony for the Inca civilization, used for training advanced military units.",
                        "Colonia militar chanca, usada para entrenar unidades militares avanzadas.")
    if base in STRUCTURE_NAMES:
        generic, specific = STRUCTURE_NAMES[base]
        text = replace_or_insert_identity(text, "GenericName", generic)
        text = replace_or_insert_identity(text, "SpecificName", specific)
    return text


def transform_actor(text: str) -> str:
    # Rutas de actores (no tocar mallas: las mallas siguen siendo las del mod Inca).
    text = text.replace("units/incas/", "units/chancas/")
    text = text.replace("structures/incas/", "structures/chancas/")
    text = text.replace("props/units/heads/head_inca", "props/units/heads/head_chanca")
    text = text.replace("props/units/helmets/inca_", "props/units/helmets/chanca_")
    text = text.replace("props/units/shields/inca_", "props/units/shields/chanca_")
    text = text.replace("props/units/weapons/inca_", "props/units/weapons/chanca_")
    text = text.replace("props/structures/inca_st", "props/structures/chanca_st")
    text = text.replace("props/special/common/garrison_flag_inca", "props/special/common/garrison_flag_chanca")
    # Corregir erratas del mod Inca
    text = text.replace(".dae.dae", ".dae")
    text = text.replace("structural/ao/inca_tower_stone_ao.png", "structural/ao/inca_stone_tower_ao.png")

    def fix_texture(match):
        path = match.group(2)
        path = path.replace("skeletal/inca_", "skeletal/chanca_")
        path = path.replace("skeletal/slinger_", "skeletal/chanca_slinger_")
        path = path.replace("structural/inca_", "structural/chanca_")
        path = path.replace("props/garrison_flag_inca", "props/garrison_flag_chanca")
        path = path.replace("props/head/inca_", "props/head/chanca_")
        path = path.replace("props/shield/inca_", "props/shield/chanca_")
        path = path.replace("props/helmet/inca_", "props/helmet/chanca_")
        return match.group(1) + path + match.group(3)

    return re.sub(r'(<texture\\s+file=")([^"]+)(")', fix_texture, text)

def tint_image(src: Path, dst: Path, tint: tuple[float, float, float], strength: float, desaturate: float = 0.0, bright: float = 1.0) -> None:
    im = Image.open(src).convert("RGBA")
    if desaturate:
        im = ImageEnhance.Color(im).enhance(max(0.0, 1.0 - desaturate))
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
    arr = np.asarray(im).astype(np.float32) / 255.0
    rgb = arr[..., :3]
    alpha = arr[..., 3:4]
    lum = (rgb[..., 0:1] * 0.299 + rgb[..., 1:2] * 0.587 + rgb[..., 2:3] * 0.114)
    tint_arr = np.array(tint, dtype=np.float32).reshape(1, 1, 3)
    out = rgb * (1.0 - strength) + tint_arr * strength * 0.85 + lum * strength * 0.15
    out = np.clip(out, 0.0, 1.0)
    result = np.concatenate([out, alpha], axis=-1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((result * 255).astype(np.uint8), "RGBA").save(dst)


def generate_textures() -> None:
    src_root = INCA / "art/textures/skins"
    dst_root = MOD / "art/textures/skins"
    for src in src_root.rglob("*"):
        if not src.is_file() or src.suffix.lower() != ".png":
            continue
        name = src.name
        rel = src.relative_to(src_root)
        if "inca" not in name and "slinger" not in name:
            continue
        new_name = name.replace("inca_", "chanca_").replace("slinger_", "chanca_slinger_")
        if "inca" in new_name:
            new_name = new_name.replace("inca", "chanca")
        dst = dst_root / rel.with_name(new_name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if "_norm" in name or "_spec" in name:
            shutil.copyfile(src, dst)
            continue
        is_struct = "structural" in rel.parts
        tint = TINT_STRUCT if is_struct else TINT_UNIT
        tint_image(src, dst, tint, 0.22 if is_struct else 0.18, 0.25 if is_struct else 0.0, 0.92 if is_struct else 1.0)

    # Catafalco/reliquia: el PNG fuente no está en el mod Inca, sino cacheado en public.
    import io
    import zipfile
    public_zip = find_public_zip()
    if public_zip and public_zip.exists():
        z = zipfile.ZipFile(public_zip)
        for name in ("catafalque.png", "catafalque_spec.png", "catafalque_norm.png"):
            key = "art/textures/skins/props/" + name + ".cached.dds"
            if key in z.namelist():
                im = Image.open(io.BytesIO(z.read(key))).convert("RGBA")
                dst = dst_root / "props" / ("chanca_" + name)
                dst.parent.mkdir(parents=True, exist_ok=True)
                arr = np.asarray(im).astype(np.float32) / 255.0
                rgb = arr[..., :3]
                alpha = arr[..., 3:4]
                tint = np.array(TINT_STRUCT, dtype=np.float32).reshape(1, 1, 3)
                out = np.clip(rgb * 0.78 + tint * 0.18, 0.0, 1.0)
                Image.fromarray((np.concatenate([out, alpha], axis=-1) * 255).astype(np.uint8), "RGBA").save(dst)

def generate_portraits() -> None:
    src_root = INCA / "art/textures/ui/session/portraits/units"
    dst_root = MOD / "art/textures/ui/session/portraits/units"
    for src in src_root.glob("inca_*.png"):
        dst = dst_root / ("chanca_" + src.name[5:])
        tint_image(src, dst, TINT_ICON, 0.25, 0.0, 0.95)
    # Iconos públicos que el mod Inca no incluye como PNG
    import io
    import zipfile
    public_zip = find_public_zip()
    if public_zip and public_zip.exists():
        z = zipfile.ZipFile(public_zip)
        for key, dst_name in (
            ("art/textures/ui/session/portraits/units/iber/support_trader.png.cached.dds", "chanca_trader.png"),
            ("art/textures/ui/session/portraits/units/catafalque.png.cached.dds", "chanca_relic.png"),
        ):
            if key in z.namelist():
                im = Image.open(io.BytesIO(z.read(key))).convert("RGBA")
                arr = np.asarray(im).astype(np.float32) / 255.0
                rgb = arr[..., :3]
                alpha = arr[..., 3:4]
                tint = np.array(TINT_ICON, dtype=np.float32).reshape(1, 1, 3)
                out = np.clip(rgb * 0.7 + tint * 0.22, 0.0, 1.0)
                dst = dst_root / dst_name
                dst.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray((np.concatenate([out, alpha], axis=-1) * 255).astype(np.uint8), "RGBA").save(dst)
    # Arquero chanca
    archer_src = src_root / "inca_merc_2.png"
    if archer_src.exists():
        tint_image(archer_src, dst_root / "chanca_archer.png", TINT_ICON, 0.25)

def generate_ui_assets() -> None:
    src = INCA / "art/textures/ui/session/icons/bkg/background_circle_inca.png"
    if src.exists():
        im = Image.open(src).convert("RGBA")
        for rel in ("art/textures/ui/session/civ_minimap",
                    "art/textures/ui/session/icons/bkg"):
            dst = MOD / rel
            dst.mkdir(parents=True, exist_ok=True)
            im.save(dst / "background_circle_inca.png")
            arr = np.asarray(im).astype(np.float32) / 255.0
            rgb = arr[..., :3]
            alpha = arr[..., 3:4]
            tint = np.array(TINT_ICON, dtype=np.float32).reshape(1, 1, 3)
            out = np.clip(rgb * 0.7 + tint * 0.22, 0.0, 1.0)
            Image.fromarray((np.concatenate([out, alpha], axis=-1) * 255).astype(np.uint8), "RGBA").save(dst / "background_circle_chanca.png")
    src = INCA / "art/textures/ui/session/portraits/emblems/m_inca.png"
    if src.exists():
        dst = MOD / "art/textures/ui/session/portraits/emblems"
        dst.mkdir(parents=True, exist_ok=True)
        im = Image.open(src).convert("RGBA")
        im.save(dst / "m_inca.png")
        arr = np.asarray(im).astype(np.float32) / 255.0
        rgb = arr[..., :3]
        alpha = arr[..., 3:4]
        tint = np.array(TINT_ICON, dtype=np.float32).reshape(1, 1, 3)
        out = np.clip(rgb * 0.7 + tint * 0.22, 0.0, 1.0)
        Image.fromarray((np.concatenate([out, alpha], axis=-1) * 255).astype(np.uint8), "RGBA").save(dst / "m_chanca.png")


def make_emblem() -> None:
    size = 512
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Fondo circular
    d.ellipse((36, 36, size - 36, size - 36), fill=(72, 26, 18, 255), outline=(220, 170, 70, 255), width=10)
    # Motivo escalonado (cruz andina estilizada)
    cx, cy = size // 2, size // 2
    gold = (232, 184, 92, 255)
    red = (170, 52, 32, 255)
    step = 54
    for i, (w, h) in enumerate([(330, 60), (250, 60), (170, 60), (90, 60)]):
        y = cy - 132 + i * 66
        d.rectangle((cx - w // 2, y, cx + w // 2, y + h), fill=gold if i % 2 == 0 else red)
    d.rectangle((cx - 34, cy - 190, cx + 34, cy + 190), fill=gold)
    d.rectangle((cx - 190, cy - 34, cx + 190, cy + 34), fill=gold)
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(40, 14, 10, 255), outline=gold, width=6)
    im.save(MOD / "art/textures/ui/session/portraits/emblems/emblem_chanca.png")


def copy_templates() -> None:
    for base in UNITS:
        src = INCA / "simulation/templates/units/inca" / f"{base}.xml"
        if not src.exists():
            print("Falta unidad inca:", base)
            continue
        text = transform_unit_template(read_text(src), re.sub(r"_[abe]$", "", base))
        write_text(MOD / "simulation/templates/units/chanca" / f"{base}.xml", text)

    # El aldeano chanca debe poder construir solo estructuras chancas existentes.
    civ_template = MOD / "simulation/templates/units/chanca/support_civilian.xml"
    if civ_template.exists():
        text = read_text(civ_template)
        text = re.sub(r"<Builder>.*?</Builder>", CHANCA_BUILDER, text, count=1, flags=re.S)
        write_text(civ_template, text)

    # Arquero chanca: se crea a partir de la plantilla de arquero mercenario inca.
    archer_src = INCA / "simulation/templates/units/inca/infantry_archer_merc_b.xml"
    if archer_src.exists():
        text = transform_unit_template(read_text(archer_src), "infantry_archer")
        text = re.sub(r"\s*<Cost>.*?</Cost>", "", text, count=1, flags=re.S)
        text = text.replace("units/chanca_infantry_archer_merc_b", "units/chanca/infantry_archer_b")
        text = text.replace("units/chanca/infantry_archer_merc_a", "units/chanca/infantry_archer_a")
        text = text.replace("units/chancas/infantry_merc_archer_b", "units/chancas/infantry_archer_b")
        text = text.replace("    <VisibleClasses datatype=\"tokens\">CitizenSoldier</VisibleClasses>\n", "")
        text = text.replace("Ashaninka Archer", "Arquero chanca")
        text = text.replace("Wisa Ashaninka", "Chanka arco")
        text = text.replace("units/chanca_merc_2.png", "units/chanca_archer.png")
        write_text(MOD / "simulation/templates/units/chanca/infantry_archer_b.xml", text)
        for rank, parent in (("a", "b"), ("e", "a")):
            rank_text = f"""<?xml version="1.0" encoding="utf-8"?>
<Entity parent="units/chanca/infantry_archer_{parent}">
  <Identity>
    <Rank>{'Advanced' if rank == 'a' else 'Elite'}</Rank>
  </Identity>
  {f'<Promotion><Entity>units/chanca/infantry_archer_e</Entity></Promotion>' if rank == 'a' else '<Promotion disable=""/>'}
  <VisualActor>
    <Actor>units/chancas/infantry_archer_{rank}.xml</Actor>
  </VisualActor>
</Entity>
"""
            write_text(MOD / "simulation/templates/units/chanca" / f"infantry_archer_{rank}.xml", rank_text)
        # Actor de arquero
        actor_src = INCA / "art/actors/units/incas/infantry_merc_archer_b.xml"
        if actor_src.exists():
            write_text(MOD / "art/actors/units/chancas/infantry_archer_b.xml", transform_actor(read_text(actor_src)))
        for rank in ("a", "e"):
            src = INCA / f"art/actors/units/incas/infantry_merc_archer_{rank}.xml"
            if src.exists():
                write_text(MOD / "art/actors/units/chancas" / f"infantry_archer_{rank}.xml", transform_actor(read_text(src)))

    for base in STRUCTURES:
        src = INCA / "simulation/templates/structures/inca" / f"{base}.xml"
        if not src.exists():
            print("Falta estructura inca:", base)
            continue
        text = transform_structure_template(read_text(src), base)
        write_text(MOD / "simulation/templates/structures/chanca" / f"{base}.xml", text)

    # El corral chanca no entrena llamas: el mod Inca referencia una plantilla inexistente.
    corral = MOD / "simulation/templates/structures/chanca/corral.xml"
    if corral.exists():
        text = read_text(corral)
        text = re.sub(r"\s*<Trainer>.*?</Trainer>", "", text, count=1, flags=re.S)
        write_text(corral, text)

    # Ajustes de entrenamiento/tecnologías
    cc = MOD / "simulation/templates/structures/chanca/civil_centre.xml"
    if cc.exists():
        text = read_text(cc)
        trainer = """<Trainer>
    <Entities datatype="tokens">
      units/{civ}/support_civilian
      units/{civ}/support_healer_b
      units/{civ}/infantry_maceman_b
      units/{civ}/infantry_slinger_b
      units/{civ}/infantry_spearman_b
      units/{civ}/infantry_chaski
      units/{civ}/hero_astoy_huaraca
      units/{civ}/hero_tomay_huaraca
      units/{civ}/hero_ancu_huallo
    </Entities>
  </Trainer>"""
        researcher = """<Researcher>
    <Technologies datatype="tokens">
      chanca/confederation
      chanca/macana
      chanca/huaraca
    </Technologies>
  </Researcher>"""
        if "<Trainer>" in text:
            text = re.sub(r"<Trainer>.*?</Trainer>", trainer, text, count=1, flags=re.S)
        else:
            text = text.replace("<VisualActor>", trainer + "\n  <VisualActor>")
        if "<Researcher>" in text:
            text = re.sub(r"<Researcher>.*?</Researcher>", researcher, text, count=1, flags=re.S)
        else:
            text = text.replace("<VisualActor>", researcher + "\n  <VisualActor>")
        write_text(cc, text)

    barracks = MOD / "simulation/templates/structures/chanca/barracks.xml"
    if barracks.exists():
        text = read_text(barracks)
        trainer = """<Trainer>
    <Entities datatype="tokens">
      units/{civ}/infantry_maceman_b
      units/{civ}/infantry_axeman_b
      units/{civ}/infantry_spearman_b
      units/{civ}/infantry_slinger_b
      units/{civ}/infantry_javelineer_b
      units/{civ}/infantry_archer_b
      units/{civ}/infantry_chaski
    </Entities>
  </Trainer>"""
        researcher = """<Researcher>
    <Technologies datatype="tokens">
      chanca/macana
      chanca/huaraca
    </Technologies>
  </Researcher>"""
        if "<Trainer>" in text:
            text = re.sub(r"<Trainer>.*?</Trainer>", trainer, text, count=1, flags=re.S)
        else:
            text = text.replace("<VisualActor>", trainer + "\n  <VisualActor>")
        if "<Researcher>" in text:
            text = re.sub(r"<Researcher>.*?</Researcher>", researcher, text, count=1, flags=re.S)
        else:
            text = text.replace("<VisualActor>", researcher + "\n  <VisualActor>")
        write_text(barracks, text)

    fortress = MOD / "simulation/templates/structures/chanca/fortress.xml"
    if fortress.exists():
        text = read_text(fortress)
        trainer = """<Trainer>
    <Entities datatype="tokens">
      units/{civ}/champion_infantry
      units/{civ}/hero_astoy_huaraca
      units/{civ}/hero_tomay_huaraca
      units/{civ}/hero_ancu_huallo
    </Entities>
  </Trainer>"""
        if "<Trainer>" in text:
            text = re.sub(r"<Trainer>.*?</Trainer>", trainer, text, count=1, flags=re.S)
        else:
            text = text.replace("<VisualActor>", trainer + "\n  <VisualActor>")
        write_text(fortress, text)

    temple = MOD / "simulation/templates/structures/chanca/temple.xml"
    if temple.exists():
        text = read_text(temple)
        text = text.replace("units/{civ}/support_acclas", "units/{civ}/support_healer_b")
        write_text(temple, text)


def copy_actors() -> None:
    # Actores de unidades
    src = INCA / "art/actors/units/incas"
    dst = MOD / "art/actors/units/chancas"
    for p in src.glob("*.xml"):
        if any(x in p.name for x in ("bireme", "ship_", "fishing_boat", "merchant_ship", "siege_ram", "operator_")):
            continue
        write_text(dst / p.name, transform_actor(read_text(p)))
    # Actores de estructuras
    src = INCA / "art/actors/structures/incas"
    dst = MOD / "art/actors/structures/chancas"
    for p in src.glob("*.xml"):
        if any(x in p.name for x in ("bireme", "fishing_boat", "merchant_ship", "siege_ram")):
            continue
        write_text(dst / p.name, transform_actor(read_text(p)))
    # Props incas específicos
    for sub in ("heads", "helmets", "shields", "weapons"):
        src = INCA / "art/actors/props/units" / sub
        dst = MOD / "art/actors/props/units" / sub
        if not src.exists():
            continue
        for p in src.glob("*.xml"):
            if "inca" not in p.name:
                continue
            new_name = p.name.replace("inca_", "chanca_")
            write_text(dst / new_name, transform_actor(read_text(p)))
    # Props de estructuras y bandera
    for rel in ("props/structures/inca_st.xml", "props/special/common/garrison_flag_inca.xml"):
        p = INCA / "art" / "actors" / rel
        if p.exists():
            new_rel = rel.replace("inca", "chanca")
            write_text(MOD / "art/actors" / new_rel, transform_actor(read_text(p)))


def make_lliclla_texture(path: Path, palette: tuple[tuple[int, int, int], ...]) -> None:
    from PIL import ImageDraw
    im = Image.new("RGBA", (512, 512), palette[0] + (255,))
    d = ImageDraw.Draw(im)
    # Bandas horizontales y motivos escalonados inspirados en textiles andinos.
    for y in range(0, 512, 64):
        d.rectangle((0, y, 511, y + 31), fill=palette[1] + (255,))
        d.rectangle((0, y + 32, 511, y + 39), fill=palette[2] + (255,))
        for x in range(-32, 512, 64):
            d.polygon([(x, y + 12), (x + 16, y), (x + 32, y + 12), (x + 16, y + 24)], fill=palette[3] + (255,))
    for x in range(0, 512, 128):
        d.rectangle((x, 0, x + 6, 511), fill=palette[2] + (255,))
    im.save(path)


def make_worker_actors() -> None:
    cape_dir = MOD / "art/actors/props/units/capes"
    cape_dir.mkdir(parents=True, exist_ok=True)
    skin_dir = MOD / "art/textures/skins/props"
    skin_dir.mkdir(parents=True, exist_ok=True)
    make_lliclla_texture(skin_dir / "lliclla_inca.png", ((92, 34, 24), (170, 62, 38), (226, 176, 84), (38, 18, 14)))
    make_lliclla_texture(skin_dir / "lliclla_chanca.png", ((78, 28, 18), (146, 54, 30), (210, 150, 60), (32, 14, 10)))
    for civ in ("inca", "chanca"):
        cape = f"""<?xml version="1.0" encoding="utf-8"?>
<actor version="1">
  <castshadow/>
  <group>
    <variant frequency="1" name="Base">
      <mesh>props/new/capes/cape_hd_medium.dae</mesh>
      <textures>
        <texture file="props/lliclla_{civ}.png" name="baseTex"/>
        <texture file="default_norm.png" name="normTex"/>
        <texture file="null_black.dds" name="specTex"/>
      </textures>
    </variant>
  </group>
  <material>no_trans_norm_spec.xml</material>
</actor>
"""
        write_text(cape_dir / f"lliclla_{civ}.xml", cape)

    def male(civ: str) -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<actor version="1">
  <castshadow/>
  <group>
    <variant frequency="1" name="Base">
      <mesh>skeletal/new/m_tunic_short.dae</mesh>
      <props>
        <prop actor="props/units/heads/head_{civ}_basic.xml" attachpoint="head"/>
        <prop actor="props/units/helmets/{civ}_b.xml" attachpoint="helmet"/>
      </props>
      <textures>
        <texture file="default_norm.png" name="normTex"/>
        <texture file="null_black.dds" name="specTex"/>
      </textures>
    </variant>
  </group>
  <group>
    <variant frequency="1" name="1">
      <textures>
        <texture file="skeletal/{civ}_w_b_2.png" name="baseTex"/>
      </textures>
    </variant>
    <variant frequency="1" name="2">
      <textures>
        <texture file="skeletal/{civ}_w_b_3.png" name="baseTex"/>
      </textures>
    </variant>
  </group>
  <group>
    <variant file="biped/base_peasant_male.xml"/>
    <variant file="biped/carry_food.xml"/>
    <variant file="biped/carry_meat.xml"/>
    <variant file="biped/carry_wood.xml"/>
    <variant file="biped/carry_stone.xml"/>
    <variant file="biped/carry_metal.xml"/>
    <variant file="biped/approach_tree.xml"/>
    <variant file="biped/approach_grain.xml"/>
    <variant file="biped/approach_fruit.xml"/>
    <variant file="biped/approach_meat.xml"/>
    <variant file="biped/approach_rock.xml"/>
    <variant file="biped/approach_ore.xml"/>
    <variant file="biped/approach_ruins.xml"/>
    <variant file="biped/approach_praise.xml"/>
  </group>
  <group>
    <variant frequency="1" name="Idle"/>
    <variant file="biped/attack_capture.xml"/>
    <variant file="biped/attack_melee_female.xml"/>
    <variant file="biped/attack_slaughter.xml"/>
    <variant file="biped/gather_tree.xml"/>
    <variant file="biped/gather_grain.xml"/>
    <variant file="biped/gather_fruit.xml"/>
    <variant file="biped/gather_meat.xml"/>
    <variant file="biped/gather_rock.xml"/>
    <variant file="biped/gather_ore.xml"/>
    <variant file="biped/gather_ruins.xml"/>
    <variant file="biped/gather_praise.xml"/>
    <variant file="biped/build.xml"/>
    <variant file="biped/build_farm.xml"/>
    <variant file="biped/death_infantry.xml"/>
  </group>
  <material>player_trans_norm_spec.xml</material>
</actor>
"""

    def female(civ: str) -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<actor version="1">
  <castshadow/>
  <group>
    <variant frequency="1" name="h_1">
      <props>
        <prop actor="props/units/heads/head_{civ}_f.xml" attachpoint="head"/>
        <prop actor="props/units/helmets/{civ}_b.xml" attachpoint="helmet"/>
        <prop actor="props/units/capes/lliclla_{civ}.xml" attachpoint="root"/>
      </props>
    </variant>
    <variant frequency="1" name="h_2">
      <props>
        <prop actor="props/units/heads/head_{civ}_f.xml" attachpoint="head"/>
        <prop actor="props/units/helmets/{civ}_f.xml" attachpoint="helmet"/>
        <prop actor="props/units/capes/lliclla_{civ}.xml" attachpoint="root"/>
      </props>
    </variant>
  </group>
  <group>
    <variant frequency="1" name="Skirt-Long_a">
      <mesh>skeletal/new/f_dress.dae</mesh>
      <textures>
        <texture file="skeletal/{civ}_f_1.png" name="baseTex"/>
        <texture file="default_norm.png" name="normTex"/>
        <texture file="null_black.dds" name="specTex"/>
      </textures>
    </variant>
    <variant frequency="1" name="Skirt-Long_b">
      <mesh>skeletal/new/f_dress.dae</mesh>
      <textures>
        <texture file="skeletal/{civ}_f_2.png" name="baseTex"/>
        <texture file="default_norm.png" name="normTex"/>
        <texture file="null_black.dds" name="specTex"/>
      </textures>
    </variant>
  </group>
  <group>
    <variant file="biped/female_base_walk.xml"/>
    <variant file="biped/female_carry_food.xml"/>
    <variant file="biped/female_carry_meat.xml"/>
    <variant file="biped/female_carry_wood.xml"/>
    <variant file="biped/female_carry_stone.xml"/>
    <variant file="biped/female_carry_metal.xml"/>
  </group>
  <group>
    <variant name="Idle" frequency="1"/>
    <variant file="biped/attack_melee_female.xml"/>
    <variant file="biped/attack_slaughter.xml"/>
    <variant file="biped/female_death.xml"/>
    <variant file="biped/female_gather_tree.xml"/>
    <variant file="biped/female_gather_grain.xml"/>
    <variant file="biped/female_gather_fruit.xml"/>
    <variant file="biped/female_gather_meat.xml"/>
    <variant file="biped/female_gather_rock.xml"/>
    <variant file="biped/female_gather_ore.xml"/>
    <variant file="biped/female_gather_ruins.xml"/>
    <variant file="biped/gather_praise.xml"/>
    <variant file="biped/female_build.xml"/>
    <variant file="biped/female_build_farm.xml"/>
  </group>
  <material>player_trans_norm_spec.xml</material>
</actor>
"""
    for civ in ("inca", "chanca"):
        out = MOD / "art/actors/units" / ("incas" if civ == "inca" else "chancas")
        write_text(out / "citizen_male.xml", male(civ))
        write_text(out / "citizen_female.xml", female(civ))


def make_hero_actors() -> None:
    # Astoy Huaraca: hacha
    text = transform_actor(read_text(INCA / "art/actors/units/incas/infantry_hero_pachacutec.xml"))
    write_text(MOD / "art/actors/units/chancas/hero_astoy_huaraca.xml", text)
    # Tomay Huaraca: lanza
    text = transform_actor(read_text(INCA / "art/actors/units/incas/infantry_hero_capac_yupanqui.xml"))
    write_text(MOD / "art/actors/units/chancas/hero_tomay_huaraca.xml", text)
    # Anccu Huallo: macana
    text = transform_actor(read_text(INCA / "art/actors/units/incas/infantry_hero_pachacutec.xml"))
    text = text.replace("props/units/weapons/chanca_axe_gold.xml", "props/units/weapons/chanca_mace.xml")
    write_text(MOD / "art/actors/units/chancas/hero_ancu_huallo.xml", text)
    # Reliquia: litera/momia. Se usa el catafalco sin caballo, con textura chanca.
    relic = """<?xml version="1.0" encoding="utf-8"?>
<actor version="1">
  <castshadow/>
  <group>
    <variant frequency="1" name="relic">
      <mesh>props/special/catafalque_two_wheel.dae</mesh>
      <textures>
        <texture file="props/chanca_catafalque.png" name="baseTex"/>
        <texture file="props/chanca_catafalque_spec.png" name="specTex"/>
        <texture file="props/chanca_catafalque_norm.png" name="normTex"/>
      </textures>
    </variant>
  </group>
  <material>player_trans_parallax_spec.xml</material>
</actor>
"""
    write_text(MOD / "art/actors/units/chancas/relic_uscovilca.xml", relic)


def make_hero_templates() -> None:
    def hero(name, parent, aura, icon, actor):
        return f"""<?xml version="1.0" encoding="utf-8"?>
<Entity parent="{parent}">
  <Auras datatype="tokens">{aura}</Auras>
  <Capturable>
    <CapturePoints>150</CapturePoints>
    <GarrisonRegenRate>0</GarrisonRegenRate>
    <RegenRate>5</RegenRate>
  </Capturable>
  <Identity>
    <Civ>chanca</Civ>
    <GenericName>{name}</GenericName>
    <SpecificName>{name}</SpecificName>
    <Icon>{icon}</Icon>
  </Identity>
  <VisualActor>
    <Actor>{actor}</Actor>
  </VisualActor>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/chanca/hero_astoy_huaraca.xml",
               hero("Astoy Huaraca", "template_unit_hero_infantry_axeman",
                    "units/heroes/chanca_hero_astoy_huaraca", "units/chanca_hero_1.png",
                    "units/chancas/hero_astoy_huaraca.xml"))
    write_text(MOD / "simulation/templates/units/chanca/hero_tomay_huaraca.xml",
               hero("Tomay Huaraca", "template_unit_hero_infantry_spearman",
                    "units/heroes/chanca_hero_tomay_huaraca", "units/chanca_hero_2.png",
                    "units/chancas/hero_tomay_huaraca.xml"))
    write_text(MOD / "simulation/templates/units/chanca/hero_ancu_huallo.xml",
               hero("Anccu Huallo", "template_unit_hero_infantry_axeman",
                    "units/heroes/chanca_hero_ancu_huallo", "units/chanca_hero_3.png",
                    "units/chancas/hero_ancu_huallo.xml"))

    relic = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_unit_catafalque">
  <Auras datatype="tokens">units/heroes/chanca_relic_uscovilca</Auras>
  <Capturable>
    <CapturePoints>600</CapturePoints>
    <RegenRate>5</RegenRate>
  </Capturable>
  <Identity>
    <Civ>chanca</Civ>
    <GenericName>Momia de Uscovilca</GenericName>
    <SpecificName>Uscovilca</SpecificName>
    <Icon>units/chanca_relic.png</Icon>
    <Tooltip>Reliquia sagrada de la confederación chanca. Capturarla quiebra su moral.</Tooltip>
  </Identity>
  <VisualActor>
    <Actor>units/chancas/relic_uscovilca.xml</Actor>
  </VisualActor>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/chanca/relic_uscovilca.xml", relic)

    champion = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_unit_champion_infantry_axeman">
  <Identity>
    <Civ>chanca</Civ>
    <GenericName>Guerrero de élite chanca</GenericName>
    <SpecificName>Chanka awqa</SpecificName>
    <Icon>units/chanca_champ_1.png</Icon>
    <Requirements>
      <Techs datatype="tokens">phase_town</Techs>
    </Requirements>
  </Identity>
  <VisualActor>
    <Actor>units/chancas/infantry_hero_pachacutec.xml</Actor>
  </VisualActor>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/chanca/champion_infantry.xml", champion)

    # Héroes incas de la campaña
    inca_heroes = {
        "hero_cusi_yupanqui.xml": ("Cusi Yupanqui", "units/inca/hero_pachacutec", "units/inca_hero_1.png"),
        "hero_viracocha_inca.xml": ("Viracocha Inca", "units/inca/hero_sapa_inca", "units/inca_hero_3.png"),
        "hero_inca_urco.xml": ("Inca Urco", "units/inca/hero_pachacutec", "units/inca_hero_2.png"),
    }
    for filename, (name, parent, icon) in inca_heroes.items():
        text = f"""<?xml version="1.0" encoding="utf-8"?>
<Entity parent="{parent}">
  <Identity>
    <GenericName>{name}</GenericName>
    <SpecificName>{name}</SpecificName>
    <Icon>{icon}</Icon>
  </Identity>
</Entity>
"""
        write_text(MOD / "simulation/templates/units/inca" / filename, text)

    chanan = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="units/inca/support_healer_b">
  <Auras datatype="tokens">units/heroes/inca_hero_chanan_curi_coca</Auras>
  <Promotion disable=""/>
  <Identity>
    <GenericName>Chanan Curi Coca</GenericName>
    <SpecificName>Chanan Quri Quka</SpecificName>
    <Icon>units/inca_support_healer.png</Icon>
  </Identity>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/inca/hero_chanan_curi_coca.xml", chanan)


def make_auras() -> None:
    auras = {
        "simulation/data/auras/teambonuses/chanca_player_teambonus.json": {
            "type": "global",
            "affects": ["Citizen Infantry"],
            "modifications": [
                {"value": "Cost/Resources/food", "multiply": 0.90},
                {"value": "Cost/BuildTime", "multiply": 0.95}
            ],
            "auraName": "Confederación chanca",
            "auraDescription": "Infantería ciudadana -10% comida y -5% tiempo de entrenamiento."
        },
        "simulation/data/auras/units/heroes/chanca_hero_astoy_huaraca.json": {
            "type": "range",
            "radius": 22,
            "affects": ["Soldier"],
            "modifications": [
                {"value": "Attack/Melee/Damage/Hack", "multiply": 1.18},
                {"value": "Attack/Melee/Damage/Pierce", "multiply": 1.18},
                {"value": "Attack/Melee/Damage/Crush", "multiply": 1.18}
            ],
            "auraName": "Furia chanca",
            "auraDescription": "Soldados cercanos +18% daño cuerpo a cuerpo.",
            "overlayIcon": "art/textures/ui/session/auras/attack_bonus.png"
        },
        "simulation/data/auras/units/heroes/chanca_hero_tomay_huaraca.json": {
            "type": "range",
            "radius": 22,
            "affects": ["Soldier"],
            "modifications": [
                {"value": "UnitMotion/WalkSpeed", "multiply": 1.15},
                {"value": "Vision/Range", "multiply": 1.10}
            ],
            "auraName": "Marcha de la puna",
            "auraDescription": "Soldados cercanos +15% velocidad y +10% visión.",
            "overlayIcon": "art/textures/ui/session/auras/speed_bonus.png"
        },
        "simulation/data/auras/units/heroes/chanca_hero_ancu_huallo.json": {
            "type": "range",
            "radius": 22,
            "affects": ["Soldier"],
            "modifications": [
                {"value": "Attack/Capture/Capture", "add": 1},
                {"value": "Resistance/Entity/Damage/Hack", "add": 1},
                {"value": "Resistance/Entity/Damage/Pierce", "add": 1}
            ],
            "auraName": "Señor de la confederación",
            "auraDescription": "Soldados cercanos +1 captura y +1 resistencia.",
            "overlayIcon": "art/textures/ui/session/auras/attack_bonus.png"
        },
        "simulation/data/auras/units/heroes/chanca_relic_uscovilca.json": {
            "type": "global",
            "affects": ["Soldier"],
            "modifications": [
                {"value": "Health/Max", "multiply": 1.10},
                {"value": "Attack/Capture/Capture", "multiply": 1.10}
            ],
            "auraName": "Presencia de Uscovilca",
            "auraDescription": "Soldados +10% salud y +10% captura mientras la reliquia esté en manos chancas."
        },
        "simulation/data/auras/units/heroes/inca_hero_chanan_curi_coca.json": {
            "type": "range",
            "radius": 20,
            "affects": ["Soldier", "Structure"],
            "modifications": [
                {"value": "Health/RegenRate", "add": 0.5},
                {"value": "Resistance/Entity/Damage/Hack", "add": 1},
                {"value": "Resistance/Entity/Damage/Pierce", "add": 1}
            ],
            "auraName": "Defensa de Cusco",
            "auraDescription": "Soldados y estructuras cercanas +0.5 regeneración y +1 resistencia.",
            "overlayIcon": "art/textures/ui/session/auras/heal.png"
        },
    }
    for path, data in auras.items():
        write_text(MOD / path, json.dumps(data, ensure_ascii=False, indent="\t") + "\n")


def make_technologies() -> None:
    techs = {
        "confederation": {
            "genericName": "Confederación chanca",
            "description": "Las jefaturas chancas coordinaban sus fuerzas mediante alianzas y botín compartido.",
            "cost": {"food": 300, "wood": 200},
            "requirements": {"all": [{"tech": "phase_town"}, {"civ": "chanca"}]},
            "requirementsTooltip": "Desbloqueado en Fase Pueblo.",
            "icon": "parade_of_daphne.png",
            "researchTime": 40,
            "tooltip": "Infantería ciudadana -10% coste de comida y madera.",
            "modifications": [
                {"value": "Cost/Resources/food", "multiply": 0.90},
                {"value": "Cost/Resources/wood", "multiply": 0.90}
            ],
            "affects": ["Citizen Infantry"],
            "soundComplete": "interface/alarm/alarm_upgradearmory.xml"
        },
        "macana": {
            "genericName": "Macana chanca",
            "description": "El garrote de madera dura, a veces con cabeza de piedra o bronce, era un arma central en la guerra andina.",
            "cost": {"metal": 200},
            "requirements": {"all": [{"tech": "phase_town"}, {"civ": "chanca"}]},
            "requirementsTooltip": "Desbloqueado en Fase Pueblo.",
            "icon": "clenched_fist.png",
            "researchTime": 40,
            "tooltip": "Macemen y axemen +15% daño cuerpo a cuerpo.",
            "modifications": [
                {"value": "Attack/Melee/Damage/Hack", "multiply": 1.15},
                {"value": "Attack/Melee/Damage/Pierce", "multiply": 1.15},
                {"value": "Attack/Melee/Damage/Crush", "multiply": 1.15}
            ],
            "affects": ["Maceman", "Axeman"],
            "soundComplete": "interface/alarm/alarm_upgradearmory.xml"
        },
        "huaraca": {
            "genericName": "Huaraca",
            "description": "La honda andina podía lanzar piedras con gran fuerza y era temida por su alcance.",
            "cost": {"wood": 200, "metal": 100},
            "requirements": {"all": [{"tech": "phase_town"}, {"civ": "chanca"}]},
            "requirementsTooltip": "Desbloqueado en Fase Pueblo.",
            "icon": "bow.png",
            "researchTime": 40,
            "tooltip": "Honderos +15% alcance.",
            "modifications": [
                {"value": "Attack/Ranged/MaxRange", "multiply": 1.15}
            ],
            "affects": ["Slinger"],
            "soundComplete": "interface/alarm/alarm_upgradearmory.xml"
        },
    }
    for name, data in techs.items():
        write_text(MOD / "simulation/data/technologies/chanca" / f"{name}.json",
                   json.dumps(data, ensure_ascii=False, indent="\t") + "\n")


def make_civ() -> None:
    civ = {
        "Code": "chanca",
        "Culture": "inca",
        "Region": ["andes"],
        "Music": [
            {"File": "Harvest_Festival.ogg", "Type": "peace"},
            {"File": "Forging_a_City-State.ogg", "Type": "peace"},
            {"File": "Highland_Mist.ogg", "Type": "peace"},
            {"File": "The_Hellespont.ogg", "Type": "peace"}
        ],
        "CivBonuses": [
            {
                "Name": "Confederación chanca",
                "History": "Las crónicas describen a los chancas como una confederación laxa de jefaturas de Andahuaylas, Apurímac y Huancavelica.",
                "Description": "Infantería ciudadana más barata y rápida de entrenar."
            }
        ],
        "WallSets": ["structures/wallset_palisade", "structures/chanca/wallset_stone"],
        "StartEntities": [
            {"Template": "structures/chanca/civil_centre"},
            {"Template": "units/chanca/support_civilian", "Count": 4},
            {"Template": "units/chanca/infantry_maceman_b", "Count": 2},
            {"Template": "units/chanca/infantry_slinger_b", "Count": 2},
            {"Template": "units/chanca/infantry_spearman_b", "Count": 2},
            {"Template": "units/chanca/infantry_chaski", "Count": 1}
        ],
        "AINames": [
            "Uscovilca", "Astoy Huaraca", "Tomay Huaraca", "Anccu Huallo",
            "Hancohuallu", "Malma", "Iquicha", "Vilca", "Parkos", "Uran Chanka",
            "Hanan Chanka", "Hurin Chanka"
        ],
        "SkirmishReplacements": {
            "skirmish/units/default_infantry_ranged_b": "units/chanca/infantry_slinger_b",
            "skirmish/units/default_infantry_melee_b": "units/chanca/infantry_maceman_b",
            "skirmish/units/special_starting_unit": "units/chanca/infantry_chaski",
            "skirmish/structures/default_house_10": "structures/chanca/house",
            "skirmish/units/default_cavalry": "units/chanca/infantry_chaski",
            "skirmish/units/default_ship_trireme": "",
            "skirmish/units/default_ship_merchant": "",
            "skirmish/units/default_ship_fishing": "",
            "skirmish/units/default_support_healer": "units/chanca/support_healer_b",
            "skirmish/units/default_support_trader": "units/chanca/support_trader",
            "skirmish/structures/default_defense_tower": "structures/chanca/defense_tower"
        },
        "SelectableInGameSetup": True
    }
    write_text(MOD / "simulation/data/civs/chanca.json",
               json.dumps(civ, ensure_ascii=False, indent="\t") + "\n")

    player = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_player">
  <Auras datatype="tokens">teambonuses/chanca_player_teambonus</Auras>
  <Identity>
    <Civ>chanca</Civ>
    <GenericName>Chancas (Confederación)</GenericName>
    <History>La confederación chanca agrupó jefaturas de los actuales departamentos de Apurímac, Ayacucho y Huancavelica. En 1438 atacó el Curacazgo del Cusco y fue derrotada por Cusi Yupanqui, el futuro Pachacútec.</History>
    <Icon>emblems/emblem_chanca.png</Icon>
  </Identity>
  <Player>
    <Formations datatype="tokens">special/formations/line_closed</Formations>
  </Player>
</Entity>
"""
    write_text(MOD / "simulation/templates/special/players/chanca.xml", player)


def add_lang_quechua(text: str) -> str:
    if "<Lang>" in text:
        return text
    if "<Identity>" in text:
        return text.replace("<Identity>", "<Identity>\n    <Lang>quechua</Lang>", 1)
    return text


def apply_lang_quechua() -> None:
    # Chancas: todas las plantillas de unidades.
    for f in (MOD / "simulation/templates/units/chanca").glob("*.xml"):
        write_text(f, add_lang_quechua(read_text(f)))
    # Incas: copiar/actualizar todas las plantillas de unidades, preservando
    # las correcciones y héroes propios de este mod.
    src_dir = INCA / "simulation/templates/units/inca"
    dst_dir = MOD / "simulation/templates/units/inca"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in src_dir.glob("*.xml"):
        dst = dst_dir / src.name
        if dst.exists():
            text = read_text(dst)
        else:
            text = read_text(src)
        write_text(dst, add_lang_quechua(text))
    for dst in dst_dir.glob("*.xml"):
        write_text(dst, add_lang_quechua(read_text(dst)))


def apply_compat_fixes() -> None:
    """Corrige plantillas del mod Inca incompatibles con esquemas estrictos (p. ej. Delenda Est)."""
    fixed_inca_chaski = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_unit_infantry_ranged_slinger_chaski">
  <Attack>
    <Ranged>
      <AttackName>Sling</AttackName>
      <Damage>
        <Pierce>4.0</Pierce>
        <Crush>0.5</Crush>
      </Damage>
      <MaxRange>38</MaxRange>
      <PrepareTime>500</PrepareTime>
      <RepeatTime>1200</RepeatTime>
      <Projectile>
        <Speed>70</Speed>
        <Spread>3</Spread>
        <Gravity>30</Gravity>
        <FriendlyFire>false</FriendlyFire>
        <LaunchPoint y="3"/>
      </Projectile>
      <PreferredClasses datatype="tokens">Human</PreferredClasses>
    </Ranged>
  </Attack>
  <Identity>
    <Civ>inca</Civ>
    <SelectionGroupName>units/inca/chaski</SelectionGroupName>
    <GenericName>Quíchua Runner</GenericName>
    <SpecificName>Chaski</SpecificName>
    <Icon>units/inca_chaski.png</Icon>
  </Identity>
  <VisualActor>
    <Actor>units/incas/infantry_chaski.xml</Actor>
  </VisualActor>
</Entity>
"""
    fixed_inca_tower = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_structure_defensive_tower_stone">
  <Footprint replace="">
    <Circle radius="6.0"/>
    <Height>10.0</Height>
  </Footprint>
  <Capturable>
    <CapturePoints>1000</CapturePoints>
    <GarrisonRegenRate>0</GarrisonRegenRate>
    <RegenRate>10</RegenRate>
  </Capturable>
  <Identity>
    <Civ>inca</Civ>
    <SpecificName>Pucara jark'akuy</SpecificName>
  </Identity>
  <Obstruction>
    <Static width="7.5" depth="7.5"/>
  </Obstruction>
  <StatusBars>
    <HeightOffset>21.0</HeightOffset>
  </StatusBars>
  <VisualActor>
    <Actor>structures/incas/inca_scout_tower.xml</Actor>
  </VisualActor>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/inca/infantry_chaski.xml", fixed_inca_chaski)
    write_text(MOD / "simulation/templates/structures/inca/defense_tower.xml", fixed_inca_tower)

    # Listas de construcción chancas para unidades ciudadanas.
    for unit_name in ("infantry_maceman_b", "infantry_axeman_b", "infantry_spearman_b",
                      "infantry_slinger_b", "infantry_javelineer_b", "infantry_chaski",
                      "infantry_archer_b"):
        unit_path = MOD / "simulation/templates/units/chanca" / f"{unit_name}.xml"
        if not unit_path.exists():
            continue
        text = read_text(unit_path)
        if "<Builder>" in text:
            text = re.sub(r"<Builder>.*?</Builder>", CHANCA_BUILDER, text, count=1, flags=re.S)
        else:
            text = re.sub(r'(<Entity parent="[^"]+">)', r'\1\n' + CHANCA_BUILDER, text, count=1)
        write_text(unit_path, text)

    # Chanca: mismas correcciones.
    fixed_chanca_chaski = """<?xml version="1.0" encoding="utf-8"?>
<Entity parent="template_unit_infantry_ranged_slinger_chaski">
  <Attack>
    <Ranged>
      <AttackName>Sling</AttackName>
      <Damage>
        <Pierce>4.0</Pierce>
        <Crush>0.5</Crush>
      </Damage>
      <MaxRange>38</MaxRange>
      <PrepareTime>500</PrepareTime>
      <RepeatTime>1200</RepeatTime>
      <Projectile>
        <Speed>70</Speed>
        <Spread>3</Spread>
        <Gravity>30</Gravity>
        <FriendlyFire>false</FriendlyFire>
        <LaunchPoint y="3"/>
      </Projectile>
      <PreferredClasses datatype="tokens">Human</PreferredClasses>
    </Ranged>
  </Attack>
  <Identity>
    <Civ>chanca</Civ>
    <SelectionGroupName>units/chanca/chaski</SelectionGroupName>
    <GenericName>Corredor chanca</GenericName>
    <SpecificName>Chaski</SpecificName>
    <Icon>units/chanca_chaski.png</Icon>
  </Identity>
  <VisualActor>
    <Actor>units/chancas/infantry_chaski.xml</Actor>
  </VisualActor>
</Entity>
"""
    write_text(MOD / "simulation/templates/units/chanca/infantry_chaski.xml", fixed_chanca_chaski)
    tower = MOD / "simulation/templates/structures/chanca/defense_tower.xml"
    if tower.exists():
        text = read_text(tower)
        if "<Capturable>" not in text:
            text = text.replace('<Entity parent="template_structure_defensive_tower_stone">\n',
                                '<Entity parent="template_structure_defensive_tower_stone">\n  <Capturable>\n    <CapturePoints>1000</CapturePoints>\n    <GarrisonRegenRate>0</GarrisonRegenRate>\n    <RegenRate>10</RegenRate>\n  </Capturable>\n', 1)
        write_text(tower, text)


def main() -> None:
    if not INCA.exists():
        raise SystemExit(f"No se encontró el mod Inca en {INCA}")
    generate_textures()
    generate_portraits()
    generate_ui_assets()
    make_emblem()
    copy_templates()
    copy_actors()
    make_worker_actors()
    make_hero_actors()
    make_hero_templates()
    make_auras()
    make_technologies()
    make_civ()
    apply_compat_fixes()
    apply_lang_quechua()
    print("Civ chanca generada en", MOD)


if __name__ == "__main__":
    main()
