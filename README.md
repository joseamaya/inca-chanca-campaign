# La Guerra Inca-Chanca (c. 1438)

**Beta 0.3.0.** Campaña histórica para **0 A.D. Empires Ascendant 0.28.0** sobre el conflicto entre el Curacazgo del Cusco y la confederación chanca. Incluye una civilización chanca jugable, cuatro misiones, un epílogo y notas historiográficas.

Repositorio: https://github.com/joseamaya/inca-chanca-campaign

English summary: `README.en.md`. Cambios: `CHANGELOG.md`. Limitaciones: `KNOWN_ISSUES.md`.

## Requisitos

- 0 A.D. **0.28.0**.
- Mod **Incas 0 A.D.** (`incas0ad`), actualizado a 0.28.0.
  - Repositorio: https://github.com/0ADMods/incas-0ad
  - Descarga obligatoria: https://github.com/0ADMods/incas-0ad/releases/tag/v0.28.0
  - En mod.io, la versión publicada de Incas puede ser anterior a 0.28.0. Para esta beta, instalá el `.pyromod` del release de GitHub.

Este mod declara la dependencia:

```json
"dependencies": ["0ad=0.28.0", "incas0ad=0.28.0"]
```

## Estado beta

Esta es una beta pública. El bando inca tiene deshabilitadas las unidades imperiales tardías, los barcos, la maravilla, la colonia militar y los héroes de otras épocas para ajustarse a 1438. Las voces son sintéticas y el arte chanca es un reskin documentado.

## Instalación

1. Copiá esta carpeta a la carpeta de mods de 0 A.D.:
   - Linux: `~/.local/share/0ad/mods/inca-chanca`
   - Windows: `%USERPROFILE%\Documents\My Games\0ad\mods\inca-chanca`
   - macOS: `~/Library/Application Support/0ad/mods/inca-chanca`
2. Instalá `incas-0ad-0.28.0.pyromod` desde el release de GitHub en la misma carpeta de mods.
3. En el juego, abrí **Opciones → Mod Selection** y activá:
   - `Incas 0 A.D.` (`incas0ad`)
   - `La Guerra Inca-Chanca (c. 1438)` (`inca-chanca`)
4. Reiniciá el juego y entrá a **Campañas**.

Orden recomendado si editás `user.cfg`:

```ini
mod.enabledmods = "mod public 0ad_delenda_est_r28 earth-maps xiiiad incas0ad inca-chanca"
```

`inca-chanca` debe cargarse después de `incas0ad` porque corrige dos plantillas del mod Inca incompatibles con esquemas estrictos (por ejemplo, Delenda Est).

## Campaña

1. **La amenaza chanca** — Cusco, c. 1438. Viracocha Inca e Inca Urco huyen; Cusi Yupanqui organiza la defensa.
2. **El asedio de Cusco** — Defensa urbana, oleadas chancas y protección del centro cívico y el santuario.
3. **Yahuar Pampa** — Batalla campal en Ichupampa; capitanes chancas, momia de Uscovilca y la leyenda de los pururaucas.
4. **La campaña chanca** — Contraofensiva hacia Andahuaylas/Apurímac y toma de una fortaleza de altura.
5. **Epílogo: Pachacútec** — Cusi Yupanqui asume el nombre de Pachacútec.

### Objetivos y reglas

- Si **Cusi Yupanqui** muere, la misión se pierde.
- En las misiones de defensa, también se pierde si cae el centro cívico (y en el asedio, el santuario).
- En **Yahuar Pampa**, capturar la **momia de Uscovilca** y eliminar o capturar a los capitanes chancas decide la batalla.
- En **La campaña chanca**, hay que tomar el centro cívico chanca y derrotar o capturar a Anccu Huallo.
- Los **pururaucas** se presentan como un evento narrativo marcado explícitamente como leyenda. No se afirma que las piedras se transformaran literalmente en guerreros.

## Civilización chanca

- Código: `chanca`.
- Infantería: macana, hacha, lanza, honda, jabalina, arco, corredor.
- Sin caballería, sin barcos, sin arietes.
- Héroes: Astoy Huaraca, Tomay Huaraca, Anccu Huallo.
- Reliquia: momia de Uscovilca.
- Bonus: infantería ciudadana más barata y rápida de entrenar.
- Tecnologías propias: Confederación chanca, Macana chanca, Huaraca.

El arte chanca es una **derivación y reskin** del arte del mod Inca (CC-BY-SA 3.0). No pretende ser una reconstrucción arqueológica exacta de la cultura material chanca.

### Ropa de trabajadores

Los trabajadores masculinos incas y chancas usan ahora una túnica corta (`m_tunic_short.dae`) con las telas andinas existentes, en lugar de la malla de torso desnudo. Las trabajadoras conservan el vestido (`f_dress.dae`) y llevan una **lliclla/manto** con motivos escalonados. Es una aproximación con los recursos disponibles, no una reconstrucción textil completa.

### Voces quechuas

El mod incluye un paquete de voces **sintéticas** en quechua generado con eSpeak NG (`audio/voice/quechua/civ/`). Se usa para seleccionar, mover, atacar, recolectar, reparar, construir y entrar a edificios. La pronunciación es aproximada y robótica; no sustituye a grabaciones de hablantes nativos. Las voces masculinas usan la variante base `qu` y las femeninas la variante `qu+f3`, con timbres claramente distintos. Las unidades incas y chancas declaran `<Lang>quechua</Lang>` para usar este paquete.

## Rigor histórico

La guerra inca-chanca es un episodio **mítico-histórico** conocido por crónicas coloniales y tradición oral. Las fuentes no coinciden en la fecha exacta (1438 según Rowe; 1424–1425 según Del Busto; comienzos del siglo XV según Rostworowski), en el papel de Viracocha Inca, en la muerte o momia de Uscovilca, ni en las cifras de combatientes (las crónicas hablan de decenas o cientos de miles, cifras consideradas exageradas por la investigación moderna).

La campaña sigue estas líneas generales:

- Cusco era un curacazgo, no todavía el Tawantinsuyu imperial.
- La victoria se atribuye a Cusi Yupanqui, luego Pachacútec.
- Los chancas eran una confederación laxa de jefaturas de Andahuaylas, Apurímac y Huancavelica.
- La guerra abrió el camino a la expansión inca.
- No se usan caballos, hierro/acero, ruedas, pólvora ni armas europeas.
- Se evitan las unidades imperiales tardías en las misiones.

Fuentes principales:

- Juan de Betanzos, *Suma y narración de los Incas*.
- Pedro Sarmiento de Gamboa, *Historia de los Incas*.
- Pedro Cieza de León, *El señorío de los Incas*.
- Inca Garcilaso de la Vega, *Comentarios reales*.
- María Rostworowski, *Pachacútec Inca Yupanqui*.
- Brian S. Bauer, Lucas C. Kellett y Miriam Aráoz Silva, *The Chanka: Archaeological Research in Andahuaylas (Apurímac), Peru*.
- Terence N. D'Altroy, *The Incas*.
- Clementina Battcock, trabajos sobre la guerra inca-chanca.

## Estructura técnica

```text
mod.json
thumbnail.png
README.en.md
CHANGELOG.md
KNOWN_ISSUES.md
PUBLISHING.md
campaigns/inca_chanca.json
maps/scenarios/inca_chanca_*.pmp / *.xml / *_triggers.js
simulation/data/civs/chanca.json
simulation/templates/units/chanca/...
simulation/templates/structures/chanca/...
simulation/templates/special/players/chanca.xml
simulation/data/auras/...
simulation/data/technologies/chanca/...
art/actors/units/chancas/...
art/actors/structures/chancas/...
art/textures/...
tools/generate_chanca.py
tools/generate_campaign.py
tools/generate_quechua_audio.py
```

Los mapas `.pmp` se generan por script, sin depender del editor Atlas. Para regenerar:

```bash
python3 tools/generate_chanca.py
python3 tools/generate_campaign.py
python3 tools/generate_quechua_audio.py   # requiere espeak-ng con voz 'qu' y ffmpeg
python3 tools/validate_mod.py             # valida XML/JSON/JS y referencias
python3 tools/package_mod.py              # genera dist/inca-chanca-<version>.zip
```

Los scripts de generación aceptan `PYROGENESIS_PUBLIC_ZIP`, `ESPEAK_NG` y `FFMPEG` para evitar rutas locales.

## Limitaciones conocidas

- El arte chanca es un reskin del arte inca; las estructuras chancas comparten mallas incas con texturas distintas.
- No hay modelo de llama/alpaca en el mod base; por eso no se usan rebaños de camélidos en los mapas.
- Las voces quechuas son sintéticas (eSpeak NG) y pueden sonar robóticas; se pueden reemplazar por grabaciones reales.
- La fauna y la vegetación son aproximaciones con los recursos disponibles en 0 A.D.
- La fecha y muchos detalles del conflicto son discutidos por la historiografía.
- El guardado/carga usa marcadores invisibles y `OnDeserialized`; se probó con quicksave/quickload en la misión 1, pero conviene repetirlo en una partida completa.
- Los textos in-game están en español; la ficha de mod.io puede ser bilingüe.
- El relieve de los mapas es procedural, no un DEM real del Cusco.

## Créditos y licencias

Ver `CREDITS.md`. El código de este mod se distribuye bajo GPL-2.0; el arte derivado del mod Inca se distribuye bajo CC-BY-SA 3.0, con atribución a sus autores originales.
